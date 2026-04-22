"""Bounded project-document ingestion for MCP-facing traversal."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.analysis import enrich_relations, persist_relation_enrichments
from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.transformation import read_text_source, semantic_objects_from_source

from .mcp_tool_registry import TRAVERSAL_TOOL_NAME, McpToolCallResult, call_registered_mcp_tool

PROJECT_DOCUMENT_INGESTION_VERSION = "v1"
DEFAULT_PROJECT_DOCUMENTS = (
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/MCP_SEAM.md",
    "_docs/STRANGLER_PLAN.md",
)


@dataclass(frozen=True)
class ProjectDocumentCorpus:
    """Project-owned semantic corpus built from the bounded doc set."""

    version: str
    project_root: str
    cartridge_path: str
    document_paths: tuple[str, ...]
    object_count: int
    relation_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "cartridge_path": self.cartridge_path,
            "document_paths": list(self.document_paths),
            "object_count": self.object_count,
            "relation_count": self.relation_count,
        }


@dataclass(frozen=True)
class ProjectDocumentIngestionResult:
    """Result of ingesting selected project docs and calling traversal."""

    version: str
    project_root: str
    cartridge_path: str
    document_paths: tuple[str, ...]
    object_count: int
    relation_count: int
    seed_semantic_id: str
    seed_source_ref: str
    tool_call: McpToolCallResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "cartridge_path": self.cartridge_path,
            "document_paths": list(self.document_paths),
            "object_count": self.object_count,
            "relation_count": self.relation_count,
            "seed_semantic_id": self.seed_semantic_id,
            "seed_source_ref": self.seed_source_ref,
            "tool_call": self.tool_call.to_dict(),
        }


def default_project_document_cartridge_path(project_root: Path | str) -> Path:
    """Return the project-owned cartridge path for selected project docs."""
    return Path(project_root) / "data" / "cartridges" / "project_documents.sqlite3"


def ingest_project_documents_for_traversal(
    project_root: Path | str,
    *,
    cartridge_path: Path | str | None = None,
    document_relpaths: tuple[str, ...] = DEFAULT_PROJECT_DOCUMENTS,
    seed_text_hint: str = "Current Park Point",
) -> ProjectDocumentIngestionResult:
    """Ingest selected docs, then call the registered traversal tool."""
    corpus = ingest_project_documents(
        project_root,
        cartridge_path=cartridge_path,
        document_relpaths=document_relpaths,
    )
    db_path = Path(corpus.cartridge_path)
    cartridge = SemanticCartridge(db_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = cartridge.all_objects()
    seed = _select_seed(objects, seed_text_hint)
    tool_call = call_registered_mcp_tool(
        TRAVERSAL_TOOL_NAME,
        {
            "db_path": str(db_path),
            "cartridge_id": DEFAULT_CARTRIDGE_ID,
            "seed_semantic_id": seed.semantic_id,
            "max_depth": 2,
            "max_steps": 64,
            "include_incoming": True,
        },
    )
    return ProjectDocumentIngestionResult(
        version=PROJECT_DOCUMENT_INGESTION_VERSION,
        project_root=corpus.project_root,
        cartridge_path=corpus.cartridge_path,
        document_paths=corpus.document_paths,
        object_count=corpus.object_count,
        relation_count=corpus.relation_count,
        seed_semantic_id=seed.semantic_id,
        seed_source_ref=seed.occurrence.source_ref if seed.occurrence else "",
        tool_call=tool_call,
    )


def ingest_project_documents(
    project_root: Path | str,
    *,
    cartridge_path: Path | str | None = None,
    document_relpaths: tuple[str, ...] = DEFAULT_PROJECT_DOCUMENTS,
) -> ProjectDocumentCorpus:
    """Ingest selected docs into the project-owned semantic cartridge."""
    root = Path(project_root).resolve()
    db_path = Path(cartridge_path) if cartridge_path else default_project_document_cartridge_path(root)
    cartridge = SemanticCartridge(db_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = []
    ingested_paths: list[str] = []

    for relpath in document_relpaths:
        doc_path = (root / relpath).resolve()
        _ensure_project_owned(root, doc_path)
        document = read_text_source(doc_path)
        cartridge.delete_objects_for_source(document.source_ref)
        ingested_paths.append(relpath)
        for obj in semantic_objects_from_source(document):
            cartridge.upsert_object(obj)
            objects.append(obj)

    enrichment_report = enrich_relations(objects)
    persist_relation_enrichments(cartridge, enrichment_report)
    manifest = cartridge.manifest()
    return ProjectDocumentCorpus(
        version=PROJECT_DOCUMENT_INGESTION_VERSION,
        project_root=str(root),
        cartridge_path=str(db_path),
        document_paths=tuple(ingested_paths),
        object_count=len(objects),
        relation_count=manifest.relation_count,
    )


def _ensure_project_owned(root: Path, path: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Document path is outside project root: {path}") from exc


def _select_seed(objects: list[Any], seed_text_hint: str) -> Any:
    for obj in objects:
        if seed_text_hint and seed_text_hint in obj.content:
            return obj
    for obj in objects:
        if obj.occurrence and obj.occurrence.source_ref.endswith("PROJECT_STATUS.md"):
            return obj
    if not objects:
        raise ValueError("No project document semantic objects were produced")
    return objects[0]
