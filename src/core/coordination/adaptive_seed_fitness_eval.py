"""Side evaluation for query-conditioned deterministic seed-fitness scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation import SemanticObject

from .project_documents import DEFAULT_PROJECT_DOCUMENT_PROFILE, ingest_project_documents
from .project_query_lens_selector import (
    AUTO_LENS_PROFILE,
    ProjectQueryLensSelection,
    manual_project_query_lens_selection,
    select_project_query_lens,
)
from .retrieval_outside_eval import RetrievalEvalQuery, default_retrieval_eval_queries
from .seed_fitness import (
    SeedFitnessPolicy,
    SeedSearchCandidate,
    _candidate_for_object,
    tokenize_seed_query,
)

ADAPTIVE_SEED_FITNESS_EVAL_VERSION = "v1"


@dataclass(frozen=True)
class SeedFitnessWeightProfile:
    """Multipliers for deterministic seed-fitness score components."""

    weights: dict[str, float]

    def multiplier_for(self, component: str) -> float:
        return self.weights.get(component, 1.0)

    def to_dict(self) -> dict[str, float]:
        return {key: round(value, 4) for key, value in self.weights.items()}


SEED_FITNESS_WEIGHT_PROFILES: dict[str, SeedFitnessWeightProfile] = {
    "balanced": SeedFitnessWeightProfile(
        {
            "document_role_fit": 1.15,
            "heading_section_affinity": 1.1,
            "continuation_marker_proximity": 1.15,
            "operator_command_proximity": 1.1,
            "expected_source_fit": 1.05,
        }
    ),
    "semantic_heavy": SeedFitnessWeightProfile(
        {
            "exact_content": 0.85,
            "exact_heading": 0.9,
            "exact_source": 0.75,
            "content_terms": 1.2,
            "heading_terms": 1.35,
            "source_terms": 0.75,
            "document_role_fit": 0.85,
            "heading_section_affinity": 1.15,
            "operator_command_proximity": 0.9,
        }
    ),
    "structure_heavy": SeedFitnessWeightProfile(
        {
            "exact_content": 0.8,
            "content_terms": 0.95,
            "heading_terms": 1.4,
            "source_terms": 0.85,
            "heading_kind": 1.25,
            "heading_section_affinity": 1.35,
            "document_role_fit": 1.05,
        }
    ),
    "provenance_heavy": SeedFitnessWeightProfile(
        {
            "exact_source": 1.4,
            "source_terms": 1.75,
            "expected_source_fit": 1.5,
            "document_role_fit": 1.25,
            "heading_section_affinity": 0.95,
        }
    ),
    "exact_match_heavy": SeedFitnessWeightProfile(
        {
            "exact_content": 1.35,
            "exact_heading": 1.25,
            "exact_source": 1.2,
            "content_terms": 1.05,
            "heading_terms": 1.0,
            "source_terms": 1.15,
            "brevity": 0.85,
            "heading_kind": 0.9,
            "operator_command_proximity": 1.25,
            "heading_section_affinity": 1.15,
        }
    ),
    "neighborhood_support_heavy": SeedFitnessWeightProfile(
        {
            "document_role_fit": 1.15,
            "heading_section_affinity": 1.1,
            "continuation_marker_proximity": 1.45,
            "operator_command_proximity": 1.15,
            "expected_source_fit": 1.05,
        }
    ),
}

_STRUCTURAL_KEYS = (
    "expected_source_fit",
    "document_role_fit",
    "heading_section_affinity",
    "continuation_marker_proximity",
    "operator_command_proximity",
)


@dataclass(frozen=True)
class AdaptiveSeedFitnessMethodResult:
    """Per-query top result and hit ranks for one scoring method."""

    top_source_ref: str
    top_heading_trail: tuple[str, ...]
    doc_hit_rank: int | None
    heading_hit_rank: int | None
    lens_selection: ProjectQueryLensSelection | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "top_source_ref": self.top_source_ref,
            "top_heading_trail": list(self.top_heading_trail),
            "doc_hit_rank": self.doc_hit_rank,
            "heading_hit_rank": self.heading_hit_rank,
        }
        if self.lens_selection is not None:
            data["lens_selection"] = self.lens_selection.to_dict()
        return data


@dataclass(frozen=True)
class AdaptiveSeedFitnessMetrics:
    """Aggregate metrics for one deterministic scoring variant."""

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
class AdaptiveSeedFitnessComparisonRow:
    """One labeled query compared across fixed and adaptive deterministic scoring."""

    query: RetrievalEvalQuery
    baseline: AdaptiveSeedFitnessMethodResult
    auto: AdaptiveSeedFitnessMethodResult
    lens_results: dict[str, AdaptiveSeedFitnessMethodResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": {
                "query_id": self.query.query_id,
                "query": self.query.query,
                "acceptable_source_suffixes": list(self.query.acceptable_source_suffixes),
                "preferred_heading_terms": list(self.query.preferred_heading_terms),
            },
            "baseline": self.baseline.to_dict(),
            "auto": self.auto.to_dict(),
            "lens_results": {name: result.to_dict() for name, result in self.lens_results.items()},
        }


@dataclass(frozen=True)
class AdaptiveSeedFitnessEvalRun:
    """Full side-eval artifact for query-conditioned deterministic scoring."""

    version: str
    project_root: str
    document_profile: str
    query_count: int
    metrics: dict[str, AdaptiveSeedFitnessMetrics]
    weight_profiles: dict[str, SeedFitnessWeightProfile]
    rows: tuple[AdaptiveSeedFitnessComparisonRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "document_profile": self.document_profile,
            "query_count": self.query_count,
            "metrics": {name: metric.to_dict() for name, metric in self.metrics.items()},
            "weight_profiles": {
                name: profile.to_dict() for name, profile in self.weight_profiles.items()
            },
            "rows": [row.to_dict() for row in self.rows],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_adaptive_seed_fitness_eval_path(project_root: Path | str) -> Path:
    """Return the default artifact path for this side evaluation."""
    return Path(project_root) / "data" / "mcp_inspection" / "adaptive_seed_fitness_eval.json"


def run_adaptive_seed_fitness_eval(
    project_root: Path | str,
    *,
    document_profile: str = DEFAULT_PROJECT_DOCUMENT_PROFILE,
    queries: tuple[RetrievalEvalQuery, ...] = default_retrieval_eval_queries(),
) -> AdaptiveSeedFitnessEvalRun:
    """Compare baseline deterministic seed scoring to query-conditioned weighting."""
    corpus = ingest_project_documents(project_root, document_profile=document_profile)
    cartridge = SemanticCartridge(corpus.cartridge_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects = list(cartridge.all_objects())

    method_doc_ranks: dict[str, list[int | None]] = {"baseline": [], "auto": []}
    method_heading_ranks: dict[str, list[int | None]] = {"baseline": [], "auto": []}
    for lens_name in SEED_FITNESS_WEIGHT_PROFILES:
        method_doc_ranks[lens_name] = []
        method_heading_ranks[lens_name] = []

    rows: list[AdaptiveSeedFitnessComparisonRow] = []
    for query in queries:
        baseline_candidates = _rank_baseline_seed_candidates(objects, query.query)
        baseline_result = _method_result(baseline_candidates, query)
        method_doc_ranks["baseline"].append(baseline_result.doc_hit_rank)
        method_heading_ranks["baseline"].append(baseline_result.heading_hit_rank)

        auto_selection = select_project_query_lens(query.query)
        auto_candidates = _rank_weighted_seed_candidates(
            objects,
            query.query,
            lens_name=auto_selection.selected_lens_profile,
        )
        auto_result = _method_result(auto_candidates, query, lens_selection=auto_selection)
        method_doc_ranks["auto"].append(auto_result.doc_hit_rank)
        method_heading_ranks["auto"].append(auto_result.heading_hit_rank)

        lens_results: dict[str, AdaptiveSeedFitnessMethodResult] = {}
        for lens_name in SEED_FITNESS_WEIGHT_PROFILES:
            candidates = _rank_weighted_seed_candidates(objects, query.query, lens_name=lens_name)
            selection = manual_project_query_lens_selection(lens_name)
            result = _method_result(candidates, query, lens_selection=selection)
            lens_results[lens_name] = result
            method_doc_ranks[lens_name].append(result.doc_hit_rank)
            method_heading_ranks[lens_name].append(result.heading_hit_rank)

        rows.append(
            AdaptiveSeedFitnessComparisonRow(
                query=query,
                baseline=baseline_result,
                auto=auto_result,
                lens_results=lens_results,
            )
        )

    metrics = {
        name: _metrics_from_ranks(method_doc_ranks[name], method_heading_ranks[name], len(queries))
        for name in method_doc_ranks
    }

    return AdaptiveSeedFitnessEvalRun(
        version=ADAPTIVE_SEED_FITNESS_EVAL_VERSION,
        project_root=corpus.project_root,
        document_profile=corpus.document_profile,
        query_count=len(queries),
        metrics=metrics,
        weight_profiles=SEED_FITNESS_WEIGHT_PROFILES,
        rows=tuple(rows),
    )


def save_adaptive_seed_fitness_eval_run(
    run: AdaptiveSeedFitnessEvalRun,
    output_path: Path | str,
) -> Path:
    """Persist the evaluation artifact to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.to_json(), encoding="utf-8")
    return path


def _rank_baseline_seed_candidates(
    objects: list[SemanticObject],
    query_text: str,
    *,
    limit: int = 5,
) -> list[SeedSearchCandidate]:
    terms = tokenize_seed_query(query_text)
    policy = SeedFitnessPolicy(seed_text_hint=query_text, question=query_text)
    ranked = [_candidate_for_object(obj, query_text, terms, policy) for obj in objects]
    candidates = [candidate for candidate in ranked if candidate.score > 0]
    candidates.sort(key=_weighted_candidate_sort_key)
    return candidates[: max(1, limit)]


def _rank_weighted_seed_candidates(
    objects: list[SemanticObject],
    query_text: str,
    *,
    lens_name: str,
    limit: int = 5,
) -> list[SeedSearchCandidate]:
    terms = tokenize_seed_query(query_text)
    policy = SeedFitnessPolicy(seed_text_hint=query_text, question=query_text)
    profile = SEED_FITNESS_WEIGHT_PROFILES[lens_name]
    weighted: list[SeedSearchCandidate] = []
    for obj in objects:
        candidate = _candidate_for_object(obj, query_text, terms, policy)
        if candidate.score <= 0:
            continue
        weighted.append(_weighted_candidate(candidate, profile))
    weighted.sort(key=_weighted_candidate_sort_key)
    return weighted[: max(1, limit)]


def _weighted_candidate(
    candidate: SeedSearchCandidate,
    profile: SeedFitnessWeightProfile,
) -> SeedSearchCandidate:
    weighted_breakdown = {
        key: round(value * profile.multiplier_for(key), 4)
        for key, value in candidate.score_breakdown.items()
        if value > 0
    }
    return SeedSearchCandidate(
        semantic_id=candidate.semantic_id,
        source_ref=candidate.source_ref,
        kind=candidate.kind,
        content_preview=candidate.content_preview,
        score=round(sum(weighted_breakdown.values()), 4),
        matched_terms=candidate.matched_terms,
        block_index=candidate.block_index,
        line_span=candidate.line_span,
        heading_trail=candidate.heading_trail,
        score_breakdown=weighted_breakdown,
    )


def _weighted_candidate_sort_key(candidate: SeedSearchCandidate) -> tuple[float, float, int, str, str]:
    block_index = candidate.block_index if candidate.block_index is not None else 999999
    structural_score = sum(candidate.score_breakdown.get(key, 0.0) for key in _STRUCTURAL_KEYS)
    return (-candidate.score, -structural_score, block_index, candidate.source_ref, candidate.semantic_id)


def _method_result(
    candidates: list[SeedSearchCandidate],
    query: RetrievalEvalQuery,
    *,
    lens_selection: ProjectQueryLensSelection | None = None,
) -> AdaptiveSeedFitnessMethodResult:
    top = candidates[0] if candidates else None
    return AdaptiveSeedFitnessMethodResult(
        top_source_ref=top.source_ref if top else "",
        top_heading_trail=top.heading_trail if top else (),
        doc_hit_rank=_first_doc_hit_rank(candidates, query),
        heading_hit_rank=_first_heading_hit_rank(candidates, query),
        lens_selection=lens_selection,
    )


def _first_doc_hit_rank(candidates: list[SeedSearchCandidate], query: RetrievalEvalQuery) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        if any(candidate.source_ref.endswith(suffix) for suffix in query.acceptable_source_suffixes):
            return index
    return None


def _first_heading_hit_rank(candidates: list[SeedSearchCandidate], query: RetrievalEvalQuery) -> int | None:
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
) -> AdaptiveSeedFitnessMetrics:
    return AdaptiveSeedFitnessMetrics(
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
