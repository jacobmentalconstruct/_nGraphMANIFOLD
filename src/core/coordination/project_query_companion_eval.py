"""Side evaluation for baseline seed selection plus bag-as-companion evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
from .project_query_lens_selector import ProjectQueryLensSelection
from .retrieval_outside_eval import RetrievalEvalQuery, default_retrieval_eval_queries
from .seed_fitness import SeedFitnessPolicy, SeedSearchCandidate, rank_seed_candidates

PROJECT_QUERY_COMPANION_EVAL_VERSION = "v1"


@dataclass(frozen=True)
class CompanionEvidenceItem:
    """One item in the combined baseline-plus-bag evidence packet."""

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
class CompanionEvalMethodMetrics:
    """Coverage metrics for a method that returns a ranked evidence packet."""

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
class ProjectQueryCompanionEvalRow:
    """One query judged as baseline alone versus baseline plus companion bag."""

    query: RetrievalEvalQuery
    baseline_top: SeedSearchCandidate | None
    baseline_hit_rank: int | None
    baseline_heading_hit_rank: int | None
    companion_doc_hit_rank: int | None
    companion_heading_hit_rank: int | None
    auto_selection: ProjectQueryLensSelection
    combined_evidence: tuple[CompanionEvidenceItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": {
                "query_id": self.query.query_id,
                "query": self.query.query,
                "acceptable_source_suffixes": list(self.query.acceptable_source_suffixes),
                "preferred_heading_terms": list(self.query.preferred_heading_terms),
            },
            "baseline_top": self.baseline_top.to_dict() if self.baseline_top else None,
            "baseline_hit_rank": self.baseline_hit_rank,
            "baseline_heading_hit_rank": self.baseline_heading_hit_rank,
            "companion_doc_hit_rank": self.companion_doc_hit_rank,
            "companion_heading_hit_rank": self.companion_heading_hit_rank,
            "auto_selection": self.auto_selection.to_dict(),
            "combined_evidence": [item.to_dict() for item in self.combined_evidence],
        }


@dataclass(frozen=True)
class ProjectQueryCompanionEvalRun:
    """Full evaluation artifact for bag-as-companion evidence support."""

    version: str
    project_root: str
    document_profile: str
    query_count: int
    baseline_metrics: CompanionEvalMethodMetrics
    companion_metrics: CompanionEvalMethodMetrics
    rows: tuple[ProjectQueryCompanionEvalRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "document_profile": self.document_profile,
            "query_count": self.query_count,
            "baseline_metrics": self.baseline_metrics.to_dict(),
            "companion_metrics": self.companion_metrics.to_dict(),
            "rows": [row.to_dict() for row in self.rows],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_project_query_companion_eval_path(project_root: Path | str) -> Path:
    """Return the default artifact path for the companion evaluation."""
    return Path(project_root) / "data" / "mcp_inspection" / "project_query_companion_eval.json"


def run_project_query_companion_eval(
    project_root: Path | str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    queries: tuple[RetrievalEvalQuery, ...] = default_retrieval_eval_queries(),
    max_seeds: int = DEFAULT_MAX_SEEDS,
    radius: int = DEFAULT_RADIUS,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_items: int = DEFAULT_MAX_ITEMS,
    char_budget: int = DEFAULT_CHAR_BUDGET,
) -> ProjectQueryCompanionEvalRun:
    """Evaluate whether the auto bag improves support coverage around baseline seeds."""
    workspace = build_project_query_lens_bag_workspace(
        project_root,
        document_profile=document_profile,
    )

    baseline_doc_ranks: list[int | None] = []
    baseline_heading_ranks: list[int | None] = []
    companion_doc_ranks: list[int | None] = []
    companion_heading_ranks: list[int | None] = []
    rows: list[ProjectQueryCompanionEvalRow] = []

    for query in queries:
        baseline_candidates = list(
            rank_seed_candidates(
                list(workspace.objects),
                query.query,
                limit=5,
                policy=SeedFitnessPolicy(seed_text_hint=query.query, question=query.query),
            )
        )
        baseline_top = baseline_candidates[0] if baseline_candidates else None
        baseline_doc_rank = _baseline_top_doc_rank(baseline_top, query)
        baseline_heading_rank = _baseline_top_heading_rank(baseline_top, query)

        companion_run = run_project_query_lens_bag(
            workspace.project_root,
            query.query,
            document_profile=document_profile,
            lens_profile="auto",
            max_seeds=max_seeds,
            radius=radius,
            max_nodes=max_nodes,
            max_items=max_items,
            char_budget=char_budget,
            workspace=workspace,
        )
        combined_evidence = _combined_evidence_packet(baseline_top, companion_run.bag_items)
        companion_doc_rank = _first_doc_hit_rank(combined_evidence, query)
        companion_heading_rank = _first_heading_hit_rank(combined_evidence, query)

        baseline_doc_ranks.append(baseline_doc_rank)
        baseline_heading_ranks.append(baseline_heading_rank)
        companion_doc_ranks.append(companion_doc_rank)
        companion_heading_ranks.append(companion_heading_rank)

        rows.append(
            ProjectQueryCompanionEvalRow(
                query=query,
                baseline_top=baseline_top,
                baseline_hit_rank=baseline_doc_rank,
                baseline_heading_hit_rank=baseline_heading_rank,
                companion_doc_hit_rank=companion_doc_rank,
                companion_heading_hit_rank=companion_heading_rank,
                auto_selection=companion_run.lens_selection,
                combined_evidence=combined_evidence,
            )
        )

    return ProjectQueryCompanionEvalRun(
        version=PROJECT_QUERY_COMPANION_EVAL_VERSION,
        project_root=workspace.project_root,
        document_profile=workspace.document_profile,
        query_count=len(queries),
        baseline_metrics=_metrics_from_ranks(baseline_doc_ranks, baseline_heading_ranks, len(queries)),
        companion_metrics=_metrics_from_ranks(companion_doc_ranks, companion_heading_ranks, len(queries)),
        rows=tuple(rows),
    )


def save_project_query_companion_eval_run(
    run: ProjectQueryCompanionEvalRun,
    output_path: Path | str,
) -> Path:
    """Persist the companion evaluation artifact to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.to_json(), encoding="utf-8")
    return path


def _combined_evidence_packet(
    baseline_top: SeedSearchCandidate | None,
    bag_items: tuple[Any, ...],
) -> tuple[CompanionEvidenceItem, ...]:
    seen: set[tuple[str, tuple[str, ...], str]] = set()
    combined: list[CompanionEvidenceItem] = []

    if baseline_top is not None:
        item = CompanionEvidenceItem(
            role="baseline_seed",
            source_ref=baseline_top.source_ref,
            heading_trail=baseline_top.heading_trail,
            kind=baseline_top.kind,
        )
        combined.append(item)
        seen.add((item.source_ref, item.heading_trail, item.kind))

    for bag_item in bag_items:
        key = (bag_item.source_ref, bag_item.heading_trail, bag_item.kind)
        if key in seen:
            continue
        seen.add(key)
        combined.append(
            CompanionEvidenceItem(
                role=f"bag_{bag_item.source_role}",
                source_ref=bag_item.source_ref,
                heading_trail=bag_item.heading_trail,
                kind=bag_item.kind,
            )
        )
    return tuple(combined)


def _baseline_top_doc_rank(
    baseline_top: SeedSearchCandidate | None,
    query: RetrievalEvalQuery,
) -> int | None:
    if baseline_top is None:
        return None
    if any(baseline_top.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
        return 1
    return None


def _baseline_top_heading_rank(
    baseline_top: SeedSearchCandidate | None,
    query: RetrievalEvalQuery,
) -> int | None:
    if baseline_top is None:
        return None
    if not any(baseline_top.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
        return None
    if not query.preferred_heading_terms:
        return 1
    joined_heading = " > ".join(baseline_top.heading_trail).lower()
    if any(term in joined_heading for term in query.preferred_heading_terms):
        return 1
    return None


def _first_doc_hit_rank(
    candidates: tuple[CompanionEvidenceItem, ...],
    query: RetrievalEvalQuery,
) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        if any(candidate.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            return index
    return None


def _first_heading_hit_rank(
    candidates: tuple[CompanionEvidenceItem, ...],
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
) -> CompanionEvalMethodMetrics:
    return CompanionEvalMethodMetrics(
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
