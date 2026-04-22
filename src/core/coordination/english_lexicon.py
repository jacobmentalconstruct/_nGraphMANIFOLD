"""Build the English lexical baseline cartridge."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Iterator

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation import SemanticObject
from src.core.transformation import iter_dictionary_alpha_entries, lexical_entry_to_semantic_object

ENGLISH_LEXICON_BASELINE_VERSION = "v1"
DEFAULT_ENGLISH_LEXICON_SOURCE_RELPATH = "assets/_corpus_examples/dictionary_alpha_arrays.json"
DEFAULT_ENGLISH_LEXICON_CARTRIDGE_NAME = "base_english_lexicon.sqlite3"


@dataclass(frozen=True)
class EnglishLexiconBuildResult:
    """Summary of an English lexical baseline cartridge build."""

    version: str
    project_root: str
    source_path: str
    cartridge_path: str
    cartridge_id: str
    limit: int | None
    reset: bool
    entries_seen: int
    objects_written: int
    object_count: int
    relation_count: int
    provenance_count: int
    sample_headwords: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "source_path": self.source_path,
            "cartridge_path": self.cartridge_path,
            "cartridge_id": self.cartridge_id,
            "limit": self.limit,
            "reset": self.reset,
            "entries_seen": self.entries_seen,
            "objects_written": self.objects_written,
            "object_count": self.object_count,
            "relation_count": self.relation_count,
            "provenance_count": self.provenance_count,
            "sample_headwords": list(self.sample_headwords),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class EnglishLexiconLookupCandidate:
    """One English lexical entry lookup candidate."""

    semantic_id: str
    headword: str
    normalized_headword: str
    definition_preview: str
    sense_count: int
    usage_example_count: int
    domain_labels: tuple[str, ...]
    part_of_speech_hints: tuple[str, ...]
    cross_references: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_id": self.semantic_id,
            "headword": self.headword,
            "normalized_headword": self.normalized_headword,
            "definition_preview": self.definition_preview,
            "sense_count": self.sense_count,
            "usage_example_count": self.usage_example_count,
            "domain_labels": list(self.domain_labels),
            "part_of_speech_hints": list(self.part_of_speech_hints),
            "cross_references": list(self.cross_references),
        }


@dataclass(frozen=True)
class EnglishLexiconLookupResult:
    """Lookup result over the dedicated English lexical cartridge."""

    version: str
    query: str
    cartridge_path: str
    candidate_count: int
    candidates: tuple[EnglishLexiconLookupCandidate, ...]
    caution: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "query": self.query,
            "cartridge_path": self.cartridge_path,
            "candidate_count": self.candidate_count,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "caution": self.caution,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_english_lexicon_source_path(project_root: Path | str) -> Path:
    """Return the project-owned dictionary alpha-array path."""
    return Path(project_root) / DEFAULT_ENGLISH_LEXICON_SOURCE_RELPATH


def default_english_lexicon_cartridge_path(project_root: Path | str) -> Path:
    """Return the project-owned English lexical cartridge path."""
    return Path(project_root) / "data" / "cartridges" / DEFAULT_ENGLISH_LEXICON_CARTRIDGE_NAME


def build_english_lexicon_baseline(
    project_root: Path | str,
    *,
    source_path: Path | str | None = None,
    cartridge_path: Path | str | None = None,
    limit: int | None = None,
    reset: bool = False,
) -> EnglishLexiconBuildResult:
    """Stream structured dictionary entries into a dedicated lexical cartridge."""
    root = Path(project_root).resolve()
    source = Path(source_path).resolve() if source_path else default_english_lexicon_source_path(root).resolve()
    db_path = Path(cartridge_path).resolve() if cartridge_path else default_english_lexicon_cartridge_path(root).resolve()
    _ensure_project_owned(root, source)
    _ensure_project_owned(root, db_path)
    if reset and db_path.exists():
        db_path.unlink()
    cartridge = SemanticCartridge(db_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    entries = iter_dictionary_alpha_entries(source)
    if limit is not None:
        entries = islice(entries, max(0, limit))

    sample_headwords: list[str] = []
    entries_seen = 0

    def objects() -> Iterator[SemanticObject]:
        nonlocal entries_seen
        for entry in entries:
            entries_seen += 1
            if len(sample_headwords) < 8:
                sample_headwords.append(entry.headword)
            yield lexical_entry_to_semantic_object(entry)

    objects_written = cartridge.upsert_objects(objects())
    manifest = cartridge.manifest()
    return EnglishLexiconBuildResult(
        version=ENGLISH_LEXICON_BASELINE_VERSION,
        project_root=str(root),
        source_path=str(source),
        cartridge_path=str(db_path),
        cartridge_id=DEFAULT_CARTRIDGE_ID,
        limit=limit,
        reset=reset,
        entries_seen=entries_seen,
        objects_written=objects_written,
        object_count=manifest.object_count,
        relation_count=manifest.relation_count,
        provenance_count=manifest.provenance_count,
        sample_headwords=tuple(sample_headwords),
    )


def lookup_english_lexicon_entry(
    project_root: Path | str,
    query: str,
    *,
    cartridge_path: Path | str | None = None,
    limit: int = 5,
) -> EnglishLexiconLookupResult:
    """Look up lexical entries by headword prefix in the English lexical cartridge."""
    root = Path(project_root).resolve()
    db_path = Path(cartridge_path).resolve() if cartridge_path else default_english_lexicon_cartridge_path(root).resolve()
    _ensure_project_owned(root, db_path)
    normalized_query = " ".join(query.strip().lower().split())
    if not normalized_query:
        raise ValueError("English lexicon lookup requires a non-empty query")
    pattern = f"{_escape_like(normalized_query)}:%"
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT object_json
            FROM semantic_objects
            WHERE kind = 'lexical_entry'
              AND LOWER(content) LIKE ? ESCAPE '\\'
            ORDER BY content
            LIMIT ?
            """,
            (pattern, max(1, limit)),
        ).fetchall()
    finally:
        conn.close()
    candidates = tuple(_lookup_candidate_from_object(SemanticObject.from_dict(json.loads(row["object_json"]))) for row in rows)
    return EnglishLexiconLookupResult(
        version=ENGLISH_LEXICON_BASELINE_VERSION,
        query=query,
        cartridge_path=str(db_path),
        candidate_count=len(candidates),
        candidates=candidates,
        caution=(
            "Alpha-array entries are reliable for headword and definition_raw. "
            "Senses, domain labels, cross references, and usage examples are conservative parser candidates."
        ),
    )


def _lookup_candidate_from_object(obj: SemanticObject) -> EnglishLexiconLookupCandidate:
    metadata = obj.metadata
    semantic = obj.surfaces.semantic
    grammatical = obj.surfaces.grammatical
    statistical = obj.surfaces.statistical
    return EnglishLexiconLookupCandidate(
        semantic_id=obj.semantic_id,
        headword=str(metadata.get("headword", "")),
        normalized_headword=str(metadata.get("normalized_headword", "")),
        definition_preview=_preview(str(obj.surfaces.verbatim.get("definition_raw", obj.content))),
        sense_count=int(statistical.get("sense_count", 0)),
        usage_example_count=int(statistical.get("usage_example_count", 0)),
        domain_labels=tuple(str(item) for item in grammatical.get("domain_labels", ())),
        part_of_speech_hints=tuple(str(item) for item in grammatical.get("part_of_speech_hints", ())),
        cross_references=tuple(str(item) for item in semantic.get("cross_references", ())),
    )


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _preview(content: str, limit: int = 280) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def _ensure_project_owned(root: Path, path: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"English lexical baseline path is outside project root: {path}") from exc
