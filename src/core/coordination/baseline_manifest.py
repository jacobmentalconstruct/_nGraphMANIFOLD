"""Protected deterministic baseline manifest helper."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .english_lexicon import (
    DEFAULT_ENGLISH_LEXICON_CARTRIDGE_NAME,
    ENGLISH_LEXICON_BASELINE_VERSION,
    default_english_lexicon_cartridge_path,
)
from .project_documents import (
    PROJECT_DOCUMENT_INGESTION_VERSION,
    default_project_document_cartridge_path,
)
from .python_docs_corpus import (
    DEFAULT_PYTHON_DOCS_CARTRIDGE_NAME,
    PYTHON_DOCS_CORPUS_VERSION,
    default_python_docs_cartridge_path,
)

BASELINE_MANIFEST_VERSION = "v1"
BASELINE_MANIFEST_NAME = "baseline_manifest.json"
PROTECTED_BASELINE_LOCK_POLICY = (
    "protected:no_in_place_deformation; regenerated versions must be explicitly versioned "
    "and manifest-recorded"
)


@dataclass(frozen=True)
class BaselineCartridgeSpec:
    """Static contract for one protected deterministic baseline cartridge."""

    name: str
    role: str
    generator_version: str
    parser_version: str
    build_command: str
    path_kind: str


@dataclass(frozen=True)
class BaselineCartridgeManifest:
    """Read-only manifest row for one protected cartridge."""

    cartridge_name: str
    role: str
    cartridge_path: str
    status: str
    object_count: int
    occurrence_count: int
    relation_count: int
    provenance_count: int
    source_refs: tuple[str, ...]
    build_command: str
    generator_version: str
    parser_version: str
    file_hash: str
    file_hash_algorithm: str
    created_time: str
    updated_time: str
    lock_policy: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "cartridge_name": self.cartridge_name,
            "role": self.role,
            "cartridge_path": self.cartridge_path,
            "status": self.status,
            "object_count": self.object_count,
            "occurrence_count": self.occurrence_count,
            "relation_count": self.relation_count,
            "provenance_count": self.provenance_count,
            "source_refs": list(self.source_refs),
            "build_command": self.build_command,
            "generator_version": self.generator_version,
            "parser_version": self.parser_version,
            "file_hash": self.file_hash,
            "file_hash_algorithm": self.file_hash_algorithm,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "lock_policy": self.lock_policy,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class BaselineManifestRun:
    """Full protected baseline manifest artifact."""

    version: str
    project_root: str
    manifest_path: str
    created_at: str
    lock_policy: str
    cartridge_count: int
    ready_count: int
    all_ready: bool
    cartridges: tuple[BaselineCartridgeManifest, ...]
    elapsed_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "manifest_path": self.manifest_path,
            "created_at": self.created_at,
            "lock_policy": self.lock_policy,
            "cartridge_count": self.cartridge_count,
            "ready_count": self.ready_count,
            "all_ready": self.all_ready,
            "cartridges": [cartridge.to_dict() for cartridge in self.cartridges],
            "elapsed_ms": self.elapsed_ms,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_baseline_manifest_path(project_root: Path | str) -> Path:
    """Return the ignored project-local baseline manifest path."""
    return Path(project_root) / "data" / "cartridges" / BASELINE_MANIFEST_NAME


def default_baseline_cartridge_specs() -> tuple[BaselineCartridgeSpec, ...]:
    """Return the protected deterministic cartridges recorded by this manifest."""
    return (
        BaselineCartridgeSpec(
            name=DEFAULT_ENGLISH_LEXICON_CARTRIDGE_NAME,
            role="canonical_deterministic_english_lexicon",
            generator_version=ENGLISH_LEXICON_BASELINE_VERSION,
            parser_version=ENGLISH_LEXICON_BASELINE_VERSION,
            build_command="python -m src.app ingest-lexicon --reset --dump-json",
            path_kind="english_lexicon",
        ),
        BaselineCartridgeSpec(
            name=DEFAULT_PYTHON_DOCS_CARTRIDGE_NAME,
            role="canonical_deterministic_python_docs_projection",
            generator_version=PYTHON_DOCS_CORPUS_VERSION,
            parser_version=PYTHON_DOCS_CORPUS_VERSION,
            build_command="python -m src.app ingest-python-docs --reset --dump-json",
            path_kind="python_docs",
        ),
        BaselineCartridgeSpec(
            name="project_documents.sqlite3",
            role="canonical_deterministic_project_documents",
            generator_version=PROJECT_DOCUMENT_INGESTION_VERSION,
            parser_version=PROJECT_DOCUMENT_INGESTION_VERSION,
            build_command="python -m src.app mcp-ingest-docs --project-doc-profile core --dump-json",
            path_kind="project_documents",
        ),
    )


def run_baseline_manifest_helper(
    project_root: Path | str,
    *,
    manifest_path: Path | str | None = None,
    specs: tuple[BaselineCartridgeSpec, ...] | None = None,
) -> BaselineManifestRun:
    """Inspect protected baseline cartridges and return a manifest artifact."""
    started = time.perf_counter()
    root = Path(project_root).resolve()
    output_path = Path(manifest_path).resolve() if manifest_path else default_baseline_manifest_path(root).resolve()
    _ensure_project_owned(root, output_path)
    cartridges = tuple(_inspect_cartridge(root, spec) for spec in (specs or default_baseline_cartridge_specs()))
    ready_count = sum(1 for cartridge in cartridges if cartridge.status == "ready")
    return BaselineManifestRun(
        version=BASELINE_MANIFEST_VERSION,
        project_root=str(root),
        manifest_path=str(output_path),
        created_at=_utc_now(),
        lock_policy=PROTECTED_BASELINE_LOCK_POLICY,
        cartridge_count=len(cartridges),
        ready_count=ready_count,
        all_ready=ready_count == len(cartridges),
        cartridges=cartridges,
        elapsed_ms=max(1, round((time.perf_counter() - started) * 1000)),
    )


def save_baseline_manifest_run(run: BaselineManifestRun, output_path: Path | str | None = None) -> Path:
    """Write the baseline manifest artifact without touching cartridges."""
    path = Path(output_path or run.manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.to_json() + "\n", encoding="utf-8")
    return path


def _inspect_cartridge(root: Path, spec: BaselineCartridgeSpec) -> BaselineCartridgeManifest:
    path = _path_for_spec(root, spec).resolve()
    _ensure_project_owned(root, path)
    if not path.exists():
        return BaselineCartridgeManifest(
            cartridge_name=spec.name,
            role=spec.role,
            cartridge_path=str(path),
            status="missing",
            object_count=0,
            occurrence_count=0,
            relation_count=0,
            provenance_count=0,
            source_refs=(),
            build_command=spec.build_command,
            generator_version=spec.generator_version,
            parser_version=spec.parser_version,
            file_hash="",
            file_hash_algorithm="sha256",
            created_time="",
            updated_time="",
            lock_policy=PROTECTED_BASELINE_LOCK_POLICY,
            notes=("cartridge file is missing",),
        )

    file_hash = _sha256_file(path)
    try:
        counts, created_time, updated_time, source_refs = _read_cartridge_state(path)
        status = "ready" if counts["object_count"] > 0 else "empty"
        notes: tuple[str, ...] = ()
    except sqlite3.Error as exc:
        counts = {
            "object_count": 0,
            "occurrence_count": 0,
            "relation_count": 0,
            "provenance_count": 0,
        }
        created_time = ""
        updated_time = ""
        source_refs = ()
        status = "unreadable"
        notes = (f"read-only sqlite inspection failed: {exc}",)

    return BaselineCartridgeManifest(
        cartridge_name=spec.name,
        role=spec.role,
        cartridge_path=str(path),
        status=status,
        object_count=counts["object_count"],
        occurrence_count=counts["occurrence_count"],
        relation_count=counts["relation_count"],
        provenance_count=counts["provenance_count"],
        source_refs=source_refs,
        build_command=spec.build_command,
        generator_version=spec.generator_version,
        parser_version=spec.parser_version,
        file_hash=file_hash,
        file_hash_algorithm="sha256",
        created_time=created_time,
        updated_time=updated_time,
        lock_policy=PROTECTED_BASELINE_LOCK_POLICY,
        notes=notes,
    )


def _path_for_spec(root: Path, spec: BaselineCartridgeSpec) -> Path:
    if spec.path_kind == "english_lexicon":
        return default_english_lexicon_cartridge_path(root)
    if spec.path_kind == "python_docs":
        return default_python_docs_cartridge_path(root)
    if spec.path_kind == "project_documents":
        return default_project_document_cartridge_path(root)
    return root / "data" / "cartridges" / spec.name


def _read_cartridge_state(path: Path) -> tuple[dict[str, int], str, str, tuple[str, ...]]:
    conn = sqlite3.connect(_read_only_sqlite_uri(path), uri=True)
    try:
        conn.row_factory = sqlite3.Row
        manifest = conn.execute(
            """
            SELECT created_at, updated_at
            FROM cartridge_manifest
            ORDER BY cartridge_id
            LIMIT 1
            """
        ).fetchone()
        counts = {
            "object_count": _count_rows(conn, "semantic_objects"),
            "occurrence_count": _count_rows(conn, "semantic_occurrences"),
            "relation_count": _count_rows(conn, "semantic_relations"),
            "provenance_count": _count_rows(conn, "provenance_records"),
        }
        rows = conn.execute(
            """
            SELECT DISTINCT source_ref
            FROM semantic_occurrences
            ORDER BY source_ref
            """
        ).fetchall()
    finally:
        conn.close()
    return (
        counts,
        str(manifest["created_at"]) if manifest is not None else "",
        str(manifest["updated_at"]) if manifest is not None else "",
        tuple(str(row["source_ref"]) for row in rows),
    )


def _read_only_sqlite_uri(path: Path) -> str:
    normalized = str(path.resolve()).replace("\\", "/")
    return f"file:{quote(normalized, safe='/:')}?mode=ro"


def _count_rows(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_project_owned(root: Path, path: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Baseline manifest path is outside project root: {path}") from exc
