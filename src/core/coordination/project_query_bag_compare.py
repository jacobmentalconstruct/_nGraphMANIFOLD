"""Side-by-side comparison runner for baseline seed scoring vs lens bags."""

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
    LENS_PROFILE_NAMES,
    ProjectQueryLensBagWorkspace,
    build_project_query_lens_bag_workspace,
    run_project_query_lens_bag,
)
from .project_query_lens_selector import ProjectQueryLensSelection
from .retrieval_outside_eval import RetrievalEvalQuery, default_retrieval_eval_queries
from .seed_fitness import SeedFitnessPolicy, rank_seed_candidates

PROJECT_QUERY_BAG_COMPARE_VERSION = "v2"


@dataclass(frozen=True)
class ComparisonMethodMetrics:
    """Aggregate hit-rate metrics for one comparison method."""

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
class ComparisonMethodResult:
    """Per-query outcome for one method."""

    top_source_ref: str
    top_heading_trail: tuple[str, ...]
    doc_hit_rank: int | None
    heading_hit_rank: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "top_source_ref": self.top_source_ref,
            "top_heading_trail": list(self.top_heading_trail),
            "doc_hit_rank": self.doc_hit_rank,
            "heading_hit_rank": self.heading_hit_rank,
        }


@dataclass(frozen=True)
class ProjectQueryBagComparisonRow:
    """One query compared across baseline and all bag lenses."""

    query: RetrievalEvalQuery
    baseline: ComparisonMethodResult
    auto_result: ComparisonMethodResult
    auto_selection: ProjectQueryLensSelection
    lens_results: dict[str, ComparisonMethodResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": {
                "query_id": self.query.query_id,
                "query": self.query.query,
                "acceptable_source_suffixes": list(self.query.acceptable_source_suffixes),
                "preferred_heading_terms": list(self.query.preferred_heading_terms),
            },
            "baseline": self.baseline.to_dict(),
            "auto_result": self.auto_result.to_dict(),
            "auto_selection": self.auto_selection.to_dict(),
            "lens_results": {
                name: result.to_dict()
                for name, result in self.lens_results.items()
            },
        }


@dataclass(frozen=True)
class ProjectQueryBagComparisonRun:
    """Full comparison artifact across the labeled query set."""

    version: str
    project_root: str
    document_profile: str
    query_count: int
    lens_profiles: tuple[str, ...]
    metrics: dict[str, ComparisonMethodMetrics]
    rows: tuple[ProjectQueryBagComparisonRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "document_profile": self.document_profile,
            "query_count": self.query_count,
            "lens_profiles": list(self.lens_profiles),
            "metrics": {
                name: metric.to_dict()
                for name, metric in self.metrics.items()
            },
            "rows": [row.to_dict() for row in self.rows],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_project_query_bag_compare_path(project_root: Path | str) -> Path:
    """Return the default comparison artifact path."""
    return Path(project_root) / "data" / "mcp_inspection" / "project_query_bag_compare.json"


def run_project_query_bag_comparison(
    project_root: Path | str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    queries: tuple[RetrievalEvalQuery, ...] = default_retrieval_eval_queries(),
    lens_profiles: tuple[str, ...] = LENS_PROFILE_NAMES,
    max_seeds: int = DEFAULT_MAX_SEEDS,
    radius: int = DEFAULT_RADIUS,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_items: int = DEFAULT_MAX_ITEMS,
    char_budget: int = DEFAULT_CHAR_BUDGET,
) -> ProjectQueryBagComparisonRun:
    """Run a side-by-side comparison over the labeled query set."""
    workspace = build_project_query_lens_bag_workspace(
        project_root,
        document_profile=document_profile,
    )
    rows: list[ProjectQueryBagComparisonRow] = []
    method_doc_ranks: dict[str, list[int | None]] = {"baseline": [], "auto": []}
    method_heading_ranks: dict[str, list[int | None]] = {"baseline": [], "auto": []}
    for lens_profile in lens_profiles:
        method_doc_ranks[lens_profile] = []
        method_heading_ranks[lens_profile] = []

    for query in queries:
        baseline_candidates = list(
            rank_seed_candidates(
                list(workspace.objects),
                query.query,
                limit=5,
                policy=SeedFitnessPolicy(seed_text_hint=query.query, question=query.query),
            )
        )
        baseline_result = ComparisonMethodResult(
            top_source_ref=baseline_candidates[0].source_ref if baseline_candidates else "",
            top_heading_trail=baseline_candidates[0].heading_trail if baseline_candidates else (),
            doc_hit_rank=_first_doc_hit_rank(
                [
                    {
                        "source_ref": candidate.source_ref,
                        "heading_trail": candidate.heading_trail,
                    }
                    for candidate in baseline_candidates
                ],
                query,
            ),
            heading_hit_rank=_first_heading_hit_rank(
                [
                    {
                        "source_ref": candidate.source_ref,
                        "heading_trail": candidate.heading_trail,
                    }
                    for candidate in baseline_candidates
                ],
                query,
            ),
        )
        method_doc_ranks["baseline"].append(baseline_result.doc_hit_rank)
        method_heading_ranks["baseline"].append(baseline_result.heading_hit_rank)

        auto_run = run_project_query_lens_bag(
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
        auto_bag_items = list(auto_run.bag_items)
        auto_result = ComparisonMethodResult(
            top_source_ref=auto_bag_items[0].source_ref if auto_bag_items else "",
            top_heading_trail=auto_bag_items[0].heading_trail if auto_bag_items else (),
            doc_hit_rank=_first_doc_hit_rank(
                [
                    {
                        "source_ref": item.source_ref,
                        "heading_trail": item.heading_trail,
                    }
                    for item in auto_bag_items
                ],
                query,
            ),
            heading_hit_rank=_first_heading_hit_rank(
                [
                    {
                        "source_ref": item.source_ref,
                        "heading_trail": item.heading_trail,
                    }
                    for item in auto_bag_items
                ],
                query,
            ),
        )
        method_doc_ranks["auto"].append(auto_result.doc_hit_rank)
        method_heading_ranks["auto"].append(auto_result.heading_hit_rank)

        lens_results: dict[str, ComparisonMethodResult] = {}
        for lens_profile in lens_profiles:
            run = run_project_query_lens_bag(
                workspace.project_root,
                query.query,
                document_profile=document_profile,
                lens_profile=lens_profile,
                max_seeds=max_seeds,
                radius=radius,
                max_nodes=max_nodes,
                max_items=max_items,
                char_budget=char_budget,
                workspace=workspace,
            )
            bag_items = list(run.bag_items)
            result = ComparisonMethodResult(
                top_source_ref=bag_items[0].source_ref if bag_items else "",
                top_heading_trail=bag_items[0].heading_trail if bag_items else (),
                doc_hit_rank=_first_doc_hit_rank(
                    [
                        {
                            "source_ref": item.source_ref,
                            "heading_trail": item.heading_trail,
                        }
                        for item in bag_items
                    ],
                    query,
                ),
                heading_hit_rank=_first_heading_hit_rank(
                    [
                        {
                            "source_ref": item.source_ref,
                            "heading_trail": item.heading_trail,
                        }
                        for item in bag_items
                    ],
                    query,
                ),
            )
            lens_results[lens_profile] = result
            method_doc_ranks[lens_profile].append(result.doc_hit_rank)
            method_heading_ranks[lens_profile].append(result.heading_hit_rank)

        rows.append(
            ProjectQueryBagComparisonRow(
                query=query,
                baseline=baseline_result,
                auto_result=auto_result,
                auto_selection=auto_run.lens_selection,
                lens_results=lens_results,
            )
        )

    metrics = {
        method: _metrics_from_ranks(
            method_doc_ranks[method],
            method_heading_ranks[method],
            len(queries),
        )
        for method in method_doc_ranks
    }

    return ProjectQueryBagComparisonRun(
        version=PROJECT_QUERY_BAG_COMPARE_VERSION,
        project_root=workspace.project_root,
        document_profile=workspace.document_profile,
        query_count=len(queries),
        lens_profiles=lens_profiles,
        metrics=metrics,
        rows=tuple(rows),
    )


def save_project_query_bag_comparison_run(
    run: ProjectQueryBagComparisonRun,
    output_path: Path | str,
) -> Path:
    """Persist the comparison artifact to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.to_json(), encoding="utf-8")
    return path


def _first_doc_hit_rank(
    candidates: list[dict[str, Any]],
    query: RetrievalEvalQuery,
) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        source_ref = str(candidate.get("source_ref") or "")
        if any(source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            return index
    return None


def _first_heading_hit_rank(
    candidates: list[dict[str, Any]],
    query: RetrievalEvalQuery,
) -> int | None:
    if not query.preferred_heading_terms:
        return _first_doc_hit_rank(candidates, query)
    for index, candidate in enumerate(candidates, start=1):
        source_ref = str(candidate.get("source_ref") or "")
        if not any(source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            continue
        joined_heading = " > ".join(str(item) for item in candidate.get("heading_trail", ())).lower()
        if any(term in joined_heading for term in query.preferred_heading_terms):
            return index
    return None


def _metrics_from_ranks(
    doc_ranks: list[int | None],
    heading_ranks: list[int | None],
    query_count: int,
) -> ComparisonMethodMetrics:
    return ComparisonMethodMetrics(
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
