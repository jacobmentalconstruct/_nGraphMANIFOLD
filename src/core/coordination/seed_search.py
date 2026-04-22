"""Seed search over the bounded project-document semantic cartridge."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation import SemanticObject

from .mcp_inspection_history import McpInspectionHistoryRecord, McpInspectionHistoryStore
from .mcp_tool_registry import TRAVERSAL_TOOL_NAME, McpToolCallResult, call_registered_mcp_tool
from .project_documents import ProjectDocumentCorpus, ingest_project_documents

SEED_SEARCH_VERSION = "v1"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class SeedSearchCandidate:
    """One ranked semantic object that can serve as a traversal seed."""

    semantic_id: str
    source_ref: str
    kind: str
    content_preview: str
    score: float
    matched_terms: tuple[str, ...]
    block_index: int | None
    line_span: tuple[int | None, int | None]
    heading_trail: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "content_preview": self.content_preview,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "block_index": self.block_index,
            "line_span": list(self.line_span),
            "heading_trail": list(self.heading_trail),
        }


@dataclass(frozen=True)
class SeedSearchResult:
    """Ranked seed search result over a project-document corpus."""

    version: str
    query: str
    cartridge_path: str
    candidate_count: int
    candidates: tuple[SeedSearchCandidate, ...]

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
    candidates = rank_seed_candidates(cartridge.all_objects(), query, limit=limit)
    return SeedSearchResult(
        version=SEED_SEARCH_VERSION,
        query=query,
        cartridge_path=corpus.cartridge_path,
        candidate_count=len(candidates),
        candidates=tuple(candidates),
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
    candidates = tuple(rank_seed_candidates(cartridge.all_objects(), query, limit=limit))
    search = SeedSearchResult(
        version=SEED_SEARCH_VERSION,
        query=query,
        cartridge_path=corpus.cartridge_path,
        candidate_count=len(candidates),
        candidates=candidates,
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


def rank_seed_candidates(
    objects: list[SemanticObject],
    query: str,
    *,
    limit: int = 5,
) -> list[SeedSearchCandidate]:
    """Rank semantic objects with a deterministic owned text scorer."""
    terms = tuple(dict.fromkeys(token.lower() for token in TOKEN_PATTERN.findall(query)))
    if not terms:
        raise ValueError("Seed search query must contain at least one alphanumeric term")
    ranked = [_candidate_for_object(obj, query, terms) for obj in objects]
    candidates = [candidate for candidate in ranked if candidate.score > 0]
    candidates.sort(key=_candidate_sort_key)
    return candidates[: max(1, limit)]


def _candidate_for_object(
    obj: SemanticObject,
    query: str,
    terms: tuple[str, ...],
) -> SeedSearchCandidate:
    occurrence = obj.occurrence
    source_ref = occurrence.source_ref if occurrence else ""
    line_span = (
        occurrence.source_span.start if occurrence else None,
        occurrence.source_span.end if occurrence else None,
    )
    local_context = occurrence.local_context if occurrence else {}
    heading_trail = tuple(str(item) for item in local_context.get("heading_trail", ()))
    block_index = local_context.get("block_index")
    normalized_content = obj.content.lower()
    normalized_source = source_ref.lower()
    normalized_heading = " ".join(heading_trail).lower()
    normalized_query = query.strip().lower()

    matched_terms = tuple(
        term
        for term in terms
        if term in normalized_content or term in normalized_source or term in normalized_heading
    )
    score = 0.0
    if normalized_query and normalized_query in normalized_content:
        score += 5.0
    if normalized_query and normalized_query in normalized_source:
        score += 2.0
    for term in terms:
        if term in normalized_content:
            score += 1.0
        if term in normalized_heading:
            score += 0.75
        if term in normalized_source:
            score += 0.5
    if obj.kind == "heading":
        score += 0.25
    score += max(0.0, 0.25 - min(len(obj.content), 1000) / 4000)

    return SeedSearchCandidate(
        semantic_id=obj.semantic_id,
        source_ref=source_ref,
        kind=obj.kind,
        content_preview=_preview(obj.content),
        score=round(score, 4),
        matched_terms=matched_terms,
        block_index=int(block_index) if isinstance(block_index, int) else None,
        line_span=line_span,
        heading_trail=heading_trail,
    )


def _candidate_sort_key(candidate: SeedSearchCandidate) -> tuple[float, str, int, str]:
    block_index = candidate.block_index if candidate.block_index is not None else 999999
    return (-candidate.score, candidate.source_ref, block_index, candidate.semantic_id)


def _preview(content: str, limit: int = 220) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."
