"""Minimal source intake adapter for Phase 4."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.core.persistence import SemanticCartridge
from src.core.representation import (
    ProvenanceRecord,
    SemanticObject,
    SemanticSurfaceSet,
    SourceSpan,
    TransformStatus,
)


@dataclass(frozen=True)
class SourceDocument:
    """Text source loaded from a local path."""

    source_ref: str
    content: str


@dataclass(frozen=True)
class SourceBlock:
    """One simple intake block with line-span provenance."""

    text: str
    line_start: int
    line_end: int
    block_index: int
    heading_trail: tuple[str, ...] = ()


class SourceReadError(RuntimeError):
    """Raised when a source cannot be read for intake."""


def read_text_source(path: Path | str, encoding: str = "utf-8") -> SourceDocument:
    """Read a UTF-8 text source from a project-owned or caller-approved path."""
    source_path = Path(path)
    try:
        content = source_path.read_text(encoding=encoding)
    except OSError as exc:
        raise SourceReadError(f"Could not read source: {source_path}") from exc
    return SourceDocument(source_ref=source_path.as_posix(), content=content)


def split_text_blocks(content: str) -> list[SourceBlock]:
    """Split text into blank-line-delimited blocks with line spans."""
    lines = content.splitlines()
    blocks: list[SourceBlock] = []
    current: list[str] = []
    start_line = 1
    block_index = 0
    heading_trail: list[str] = []

    def flush(end_line: int) -> None:
        nonlocal block_index, current, start_line
        text = "\n".join(current).strip()
        if not text:
            current = []
            start_line = end_line + 1
            return
        block_heading = tuple(heading_trail)
        blocks.append(
            SourceBlock(
                text=text,
                line_start=start_line,
                line_end=end_line,
                block_index=block_index,
                heading_trail=block_heading,
            )
        )
        block_index += 1
        current = []
        start_line = end_line + 1

    for index, line in enumerate(lines, start=1):
        if line.strip() == "":
            flush(index - 1)
            continue
        if not current:
            start_line = index
        current.append(line)
        heading = markdown_heading_text(line)
        if heading:
            heading_trail = [heading]

    if current:
        flush(len(lines))

    return blocks


def semantic_objects_from_source(document: SourceDocument) -> list[SemanticObject]:
    """Transform one source document into canonical semantic objects."""
    blocks = split_text_blocks(document.content)
    if not blocks and document.content.strip():
        blocks = [
            SourceBlock(
                text=document.content.strip(),
                line_start=1,
                line_end=max(1, len(document.content.splitlines())),
                block_index=0,
            )
        ]

    return [
        semantic_object_from_block(document.source_ref, block, len(blocks))
        for block in blocks
    ]


def semantic_object_from_block(
    source_ref: str,
    block: SourceBlock,
    block_count: int,
) -> SemanticObject:
    """Create a SemanticObject for a source block."""
    kind = "heading" if markdown_heading_text(block.text.splitlines()[0]) else "text_block"
    token_count = len(block.text.split())
    surfaces = SemanticSurfaceSet(
        verbatim={"content": block.text},
        structural={
            "block_index": block.block_index,
            "block_count": block_count,
            "heading_trail": list(block.heading_trail),
        },
        grammatical={
            "node_kind": kind,
            "format": "markdown" if block.heading_trail else "plain_text",
        },
        statistical={
            "line_count": block.line_end - block.line_start + 1,
            "token_count": token_count,
            "char_count": len(block.text),
        },
        semantic={},
    )
    provenance = ProvenanceRecord(
        source_ref=source_ref,
        transform_status=TransformStatus.IDENTITY_PRESERVING,
        method="phase4_text_intake",
        confidence=1.0,
    )
    return SemanticObject.create(
        kind=kind,
        content=block.text,
        surfaces=surfaces,
        provenance=(provenance,),
        source_ref=source_ref,
        source_span=SourceSpan(start=block.line_start, end=block.line_end, unit="line"),
        local_context={
            "block_index": block.block_index,
            "heading_trail": list(block.heading_trail),
        },
    )


def ingest_source_to_cartridge(
    source_path: Path | str,
    cartridge: SemanticCartridge,
) -> list[SemanticObject]:
    """Read a source path, emit semantic objects, and persist them."""
    document = read_text_source(source_path)
    objects = semantic_objects_from_source(document)
    for obj in objects:
        cartridge.upsert_object(obj)
    return objects


def ingest_documents_to_cartridge(
    documents: Iterable[SourceDocument],
    cartridge: SemanticCartridge,
) -> list[SemanticObject]:
    """Persist semantic objects from already-loaded source documents."""
    objects: list[SemanticObject] = []
    for document in documents:
        for obj in semantic_objects_from_source(document):
            cartridge.upsert_object(obj)
            objects.append(obj)
    return objects


def markdown_heading_text(line: str) -> str:
    """Return Markdown heading text for simple ATX headings."""
    stripped = line.strip()
    if not stripped.startswith("#"):
        return ""
    marker, _, title = stripped.partition(" ")
    if not marker or any(char != "#" for char in marker) or not title.strip():
        return ""
    return title.strip()
