"""Export the append-only app journal as a readable DEV-LOG mirror."""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RENDERED_METADATA_KEYS = {
    "files_changed",
    "verification",
    "next_focus",
    "key_decisions",
    "lessons_learned",
    "evidence_used",
    "rejected_alternatives",
}


@dataclass(frozen=True)
class JournalEntry:
    """Simple in-memory representation of a journal row."""

    id: int
    created_at: str
    kind: str
    status: str
    title: str
    body: str
    tags_json: str
    related_path: str
    related_ref: str
    metadata_json: str

    @property
    def metadata(self) -> dict[str, Any]:
        if not self.metadata_json:
            return {}
        return json.loads(self.metadata_json)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_entries(db_path: Path) -> list[JournalEntry]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, created_at, kind, status, title, body, tags_json,
                   related_path, related_ref, metadata_json
            FROM journal_entries
            ORDER BY id ASC
            """
        ).fetchall()
    finally:
        conn.close()
    return [JournalEntry(**dict(row)) for row in rows]


def _append_lines(lines: list[str], heading: str, items: list[str]) -> None:
    if not items:
        return
    lines.append(f"### {heading}")
    lines.append("")
    for item in items:
        lines.append(f"- {item}")
    lines.append("")


def _format_list_items(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    rendered: list[str] = []
    for item in items:
        if isinstance(item, str):
            rendered.append(item)
        else:
            rendered.append(json.dumps(item, sort_keys=True))
    return rendered


def _format_verification(verification: Any) -> list[str]:
    if not isinstance(verification, dict):
        return []
    lines: list[str] = []
    for key, value in verification.items():
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, sort_keys=True)
        else:
            rendered = str(value)
        lines.append(f"`{key}`: {rendered}")
    return lines


def render_dev_log(
    entries: list[JournalEntry],
    *,
    exported_at: str,
    source_of_truth: str,
) -> str:
    """Render a readable markdown mirror from journal rows."""

    lines = [
        "# DEV-LOG",
        "",
        "_Generated mirror export created at user request for external assistant review._",
        "",
        f"_Source of truth: `{source_of_truth}`_",
        "",
        f"_Exported at: `{exported_at}`_",
        "",
        f"_Exported entries: {len(entries)}_",
        "",
        "This file is a generated append-only mirror of the authoritative app journal.",
        "Do not treat it as a second canonical continuity surface.",
        "",
    ]

    for entry in entries:
        lines.extend(
            [
                f"## {entry.id}. {entry.title}",
                "",
                f"- created_at: `{entry.created_at}`",
                f"- kind: `{entry.kind}`",
                f"- status: `{entry.status}`",
            ]
        )
        if entry.related_path:
            lines.append(f"- related_path: `{entry.related_path}`")
        if entry.related_ref:
            lines.append(f"- related_ref: `{entry.related_ref}`")
        if entry.tags_json:
            lines.append(f"- tags_json: `{entry.tags_json}`")
        lines.extend(["", entry.body.strip(), ""])

        metadata = entry.metadata
        _append_lines(
            lines,
            "Files Changed",
            _format_list_items(metadata.get("files_changed")),
        )
        _append_lines(
            lines,
            "Key Decisions",
            _format_list_items(metadata.get("key_decisions")),
        )
        _append_lines(
            lines,
            "Lessons Learned",
            _format_list_items(metadata.get("lessons_learned")),
        )
        _append_lines(
            lines,
            "Evidence Used",
            _format_list_items(metadata.get("evidence_used")),
        )
        _append_lines(
            lines,
            "Rejected Alternatives",
            _format_list_items(metadata.get("rejected_alternatives")),
        )
        _append_lines(
            lines,
            "Verification",
            _format_verification(metadata.get("verification")),
        )
        _append_lines(
            lines,
            "Next Focus",
            _format_list_items(metadata.get("next_focus")),
        )

        residual = {
            key: value
            for key, value in metadata.items()
            if key not in RENDERED_METADATA_KEYS
        }
        if residual:
            lines.extend(
                [
                    "### Raw Metadata",
                    "",
                    "```json",
                    json.dumps(residual, indent=2, sort_keys=True),
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def export_dev_log(output_path: Path | None = None) -> Path:
    """Export the current app journal mirror to markdown."""

    project_root = _project_root()
    db_path = project_root / "_docs" / "_journalDB" / "app_journal.sqlite3"
    output = output_path or project_root / "_docs" / "DEV-LOG.md"
    exported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    entries = _load_entries(db_path)
    output.write_text(
        render_dev_log(
            entries,
            exported_at=exported_at,
            source_of_truth="_docs/_journalDB/app_journal.sqlite3",
        ),
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for the DEV-LOG markdown mirror.",
    )
    args = parser.parse_args()
    output_path = export_dev_log(args.output)
    print(output_path)


if __name__ == "__main__":
    main()
