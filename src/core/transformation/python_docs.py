"""Extraction adapter for the official Python documentation text corpus."""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .python_ast import PythonAstSummary, summarize_python_ast

PYTHON_DOCS_EXTRACTION_VERSION = "v1"

SIGNATURE_RE = re.compile(
    r"^(?:(?:class|def|async def|awaitable)\s+)?"
    r"[A-Za-z_][\w.]*\s*\([^()]*\)(?:\s*->\s*[^:]+)?$"
)
HEADING_UNDERLINE_CHARS = {"*", "=", "-", "~", "^"}
GRAMMAR_MARKER = "::="


@dataclass(frozen=True)
class PythonDocsRecord:
    """One extracted unit from the Python documentation text corpus."""

    kind: str
    source_ref: str
    source_relpath: str
    line_start: int
    line_end: int
    content: str
    heading_trail: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    ast_summary: PythonAstSummary | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "source_ref": self.source_ref,
            "source_relpath": self.source_relpath,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "content": self.content,
            "heading_trail": list(self.heading_trail),
            "metadata": self.metadata,
            "ast_summary": self.ast_summary.to_dict() if self.ast_summary else None,
        }


def iter_python_docs_records(
    docs_root: Path | str,
    *,
    limit: int | None = None,
    include_prose: bool = True,
) -> Iterable[PythonDocsRecord]:
    """Yield typed documentation records from a Python docs text directory."""
    root = Path(docs_root).resolve()
    emitted = 0
    for path in sorted(root.rglob("*.txt")):
        for record in extract_python_docs_file(path, root, include_prose=include_prose):
            yield record
            emitted += 1
            if limit is not None and emitted >= limit:
                return


def extract_python_docs_file(
    path: Path | str,
    docs_root: Path | str,
    *,
    include_prose: bool = True,
) -> list[PythonDocsRecord]:
    """Extract typed records from one text-exported Python documentation file."""
    source_path = Path(path).resolve()
    root = Path(docs_root).resolve()
    source_relpath = source_path.relative_to(root).as_posix()
    source_ref = source_path.as_posix()
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    records: list[PythonDocsRecord] = []
    heading_stack: list[tuple[int, str]] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        line_no = index + 1

        heading_level = _heading_level(lines, index)
        if heading_level is not None:
            title = line.strip()
            heading_stack = [(level, text) for level, text in heading_stack if level < heading_level]
            heading_stack.append((heading_level, title))
            records.append(
                _record(
                    "python_doc_section",
                    source_ref,
                    source_relpath,
                    line_no,
                    line_no + 1,
                    title,
                    tuple(text for _, text in heading_stack),
                    {"heading_level": heading_level},
                )
            )
            index += 2
            continue

        if _is_doctest_start(line):
            record, index = _extract_doctest(lines, index, source_ref, source_relpath, heading_stack)
            records.append(record)
            continue

        if _is_indented_content(line):
            block_lines, start, end, index = _extract_indented_block(lines, index)
            records.extend(_records_from_indented_block(block_lines, start, end, source_ref, source_relpath, heading_stack))
            continue

        stripped = line.strip()
        if _is_signature_line(stripped):
            records.append(
                _record(
                    "python_api_signature",
                    source_ref,
                    source_relpath,
                    line_no,
                    line_no,
                    stripped,
                    tuple(text for _, text in heading_stack),
                    {"symbol": _signature_symbol(stripped)},
                )
            )
            index += 1
            continue

        if include_prose and stripped and not _is_table_line(stripped):
            paragraph, start, end, index = _extract_paragraph(lines, index)
            content = " ".join(part.strip() for part in paragraph if part.strip())
            if content:
                records.append(
                    _record(
                        "python_prose_description",
                        source_ref,
                        source_relpath,
                        start,
                        end,
                        content,
                        tuple(text for _, text in heading_stack),
                        {},
                    )
                )
            continue

        index += 1

    return records


def _records_from_indented_block(
    block_lines: list[str],
    start: int,
    end: int,
    source_ref: str,
    source_relpath: str,
    heading_stack: list[tuple[int, str]],
) -> list[PythonDocsRecord]:
    content = textwrap.dedent("\n".join(block_lines)).strip("\n")
    heading_trail = tuple(text for _, text in heading_stack)
    if not content or _is_table_line(content):
        return []

    grammar_lines = [line.strip() for line in content.splitlines() if GRAMMAR_MARKER in line]
    if grammar_lines:
        return [
            _record(
                "python_grammar_rule",
                source_ref,
                source_relpath,
                start,
                end,
                "\n".join(grammar_lines),
                heading_trail,
                {"rule_count": len(grammar_lines)},
            )
        ]

    ast_summary = summarize_python_ast(content)
    if ast_summary.is_parseable and _looks_like_python_code(content, ast_summary):
        return [
            _record(
                "python_code_example",
                source_ref,
                source_relpath,
                start,
                end,
                content,
                heading_trail,
                {"code_form": "indented_block"},
                ast_summary,
            )
        ]
    return []


def _extract_doctest(
    lines: list[str],
    index: int,
    source_ref: str,
    source_relpath: str,
    heading_stack: list[tuple[int, str]],
) -> tuple[PythonDocsRecord, int]:
    start = index + 1
    source_lines: list[str] = []
    while index < len(lines):
        line = lines[index]
        if line.startswith("   >>>"):
            source_lines.append(line[7:] if line.startswith("   >>> ") else line[6:])
            index += 1
            continue
        if line.startswith("   ..."):
            source_lines.append(line[7:] if line.startswith("   ... ") else line[6:])
            index += 1
            continue
        break
    content = "\n".join(source_lines).strip("\n")
    ast_summary = summarize_python_ast(content)
    return (
        _record(
            "python_doctest_example",
            source_ref,
            source_relpath,
            start,
            index,
            content,
            tuple(text for _, text in heading_stack),
            {"code_form": "doctest_prompt"},
            ast_summary,
        ),
        index,
    )


def _record(
    kind: str,
    source_ref: str,
    source_relpath: str,
    line_start: int,
    line_end: int,
    content: str,
    heading_trail: tuple[str, ...],
    metadata: dict[str, Any],
    ast_summary: PythonAstSummary | None = None,
) -> PythonDocsRecord:
    return PythonDocsRecord(
        kind=kind,
        source_ref=source_ref,
        source_relpath=source_relpath,
        line_start=line_start,
        line_end=line_end,
        content=content,
        heading_trail=heading_trail,
        metadata={"extraction_version": PYTHON_DOCS_EXTRACTION_VERSION, **metadata},
        ast_summary=ast_summary,
    )


def _heading_level(lines: list[str], index: int) -> int | None:
    if index + 1 >= len(lines):
        return None
    title = lines[index].strip()
    underline = lines[index + 1].strip()
    if not title or len(underline) < max(3, min(len(title), 8)):
        return None
    if len(set(underline)) != 1:
        return None
    marker = underline[0]
    if marker not in HEADING_UNDERLINE_CHARS:
        return None
    return {"*": 1, "=": 2, "-": 3, "~": 4, "^": 5}[marker]


def _extract_indented_block(lines: list[str], index: int) -> tuple[list[str], int, int, int]:
    start = index + 1
    block: list[str] = []
    while index < len(lines) and _is_indented_content(lines[index]):
        block.append(lines[index][3:] if lines[index].startswith("   ") else lines[index])
        index += 1
    return block, start, index, index


def _extract_paragraph(lines: list[str], index: int) -> tuple[list[str], int, int, int]:
    start = index + 1
    paragraph: list[str] = []
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or _heading_level(lines, index) is not None:
            break
        if _is_doctest_start(line) or _is_indented_content(line) or _is_signature_line(stripped) or _is_table_line(stripped):
            break
        paragraph.append(line)
        index += 1
    return paragraph, start, index, index


def _is_doctest_start(line: str) -> bool:
    return line.startswith("   >>>")


def _is_indented_content(line: str) -> bool:
    return line.startswith("   ") and not line.startswith("   >>>") and not line.startswith("   ...") and line.strip() != ""


def _is_signature_line(stripped: str) -> bool:
    if len(stripped) > 180 or stripped.endswith("."):
        return False
    symbol_side = stripped.split("(", 1)[0]
    for prefix in ("async def ", "def ", "class ", "awaitable "):
        if symbol_side.startswith(prefix):
            symbol_side = symbol_side[len(prefix) :]
            break
    if " " in symbol_side:
        return False
    return bool(SIGNATURE_RE.match(stripped))


def _signature_symbol(signature: str) -> str:
    cleaned = signature
    for prefix in ("async def ", "def ", "class ", "awaitable "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    return cleaned.split("(", 1)[0].strip()


def _is_table_line(stripped: str) -> bool:
    return stripped.startswith("|") or stripped.startswith("+---") or stripped.startswith("====")


def _looks_like_python_code(content: str, summary: PythonAstSummary) -> bool:
    if summary.defined_names or summary.call_names or summary.imported_modules or summary.control_flow:
        return True
    return any(token in content for token in ("=", "[", "{", "(", ")", "lambda", "yield", "return"))
