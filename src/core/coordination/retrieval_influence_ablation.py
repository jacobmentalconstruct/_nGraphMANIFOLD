"""Fixture for separating deterministic retrieval gains from ML influence."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from .project_documents import DEFAULT_PROJECT_DOCUMENT_PROFILE
from .project_query_lens_bag import (
    DEFAULT_CHAR_BUDGET,
    DEFAULT_MAX_ITEMS,
    DEFAULT_MAX_NODES,
    DEFAULT_MAX_SEEDS,
    DEFAULT_RADIUS,
    ProjectQueryLensBagWorkspace,
    build_project_query_lens_bag_workspace,
    run_project_query_lens_bag,
)
from .retrieval_outside_eval import RetrievalEvalQuery, default_retrieval_eval_queries
from .seed_fitness import SeedFitnessPolicy, SeedSearchCandidate, rank_seed_candidates

RETRIEVAL_INFLUENCE_ABLATION_VERSION = "v1"
ZERO_SEMANTIC_MODEL_NAME = "deterministic_ablation:zero_semantic_vector"


@dataclass(frozen=True)
class AblationEvidenceItem:
    """One ranked evidence item in an ablation packet."""

    role: str
    source_ref: str
    heading_trail: tuple[str, ...]
    kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "source_ref": self.source_ref,
            "heading_trail": list(self.heading_trail),
            "kind": self.kind,
        }


@dataclass(frozen=True)
class AblationMethodMetrics:
    """Coverage metrics for one retrieval influence method."""

    doc_hit_at_1: float
    doc_hit_at_3: float
    doc_hit_at_5: float
    doc_hit_at_8: float
    heading_hit_at_1: float
    heading_hit_at_3: float
    heading_hit_at_5: float
    heading_hit_at_8: float
    doc_mrr: float
    heading_mrr: float

    def to_dict(self) -> dict[str, float]:
        return {
            "doc_hit_at_1": round(self.doc_hit_at_1, 4),
            "doc_hit_at_3": round(self.doc_hit_at_3, 4),
            "doc_hit_at_5": round(self.doc_hit_at_5, 4),
            "doc_hit_at_8": round(self.doc_hit_at_8, 4),
            "heading_hit_at_1": round(self.heading_hit_at_1, 4),
            "heading_hit_at_3": round(self.heading_hit_at_3, 4),
            "heading_hit_at_5": round(self.heading_hit_at_5, 4),
            "heading_hit_at_8": round(self.heading_hit_at_8, 4),
            "doc_mrr": round(self.doc_mrr, 4),
            "heading_mrr": round(self.heading_mrr, 4),
        }


@dataclass(frozen=True)
class RetrievalInfluenceAblationRow:
    """One labeled query compared across influence-isolation methods."""

    query: RetrievalEvalQuery
    ml_lens_profile: str
    deterministic_lens_profile: str
    baseline_doc_hit_rank: int | None
    baseline_heading_hit_rank: int | None
    deterministic_doc_hit_rank: int | None
    deterministic_heading_hit_rank: int | None
    ml_doc_hit_rank: int | None
    ml_heading_hit_rank: int | None
    deterministic_evidence: tuple[AblationEvidenceItem, ...]
    ml_evidence: tuple[AblationEvidenceItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": {
                "query_id": self.query.query_id,
                "query": self.query.query,
                "acceptable_source_suffixes": list(self.query.acceptable_source_suffixes),
                "preferred_heading_terms": list(self.query.preferred_heading_terms),
            },
            "ml_lens_profile": self.ml_lens_profile,
            "deterministic_lens_profile": self.deterministic_lens_profile,
            "baseline_doc_hit_rank": self.baseline_doc_hit_rank,
            "baseline_heading_hit_rank": self.baseline_heading_hit_rank,
            "deterministic_doc_hit_rank": self.deterministic_doc_hit_rank,
            "deterministic_heading_hit_rank": self.deterministic_heading_hit_rank,
            "ml_doc_hit_rank": self.ml_doc_hit_rank,
            "ml_heading_hit_rank": self.ml_heading_hit_rank,
            "deterministic_evidence": [item.to_dict() for item in self.deterministic_evidence],
            "ml_evidence": [item.to_dict() for item in self.ml_evidence],
        }


@dataclass(frozen=True)
class RetrievalInfluenceAblationRun:
    """Full retrieval influence ablation artifact."""

    version: str
    project_root: str
    document_profile: str
    query_count: int
    semantic_model_name: str
    deterministic_semantic_model_name: str
    corpus_object_count: int
    corpus_relation_count: int
    baseline_metrics: AblationMethodMetrics
    deterministic_companion_metrics: AblationMethodMetrics
    ml_companion_metrics: AblationMethodMetrics
    interpretation: dict[str, Any]
    rows: tuple[RetrievalInfluenceAblationRow, ...]
    elapsed_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "document_profile": self.document_profile,
            "query_count": self.query_count,
            "semantic_model_name": self.semantic_model_name,
            "deterministic_semantic_model_name": self.deterministic_semantic_model_name,
            "corpus_object_count": self.corpus_object_count,
            "corpus_relation_count": self.corpus_relation_count,
            "baseline_metrics": self.baseline_metrics.to_dict(),
            "deterministic_companion_metrics": self.deterministic_companion_metrics.to_dict(),
            "ml_companion_metrics": self.ml_companion_metrics.to_dict(),
            "interpretation": self.interpretation,
            "rows": [row.to_dict() for row in self.rows],
            "elapsed_ms": self.elapsed_ms,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


class ZeroSemanticModel:
    """Deterministic encoder that removes semantic-vector influence."""

    def __init__(self, dimensions: int) -> None:
        self.dimensions = max(1, dimensions)

    def encode(
        self,
        texts: list[str] | tuple[str, ...],
        *,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        del normalize_embeddings, show_progress_bar
        return np.zeros((len(texts), self.dimensions), dtype=float)


def default_retrieval_influence_ablation_path(project_root: Path | str) -> Path:
    """Return the default artifact path for retrieval influence ablation."""
    return Path(project_root) / "data" / "mcp_inspection" / "retrieval_influence_ablation.json"


def run_retrieval_influence_ablation(
    project_root: Path | str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    queries: tuple[RetrievalEvalQuery, ...] = default_retrieval_eval_queries(),
    max_seeds: int = DEFAULT_MAX_SEEDS,
    radius: int = DEFAULT_RADIUS,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_items: int = DEFAULT_MAX_ITEMS,
    char_budget: int = DEFAULT_CHAR_BUDGET,
    workspace: ProjectQueryLensBagWorkspace | None = None,
) -> RetrievalInfluenceAblationRun:
    """Compare baseline, deterministic-only companion, and ML companion evidence."""
    started = time.perf_counter()
    active_workspace = workspace or build_project_query_lens_bag_workspace(
        project_root,
        document_profile=document_profile,
    )
    deterministic_workspace = _zero_semantic_workspace(active_workspace)

    baseline_doc_ranks: list[int | None] = []
    baseline_heading_ranks: list[int | None] = []
    deterministic_doc_ranks: list[int | None] = []
    deterministic_heading_ranks: list[int | None] = []
    ml_doc_ranks: list[int | None] = []
    ml_heading_ranks: list[int | None] = []
    rows: list[RetrievalInfluenceAblationRow] = []

    for query in queries:
        baseline_candidates = list(
            rank_seed_candidates(
                list(active_workspace.objects),
                query.query,
                limit=5,
                policy=SeedFitnessPolicy(seed_text_hint=query.query, question=query.query),
            )
        )
        baseline_top = baseline_candidates[0] if baseline_candidates else None
        baseline_packet = _baseline_packet(baseline_top)
        baseline_doc_rank = _first_doc_hit_rank(baseline_packet, query)
        baseline_heading_rank = _first_heading_hit_rank(baseline_packet, query)

        deterministic_run = run_project_query_lens_bag(
            deterministic_workspace.project_root,
            query.query,
            document_profile=document_profile,
            lens_profile="auto",
            max_seeds=max_seeds,
            radius=radius,
            max_nodes=max_nodes,
            max_items=max_items,
            char_budget=char_budget,
            workspace=deterministic_workspace,
        )
        deterministic_evidence = _combined_evidence_packet(
            baseline_top,
            deterministic_run.bag_items,
        )
        deterministic_doc_rank = _first_doc_hit_rank(deterministic_evidence, query)
        deterministic_heading_rank = _first_heading_hit_rank(deterministic_evidence, query)

        ml_run = run_project_query_lens_bag(
            active_workspace.project_root,
            query.query,
            document_profile=document_profile,
            lens_profile="auto",
            max_seeds=max_seeds,
            radius=radius,
            max_nodes=max_nodes,
            max_items=max_items,
            char_budget=char_budget,
            workspace=active_workspace,
        )
        ml_evidence = _combined_evidence_packet(baseline_top, ml_run.bag_items)
        ml_doc_rank = _first_doc_hit_rank(ml_evidence, query)
        ml_heading_rank = _first_heading_hit_rank(ml_evidence, query)

        baseline_doc_ranks.append(baseline_doc_rank)
        baseline_heading_ranks.append(baseline_heading_rank)
        deterministic_doc_ranks.append(deterministic_doc_rank)
        deterministic_heading_ranks.append(deterministic_heading_rank)
        ml_doc_ranks.append(ml_doc_rank)
        ml_heading_ranks.append(ml_heading_rank)

        rows.append(
            RetrievalInfluenceAblationRow(
                query=query,
                ml_lens_profile=ml_run.lens_profile,
                deterministic_lens_profile=deterministic_run.lens_profile,
                baseline_doc_hit_rank=baseline_doc_rank,
                baseline_heading_hit_rank=baseline_heading_rank,
                deterministic_doc_hit_rank=deterministic_doc_rank,
                deterministic_heading_hit_rank=deterministic_heading_rank,
                ml_doc_hit_rank=ml_doc_rank,
                ml_heading_hit_rank=ml_heading_rank,
                deterministic_evidence=deterministic_evidence,
                ml_evidence=ml_evidence,
            )
        )

    baseline_metrics = _metrics_from_ranks(baseline_doc_ranks, baseline_heading_ranks, len(queries))
    deterministic_metrics = _metrics_from_ranks(
        deterministic_doc_ranks,
        deterministic_heading_ranks,
        len(queries),
    )
    ml_metrics = _metrics_from_ranks(ml_doc_ranks, ml_heading_ranks, len(queries))

    return RetrievalInfluenceAblationRun(
        version=RETRIEVAL_INFLUENCE_ABLATION_VERSION,
        project_root=active_workspace.project_root,
        document_profile=active_workspace.document_profile,
        query_count=len(queries),
        semantic_model_name=active_workspace.semantic_model_name,
        deterministic_semantic_model_name=ZERO_SEMANTIC_MODEL_NAME,
        corpus_object_count=len(active_workspace.objects),
        corpus_relation_count=active_workspace.manifest_relation_count,
        baseline_metrics=baseline_metrics,
        deterministic_companion_metrics=deterministic_metrics,
        ml_companion_metrics=ml_metrics,
        interpretation=_interpret_metrics(baseline_metrics, deterministic_metrics, ml_metrics),
        rows=tuple(rows),
        elapsed_ms=round((time.perf_counter() - started) * 1000),
    )


def save_retrieval_influence_ablation_run(
    run: RetrievalInfluenceAblationRun,
    output_path: Path | str,
) -> Path:
    """Persist the retrieval influence ablation artifact."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.to_json(), encoding="utf-8")
    return path


def _zero_semantic_workspace(
    workspace: ProjectQueryLensBagWorkspace,
) -> ProjectQueryLensBagWorkspace:
    if workspace.semantic_matrix.ndim == 2 and workspace.semantic_matrix.shape[1] > 0:
        dimensions = int(workspace.semantic_matrix.shape[1])
    else:
        dimensions = 1
    return replace(
        workspace,
        semantic_model_name=ZERO_SEMANTIC_MODEL_NAME,
        semantic_model=ZeroSemanticModel(dimensions),
        semantic_matrix=np.zeros_like(workspace.semantic_matrix, dtype=float),
    )


def _baseline_packet(
    baseline_top: SeedSearchCandidate | None,
) -> tuple[AblationEvidenceItem, ...]:
    if baseline_top is None:
        return ()
    return (
        AblationEvidenceItem(
            role="baseline_seed",
            source_ref=baseline_top.source_ref,
            heading_trail=baseline_top.heading_trail,
            kind=baseline_top.kind,
        ),
    )


def _combined_evidence_packet(
    baseline_top: SeedSearchCandidate | None,
    bag_items: tuple[Any, ...],
) -> tuple[AblationEvidenceItem, ...]:
    seen: set[tuple[str, tuple[str, ...], str]] = set()
    combined = list(_baseline_packet(baseline_top))
    for item in combined:
        seen.add((item.source_ref, item.heading_trail, item.kind))

    for bag_item in bag_items:
        key = (bag_item.source_ref, bag_item.heading_trail, bag_item.kind)
        if key in seen:
            continue
        seen.add(key)
        combined.append(
            AblationEvidenceItem(
                role=f"bag_{bag_item.source_role}",
                source_ref=bag_item.source_ref,
                heading_trail=bag_item.heading_trail,
                kind=bag_item.kind,
            )
        )
    return tuple(combined)


def _first_doc_hit_rank(
    candidates: tuple[AblationEvidenceItem, ...],
    query: RetrievalEvalQuery,
) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        if any(candidate.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            return index
    return None


def _first_heading_hit_rank(
    candidates: tuple[AblationEvidenceItem, ...],
    query: RetrievalEvalQuery,
) -> int | None:
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
) -> AblationMethodMetrics:
    return AblationMethodMetrics(
        doc_hit_at_1=_hit_at_k(doc_ranks, 1, query_count),
        doc_hit_at_3=_hit_at_k(doc_ranks, 3, query_count),
        doc_hit_at_5=_hit_at_k(doc_ranks, 5, query_count),
        doc_hit_at_8=_hit_at_k(doc_ranks, 8, query_count),
        heading_hit_at_1=_hit_at_k(heading_ranks, 1, query_count),
        heading_hit_at_3=_hit_at_k(heading_ranks, 3, query_count),
        heading_hit_at_5=_hit_at_k(heading_ranks, 5, query_count),
        heading_hit_at_8=_hit_at_k(heading_ranks, 8, query_count),
        doc_mrr=_mean_reciprocal_rank(doc_ranks, query_count),
        heading_mrr=_mean_reciprocal_rank(heading_ranks, query_count),
    )


def _hit_at_k(ranks: list[int | None], k: int, query_count: int) -> float:
    if query_count <= 0:
        return 0.0
    return sum(1 for rank in ranks if rank is not None and rank <= k) / query_count


def _mean_reciprocal_rank(ranks: list[int | None], query_count: int) -> float:
    if query_count <= 0:
        return 0.0
    total = 0.0
    for rank in ranks:
        if rank is not None and rank > 0:
            total += 1.0 / rank
    return total / query_count


def _interpret_metrics(
    baseline: AblationMethodMetrics,
    deterministic: AblationMethodMetrics,
    ml: AblationMethodMetrics,
) -> dict[str, Any]:
    deterministic_doc_gain = deterministic.doc_hit_at_3 - baseline.doc_hit_at_3
    deterministic_heading_gain = deterministic.heading_hit_at_3 - baseline.heading_hit_at_3
    ml_doc_gain = ml.doc_hit_at_3 - deterministic.doc_hit_at_3
    ml_heading_gain = ml.heading_hit_at_3 - deterministic.heading_hit_at_3
    return {
        "deterministic_doc_hit_at_3_gain_over_baseline": round(deterministic_doc_gain, 4),
        "deterministic_heading_hit_at_3_gain_over_baseline": round(deterministic_heading_gain, 4),
        "ml_doc_hit_at_3_gain_over_deterministic": round(ml_doc_gain, 4),
        "ml_heading_hit_at_3_gain_over_deterministic": round(ml_heading_gain, 4),
        "deterministic_preserves_or_improves_doc_coverage": deterministic.doc_hit_at_3 >= baseline.doc_hit_at_3,
        "ml_improves_heading_rank_over_deterministic": ml.heading_hit_at_3 > deterministic.heading_hit_at_3,
    }
