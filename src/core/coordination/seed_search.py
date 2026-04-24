"""Seed search over the bounded project-document semantic cartridge."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge

from .mcp_inspection_history import McpInspectionHistoryRecord, McpInspectionHistoryStore
from .mcp_tool_registry import TRAVERSAL_TOOL_NAME, McpToolCallResult, call_registered_mcp_tool
from .project_documents import default_project_document_cartridge_path
from .project_documents import ProjectDocumentCorpus, ingest_project_documents
from .seed_fitness import SeedSearchCandidate, rank_seed_candidates

SEED_SEARCH_VERSION = "v1"


@dataclass(frozen=True)
class SeedFlowObject:
    """One source-ordered object around a selected traversal seed."""

    role: str
    semantic_id: str
    source_ref: str
    kind: str
    content_preview: str
    block_index: int | None
    line_span: tuple[int | None, int | None]
    heading_trail: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "content_preview": self.content_preview,
            "block_index": self.block_index,
            "line_span": list(self.line_span),
            "heading_trail": list(self.heading_trail),
        }


@dataclass(frozen=True)
class SeedFlowWindow:
    """Previous / selected / next source-flow context for a seed."""

    source_ref: str
    breadcrumb: tuple[str, ...]
    objects: tuple[SeedFlowObject, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_ref": self.source_ref,
            "breadcrumb": list(self.breadcrumb),
            "objects": [obj.to_dict() for obj in self.objects],
        }


@dataclass(frozen=True)
class SeedSearchResult:
    """Ranked seed search result over a project-document corpus."""

    version: str
    query: str
    cartridge_path: str
    candidate_count: int
    candidates: tuple[SeedSearchCandidate, ...]
    selected_flow: SeedFlowWindow | None = None

    @property
    def selected_seed(self) -> SeedSearchCandidate | None:
        return self.candidates[0] if self.candidates else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "query": self.query,
            "cartridge_path": self.cartridge_path,
            "candidate_count": self.candidate_count,
            "selected_seed": self.selected_seed.to_dict() if self.selected_seed else None,
            "selected_flow": self.selected_flow.to_dict() if self.selected_flow else None,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


@dataclass(frozen=True)
class SeedTraversalSelectionResult:
    """Search result plus the registered traversal call selected from it."""

    version: str
    corpus: ProjectDocumentCorpus
    search: SeedSearchResult
    tool_call: McpToolCallResult
    history_record: McpInspectionHistoryRecord | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "corpus": self.corpus.to_dict(),
            "search": self.search.to_dict(),
            "tool_call": self.tool_call.to_dict(),
            "history_record": self.history_record.to_dict() if self.history_record else None,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def search_project_document_seeds(
    project_root: Path | str,
    query: str,
    *,
    limit: int = 5,
    cartridge_path: Path | str | None = None,
) -> SeedSearchResult:
    """Ingest bounded project docs and rank matching semantic objects."""
    corpus = ingest_project_documents(project_root, cartridge_path=cartridge_path)
    cartridge = SemanticCartridge(corpus.cartridge_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = cartridge.all_objects()
    candidates = rank_seed_candidates(objects, query, limit=limit)
    selected = candidates[0] if candidates else None
    return SeedSearchResult(
        version=SEED_SEARCH_VERSION,
        query=query,
        cartridge_path=corpus.cartridge_path,
        candidate_count=len(candidates),
        candidates=tuple(candidates),
        selected_flow=_selected_flow_window(objects, selected),
    )


def run_seed_search_traversal(
    project_root: Path | str,
    query: str,
    *,
    history_path: Path | str | None = None,
    limit: int = 5,
    max_depth: int = 2,
    max_steps: int = 64,
) -> SeedTraversalSelectionResult:
    """Search project-document seeds, call traversal on the top seed, and record history."""
    corpus = ingest_project_documents(project_root)
    cartridge = SemanticCartridge(corpus.cartridge_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = cartridge.all_objects()
    candidates = tuple(rank_seed_candidates(objects, query, limit=limit))
    search = SeedSearchResult(
        version=SEED_SEARCH_VERSION,
        query=query,
        cartridge_path=corpus.cartridge_path,
        candidate_count=len(candidates),
        candidates=candidates,
        selected_flow=_selected_flow_window(objects, candidates[0] if candidates else None),
    )
    selected = search.selected_seed
    if selected is None:
        raise ValueError(f"No project-document seed candidates matched query: {query}")
    tool_call = call_registered_mcp_tool(
        TRAVERSAL_TOOL_NAME,
        {
            "db_path": corpus.cartridge_path,
            "cartridge_id": DEFAULT_CARTRIDGE_ID,
            "seed_semantic_id": selected.semantic_id,
            "max_depth": max_depth,
            "max_steps": max_steps,
            "include_incoming": True,
        },
    )
    history_record = None
    if history_path is not None:
        history_record = McpInspectionHistoryStore(history_path).record_call(tool_call.to_dict())
    return SeedTraversalSelectionResult(
        version=SEED_SEARCH_VERSION,
        corpus=corpus,
        search=search,
        tool_call=tool_call,
        history_record=history_record,
    )


def seed_flow_window_for_semantic_id(
    project_root: Path | str,
    semantic_id: str,
    *,
    cartridge_path: Path | str | None = None,
) -> SeedFlowWindow | None:
    """Return source-ordered flow context for a persisted semantic object id."""
    db_path = Path(cartridge_path) if cartridge_path else default_project_document_cartridge_path(project_root)
    if not db_path.exists():
        return None
    cartridge = SemanticCartridge(db_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = cartridge.all_objects()
    selected = next((obj for obj in objects if obj.semantic_id == semantic_id), None)
    if selected is None or not selected.occurrence:
        return None
    line_span = (
        selected.occurrence.source_span.start,
        selected.occurrence.source_span.end,
    )
    candidate = SeedSearchCandidate(
        semantic_id=selected.semantic_id,
        source_ref=selected.occurrence.source_ref,
        kind=selected.kind,
        content_preview=_preview(selected.content),
        line_span=line_span,
        score=0.0,
        matched_terms=(),
        heading_trail=tuple(
            str(item) for item in selected.occurrence.local_context.get("heading_trail", ())
        ),
        block_index=(
            int(selected.occurrence.local_context["block_index"])
            if isinstance(selected.occurrence.local_context.get("block_index"), int)
            else None
        ),
        score_breakdown={},
    )
    return _selected_flow_window(objects, candidate)


def _selected_flow_window(
    objects: list[Any],
    selected: SeedSearchCandidate | None,
) -> SeedFlowWindow | None:
    if selected is None:
        return None
    same_source = [
        obj for obj in objects
        if obj.occurrence and obj.occurrence.source_ref == selected.source_ref
    ]
    same_source.sort(key=_flow_object_sort_key)
    selected_index = next(
        (index for index, obj in enumerate(same_source) if obj.semantic_id == selected.semantic_id),
        None,
    )
    if selected_index is None:
        return None
    start = max(0, selected_index - 1)
    end = min(len(same_source), selected_index + 2)
    flow_objects: list[SeedFlowObject] = []
    for index in range(start, end):
        role = "selected"
        if index < selected_index:
            role = "previous"
        elif index > selected_index:
            role = "next"
        flow_objects.append(_flow_object(same_source[index], role))
    breadcrumb = tuple(
        item for item in (
            selected.source_ref,
            *selected.heading_trail,
            f"block {selected.block_index}" if selected.block_index is not None else "",
        )
        if item
    )
    return SeedFlowWindow(
        source_ref=selected.source_ref,
        breadcrumb=breadcrumb,
        objects=tuple(flow_objects),
    )


def _flow_object(obj: Any, role: str) -> SeedFlowObject:
    occurrence = obj.occurrence
    source_ref = occurrence.source_ref if occurrence else ""
    line_span = (
        occurrence.source_span.start if occurrence else None,
        occurrence.source_span.end if occurrence else None,
    )
    local_context = occurrence.local_context if occurrence else {}
    heading_trail = tuple(str(item) for item in local_context.get("heading_trail", ()))
    block_index = local_context.get("block_index")
    return SeedFlowObject(
        role=role,
        semantic_id=obj.semantic_id,
        source_ref=source_ref,
        kind=obj.kind,
        content_preview=_preview(obj.content),
        block_index=int(block_index) if isinstance(block_index, int) else None,
        line_span=line_span,
        heading_trail=heading_trail,
    )


def _flow_object_sort_key(obj: Any) -> tuple[int, int, str]:
    occurrence = obj.occurrence
    local_context = occurrence.local_context if occurrence else {}
    block_index = local_context.get("block_index")
    line_start = occurrence.source_span.start if occurrence else None
    return (
        int(block_index) if isinstance(block_index, int) else 999999,
        int(line_start) if isinstance(line_start, int) else 999999,
        obj.semantic_id,
    )


def _preview(content: str, limit: int = 220) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."
