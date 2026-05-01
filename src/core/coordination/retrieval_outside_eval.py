"""Retrieval-only evaluation outside the tuned project scorer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge

from .project_documents import DEFAULT_PROJECT_DOCUMENT_PROFILE, ingest_project_documents

RETRIEVAL_OUTSIDE_EVAL_VERSION = "v1"
DEFAULT_SEMANTIC_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass(frozen=True)
class RetrievalEvalQuery:
    """One hand-labeled retrieval query for scorer-independent evaluation."""

    query_id: str
    query: str
    acceptable_source_suffixes: tuple[str, ...]
    preferred_heading_terms: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "query": self.query,
            "acceptable_source_suffixes": list(self.acceptable_source_suffixes),
            "preferred_heading_terms": list(self.preferred_heading_terms),
        }


@dataclass(frozen=True)
class RetrievalEvalCandidate:
    """One retrieval candidate independent of the tuned scorer."""

    semantic_id: str
    source_ref: str
    kind: str
    heading_trail: tuple[str, ...]
    preview: str
    lexical_score: float
    semantic_score: float
    hybrid_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "heading_trail": list(self.heading_trail),
            "preview": self.preview,
            "lexical_score": round(self.lexical_score, 4),
            "semantic_score": round(self.semantic_score, 4),
            "hybrid_score": round(self.hybrid_score, 4),
        }


@dataclass(frozen=True)
class RetrievalEvalMetrics:
    """Aggregate retrieval metrics for one retrieval method."""

    doc_hit_at_1: float
    doc_hit_at_3: float
    doc_hit_at_5: float
    heading_hit_at_1: float
    heading_hit_at_3: float
    heading_hit_at_5: float
    doc_mrr: float
    heading_mrr: float

    def to_dict(self) -> dict[str, float]:
        return {
            "doc_hit_at_1": round(self.doc_hit_at_1, 4),
            "doc_hit_at_3": round(self.doc_hit_at_3, 4),
            "doc_hit_at_5": round(self.doc_hit_at_5, 4),
            "heading_hit_at_1": round(self.heading_hit_at_1, 4),
            "heading_hit_at_3": round(self.heading_hit_at_3, 4),
            "heading_hit_at_5": round(self.heading_hit_at_5, 4),
            "doc_mrr": round(self.doc_mrr, 4),
            "heading_mrr": round(self.heading_mrr, 4),
        }


@dataclass(frozen=True)
class RetrievalEvalPerQuery:
    """Per-query retrieval results for each method."""

    query: RetrievalEvalQuery
    lexical_top5: tuple[RetrievalEvalCandidate, ...]
    semantic_top5: tuple[RetrievalEvalCandidate, ...]
    semantic_structured_top5: tuple[RetrievalEvalCandidate, ...]
    hybrid_top5: tuple[RetrievalEvalCandidate, ...]
    hybrid_weighted_top5: tuple[RetrievalEvalCandidate, ...]
    lexical_doc_hit_rank: int | None
    semantic_doc_hit_rank: int | None
    semantic_structured_doc_hit_rank: int | None
    hybrid_doc_hit_rank: int | None
    hybrid_weighted_doc_hit_rank: int | None
    lexical_heading_hit_rank: int | None
    semantic_heading_hit_rank: int | None
    semantic_structured_heading_hit_rank: int | None
    hybrid_heading_hit_rank: int | None
    hybrid_weighted_heading_hit_rank: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query.to_dict(),
            "lexical_top5": [candidate.to_dict() for candidate in self.lexical_top5],
            "semantic_top5": [candidate.to_dict() for candidate in self.semantic_top5],
            "semantic_structured_top5": [candidate.to_dict() for candidate in self.semantic_structured_top5],
            "hybrid_top5": [candidate.to_dict() for candidate in self.hybrid_top5],
            "hybrid_weighted_top5": [candidate.to_dict() for candidate in self.hybrid_weighted_top5],
            "lexical_doc_hit_rank": self.lexical_doc_hit_rank,
            "semantic_doc_hit_rank": self.semantic_doc_hit_rank,
            "semantic_structured_doc_hit_rank": self.semantic_structured_doc_hit_rank,
            "hybrid_doc_hit_rank": self.hybrid_doc_hit_rank,
            "hybrid_weighted_doc_hit_rank": self.hybrid_weighted_doc_hit_rank,
            "lexical_heading_hit_rank": self.lexical_heading_hit_rank,
            "semantic_heading_hit_rank": self.semantic_heading_hit_rank,
            "semantic_structured_heading_hit_rank": self.semantic_structured_heading_hit_rank,
            "hybrid_heading_hit_rank": self.hybrid_heading_hit_rank,
            "hybrid_weighted_heading_hit_rank": self.hybrid_weighted_heading_hit_rank,
        }


@dataclass(frozen=True)
class RetrievalOutsideEvalRun:
    """Full scorer-independent retrieval evaluation run."""

    version: str
    project_root: str
    document_profile: str
    document_paths: tuple[str, ...]
    cartridge_path: str
    corpus_object_count: int
    semantic_model_name: str
    lexical_metrics: RetrievalEvalMetrics
    semantic_metrics: RetrievalEvalMetrics
    semantic_structured_metrics: RetrievalEvalMetrics
    hybrid_metrics: RetrievalEvalMetrics
    hybrid_weighted_metrics: RetrievalEvalMetrics
    queries: tuple[RetrievalEvalPerQuery, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "document_profile": self.document_profile,
            "document_paths": list(self.document_paths),
            "cartridge_path": self.cartridge_path,
            "corpus_object_count": self.corpus_object_count,
            "semantic_model_name": self.semantic_model_name,
            "lexical_metrics": self.lexical_metrics.to_dict(),
            "semantic_metrics": self.semantic_metrics.to_dict(),
            "semantic_structured_metrics": self.semantic_structured_metrics.to_dict(),
            "hybrid_metrics": self.hybrid_metrics.to_dict(),
            "hybrid_weighted_metrics": self.hybrid_weighted_metrics.to_dict(),
            "queries": [query.to_dict() for query in self.queries],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_retrieval_eval_queries() -> tuple[RetrievalEvalQuery, ...]:
    """Return a bounded, hand-labeled scorer-independent query set."""
    return (
        RetrievalEvalQuery(
            query_id="park_marker_exact",
            query="Current Park Point",
            acceptable_source_suffixes=("PROJECT_STATUS.md",),
            preferred_heading_terms=("current park point",),
        ),
        RetrievalEvalQuery(
            query_id="park_marker_paraphrase",
            query="where are we parked now and what should we build next?",
            acceptable_source_suffixes=("PROJECT_STATUS.md",),
            preferred_heading_terms=("current park point", "proposed next tranche"),
        ),
        RetrievalEvalQuery(
            query_id="next_work_plan",
            query="what work comes immediately after the prototype phase?",
            acceptable_source_suffixes=("STRANGLER_PLAN.md",),
            preferred_heading_terms=("immediate post-prototype work",),
        ),
        RetrievalEvalQuery(
            query_id="mcp_surface",
            query="what MCP-facing tools or seams are available right now?",
            acceptable_source_suffixes=("MCP_SEAM.md",),
            preferred_heading_terms=("shared command spine", "tool registration", "mcp usefulness seam"),
        ),
        RetrievalEvalQuery(
            query_id="history_command",
            query="how do I inspect prior MCP calls?",
            acceptable_source_suffixes=("README.md", "MCP_SEAM.md"),
            preferred_heading_terms=("run", "persistent inspection history", "history-aware inspector"),
        ),
        RetrievalEvalQuery(
            query_id="history_command_terse",
            query="show command for saved inspection history",
            acceptable_source_suffixes=("README.md", "MCP_SEAM.md"),
            preferred_heading_terms=("run", "persistent inspection history"),
        ),
        RetrievalEvalQuery(
            query_id="tool_listing",
            query="which command lists the registered MCP tool candidates?",
            acceptable_source_suffixes=("README.md", "MCP_SEAM.md"),
            preferred_heading_terms=("run", "tool registration candidate"),
        ),
        RetrievalEvalQuery(
            query_id="bridge_transport",
            query="what bridge transport does the host use right now?",
            acceptable_source_suffixes=("README.md", "PROJECT_STATUS.md"),
            preferred_heading_terms=("current status", "project status"),
        ),
        RetrievalEvalQuery(
            query_id="visibility_fixture",
            query="what scores whether operator and builder can inspect the same evidence?",
            acceptable_source_suffixes=("README.md", "PROJECT_STATUS.md"),
            preferred_heading_terms=("current status", "current park point"),
        ),
        RetrievalEvalQuery(
            query_id="profile_compare",
            query="what are the core and expanded project doc profiles right now?",
            acceptable_source_suffixes=("README.md", "PROJECT_STATUS.md"),
            preferred_heading_terms=("current status", "run"),
        ),
        RetrievalEvalQuery(
            query_id="bridge_cleanup",
            query="how do I clean up stale bridge files?",
            acceptable_source_suffixes=("README.md", "PROJECT_STATUS.md"),
            preferred_heading_terms=("run", "current status"),
        ),
        RetrievalEvalQuery(
            query_id="panel_readback",
            query="how can the builder read what panel the human is looking at?",
            acceptable_source_suffixes=("README.md", "EXPERIENTIAL_WORKFLOW.md"),
            preferred_heading_terms=("run", "step 4: inspect what we just changed"),
        ),
        RetrievalEvalQuery(
            query_id="project_query_command",
            query="which command runs a project query through the host bridge?",
            acceptable_source_suffixes=("README.md", "MCP_SEAM.md"),
            preferred_heading_terms=("run", "shared command spine"),
        ),
        RetrievalEvalQuery(
            query_id="seed_search_command",
            query="what command searches for traversal seeds?",
            acceptable_source_suffixes=("README.md", "MCP_SEAM.md"),
            preferred_heading_terms=("run", "traversal seed search"),
        ),
        RetrievalEvalQuery(
            query_id="retention_policy",
            query="what is the retention policy for MCP inspection history?",
            acceptable_source_suffixes=("README.md", "PROJECT_STATUS.md", "MCP_SEAM.md"),
            preferred_heading_terms=("current status", "persistent inspection history"),
        ),
    )


def run_retrieval_outside_eval(
    project_root: Path | str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    semantic_model_name: str = DEFAULT_SEMANTIC_MODEL_NAME,
    queries: tuple[RetrievalEvalQuery, ...] = default_retrieval_eval_queries(),
) -> RetrievalOutsideEvalRun:
    """Run retrieval-only evaluation outside the tuned scorer."""
    corpus = ingest_project_documents(project_root, document_profile=document_profile)
    cartridge = SemanticCartridge(corpus.cartridge_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = cartridge.all_objects()
    corpus_texts = [_candidate_text(obj) for obj in objects]
    semantic_structured_texts = [_semantic_structured_text(obj) for obj in objects]

    lexical_vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    lexical_matrix = lexical_vectorizer.fit_transform(corpus_texts)

    semantic_model = SentenceTransformer(semantic_model_name)
    semantic_matrix = semantic_model.encode(corpus_texts, normalize_embeddings=True, show_progress_bar=False)
    semantic_structured_matrix = semantic_model.encode(
        semantic_structured_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_results: list[RetrievalEvalPerQuery] = []
    lexical_doc_ranks: list[int | None] = []
    semantic_doc_ranks: list[int | None] = []
    semantic_structured_doc_ranks: list[int | None] = []
    hybrid_doc_ranks: list[int | None] = []
    hybrid_weighted_doc_ranks: list[int | None] = []
    lexical_heading_ranks: list[int | None] = []
    semantic_heading_ranks: list[int | None] = []
    semantic_structured_heading_ranks: list[int | None] = []
    hybrid_heading_ranks: list[int | None] = []
    hybrid_weighted_heading_ranks: list[int | None] = []

    for query in queries:
        lexical_query = lexical_vectorizer.transform([query.query])
        lexical_scores = np.asarray((lexical_matrix @ lexical_query.T).todense()).ravel()
        semantic_query = semantic_model.encode([query.query], normalize_embeddings=True, show_progress_bar=False)[0]
        semantic_scores = np.dot(semantic_matrix, semantic_query)
        semantic_structured_scores = np.dot(semantic_structured_matrix, semantic_query)
        hybrid_scores = _normalize(lexical_scores) * 0.5 + _normalize(semantic_structured_scores) * 0.5
        hybrid_weighted_scores = (
            _normalize(lexical_scores) * 0.7
            + _normalize(semantic_structured_scores) * 0.3
        )

        lexical_ranked = _top_candidates(
            objects,
            lexical_scores,
            semantic_scores,
            semantic_structured_scores,
            hybrid_scores,
            hybrid_weighted_scores,
            key="lexical",
        )
        semantic_ranked = _top_candidates(
            objects,
            lexical_scores,
            semantic_scores,
            semantic_structured_scores,
            hybrid_scores,
            hybrid_weighted_scores,
            key="semantic",
        )
        semantic_structured_ranked = _top_candidates(
            objects,
            lexical_scores,
            semantic_scores,
            semantic_structured_scores,
            hybrid_scores,
            hybrid_weighted_scores,
            key="semantic_structured",
        )
        hybrid_ranked = _top_candidates(
            objects,
            lexical_scores,
            semantic_scores,
            semantic_structured_scores,
            hybrid_scores,
            hybrid_weighted_scores,
            key="hybrid",
        )
        hybrid_weighted_ranked = _top_candidates(
            objects,
            lexical_scores,
            semantic_scores,
            semantic_structured_scores,
            hybrid_scores,
            hybrid_weighted_scores,
            key="hybrid_weighted",
        )

        lexical_doc_rank = _first_doc_hit_rank(lexical_ranked, query)
        semantic_doc_rank = _first_doc_hit_rank(semantic_ranked, query)
        semantic_structured_doc_rank = _first_doc_hit_rank(semantic_structured_ranked, query)
        hybrid_doc_rank = _first_doc_hit_rank(hybrid_ranked, query)
        hybrid_weighted_doc_rank = _first_doc_hit_rank(hybrid_weighted_ranked, query)
        lexical_heading_rank = _first_heading_hit_rank(lexical_ranked, query)
        semantic_heading_rank = _first_heading_hit_rank(semantic_ranked, query)
        semantic_structured_heading_rank = _first_heading_hit_rank(semantic_structured_ranked, query)
        hybrid_heading_rank = _first_heading_hit_rank(hybrid_ranked, query)
        hybrid_weighted_heading_rank = _first_heading_hit_rank(hybrid_weighted_ranked, query)

        lexical_doc_ranks.append(lexical_doc_rank)
        semantic_doc_ranks.append(semantic_doc_rank)
        semantic_structured_doc_ranks.append(semantic_structured_doc_rank)
        hybrid_doc_ranks.append(hybrid_doc_rank)
        hybrid_weighted_doc_ranks.append(hybrid_weighted_doc_rank)
        lexical_heading_ranks.append(lexical_heading_rank)
        semantic_heading_ranks.append(semantic_heading_rank)
        semantic_structured_heading_ranks.append(semantic_structured_heading_rank)
        hybrid_heading_ranks.append(hybrid_heading_rank)
        hybrid_weighted_heading_ranks.append(hybrid_weighted_heading_rank)

        query_results.append(
            RetrievalEvalPerQuery(
                query=query,
                lexical_top5=tuple(lexical_ranked[:5]),
                semantic_top5=tuple(semantic_ranked[:5]),
                semantic_structured_top5=tuple(semantic_structured_ranked[:5]),
                hybrid_top5=tuple(hybrid_ranked[:5]),
                hybrid_weighted_top5=tuple(hybrid_weighted_ranked[:5]),
                lexical_doc_hit_rank=lexical_doc_rank,
                semantic_doc_hit_rank=semantic_doc_rank,
                semantic_structured_doc_hit_rank=semantic_structured_doc_rank,
                hybrid_doc_hit_rank=hybrid_doc_rank,
                hybrid_weighted_doc_hit_rank=hybrid_weighted_doc_rank,
                lexical_heading_hit_rank=lexical_heading_rank,
                semantic_heading_hit_rank=semantic_heading_rank,
                semantic_structured_heading_hit_rank=semantic_structured_heading_rank,
                hybrid_heading_hit_rank=hybrid_heading_rank,
                hybrid_weighted_heading_hit_rank=hybrid_weighted_heading_rank,
            )
        )

    return RetrievalOutsideEvalRun(
        version=RETRIEVAL_OUTSIDE_EVAL_VERSION,
        project_root=corpus.project_root,
        document_profile=corpus.document_profile,
        document_paths=corpus.document_paths,
        cartridge_path=corpus.cartridge_path,
        corpus_object_count=corpus.object_count,
        semantic_model_name=semantic_model_name,
        lexical_metrics=_metrics_from_ranks(lexical_doc_ranks, lexical_heading_ranks, len(queries)),
        semantic_metrics=_metrics_from_ranks(semantic_doc_ranks, semantic_heading_ranks, len(queries)),
        semantic_structured_metrics=_metrics_from_ranks(
            semantic_structured_doc_ranks,
            semantic_structured_heading_ranks,
            len(queries),
        ),
        hybrid_metrics=_metrics_from_ranks(hybrid_doc_ranks, hybrid_heading_ranks, len(queries)),
        hybrid_weighted_metrics=_metrics_from_ranks(
            hybrid_weighted_doc_ranks,
            hybrid_weighted_heading_ranks,
            len(queries),
        ),
        queries=tuple(query_results),
    )


def _candidate_text(obj: Any) -> str:
    occurrence = obj.occurrence
    source_ref = occurrence.source_ref if occurrence else ""
    heading_trail = " > ".join(str(item) for item in occurrence.local_context.get("heading_trail", ())) if occurrence else ""
    return "\n".join(part for part in (source_ref, heading_trail, obj.kind, obj.content) if part)


def _semantic_structured_text(obj: Any) -> str:
    occurrence = obj.occurrence
    source_ref = occurrence.source_ref if occurrence else ""
    heading_trail = tuple(str(item) for item in occurrence.local_context.get("heading_trail", ())) if occurrence else ()
    heading_text = " > ".join(heading_trail)
    source_name = Path(source_ref).name if source_ref else ""
    kind = str(obj.kind).replace("_", " ")
    content = " ".join(obj.content.split())
    repeated_heading = f"{heading_text}. {heading_text}." if heading_text else ""
    return "\n".join(
        part
        for part in (
            f"document {source_name}",
            f"section {heading_text}" if heading_text else "",
            f"kind {kind}",
            repeated_heading,
            content,
        )
        if part
    )


def _preview(text: str, limit: int = 220) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def _normalize(scores: np.ndarray) -> np.ndarray:
    minimum = float(scores.min())
    maximum = float(scores.max())
    if maximum - minimum <= 1e-12:
        return np.zeros_like(scores, dtype=float)
    return (scores - minimum) / (maximum - minimum)


def _top_candidates(
    objects: list[Any],
    lexical_scores: np.ndarray,
    semantic_scores: np.ndarray,
    semantic_structured_scores: np.ndarray,
    hybrid_scores: np.ndarray,
    hybrid_weighted_scores: np.ndarray,
    *,
    key: str,
) -> list[RetrievalEvalCandidate]:
    key_scores = {
        "lexical": lexical_scores,
        "semantic": semantic_scores,
        "semantic_structured": semantic_structured_scores,
        "hybrid": hybrid_scores,
        "hybrid_weighted": hybrid_weighted_scores,
    }[key]
    order = np.argsort(-key_scores)
    ranked: list[RetrievalEvalCandidate] = []
    for index in order.tolist():
        obj = objects[index]
        occurrence = obj.occurrence
        ranked.append(
            RetrievalEvalCandidate(
                semantic_id=obj.semantic_id,
                source_ref=occurrence.source_ref if occurrence else "",
                kind=obj.kind,
                heading_trail=tuple(str(item) for item in occurrence.local_context.get("heading_trail", ())) if occurrence else (),
                preview=_preview(obj.content),
                lexical_score=float(lexical_scores[index]),
                semantic_score=float(semantic_structured_scores[index]),
                hybrid_score=float(hybrid_scores[index]),
            )
        )
    return ranked


def _first_doc_hit_rank(candidates: list[RetrievalEvalCandidate], query: RetrievalEvalQuery) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        if any(candidate.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            return index
    return None


def _first_heading_hit_rank(candidates: list[RetrievalEvalCandidate], query: RetrievalEvalQuery) -> int | None:
    if not query.preferred_heading_terms:
        return _first_doc_hit_rank(candidates, query)
    for index, candidate in enumerate(candidates, start=1):
        if not any(candidate.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            continue
        joined_heading = " > ".join(candidate.heading_trail).lower()
        if any(term in joined_heading for term in query.preferred_heading_terms):
            return index
    return None


def _metrics_from_ranks(
    doc_ranks: list[int | None],
    heading_ranks: list[int | None],
    query_count: int,
) -> RetrievalEvalMetrics:
    return RetrievalEvalMetrics(
        doc_hit_at_1=_hit_at_k(doc_ranks, 1, query_count),
        doc_hit_at_3=_hit_at_k(doc_ranks, 3, query_count),
        doc_hit_at_5=_hit_at_k(doc_ranks, 5, query_count),
        heading_hit_at_1=_hit_at_k(heading_ranks, 1, query_count),
        heading_hit_at_3=_hit_at_k(heading_ranks, 3, query_count),
        heading_hit_at_5=_hit_at_k(heading_ranks, 5, query_count),
        doc_mrr=_mean_reciprocal_rank(doc_ranks, query_count),
        heading_mrr=_mean_reciprocal_rank(heading_ranks, query_count),
    )


def _hit_at_k(ranks: list[int | None], k: int, query_count: int) -> float:
    if query_count <= 0:
        return 0.0
    hits = sum(1 for rank in ranks if rank is not None and rank <= k)
    return hits / query_count


def _mean_reciprocal_rank(ranks: list[int | None], query_count: int) -> float:
    if query_count <= 0:
        return 0.0
    total = 0.0
    for rank in ranks:
        if rank is not None and rank > 0:
            total += 1.0 / rank
    return total / query_count
