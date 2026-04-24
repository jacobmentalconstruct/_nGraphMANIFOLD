"""Deterministic seed-fitness scoring for project-document traversal starts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.core.representation import SemanticObject

SEED_FITNESS_VERSION = "v1"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class SeedFitnessPolicy:
    """Optional task-aware constraints for project-document seed selection."""

    task_id: str = ""
    question: str = ""
    expected_source_suffix: str = ""
    seed_text_hint: str = ""


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
    score_breakdown: dict[str, float]

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
            "score_breakdown": self.score_breakdown,
        }


def rank_seed_candidates(
    objects: list[SemanticObject],
    query: str,
    *,
    limit: int = 5,
    policy: SeedFitnessPolicy | None = None,
) -> list[SeedSearchCandidate]:
    """Rank semantic objects with deterministic, inspectable seed-fitness scoring."""
    terms = tokenize_seed_query(query)
    if not terms:
        raise ValueError("Seed search query must contain at least one alphanumeric term")
    active_policy = policy or SeedFitnessPolicy(seed_text_hint=query)
    ranked = [_candidate_for_object(obj, query, terms, active_policy) for obj in objects]
    candidates = [candidate for candidate in ranked if candidate.score > 0]
    candidates.sort(key=_candidate_sort_key)
    return candidates[: max(1, limit)]


def tokenize_seed_query(query: str) -> tuple[str, ...]:
    """Tokenize a seed query for deterministic matching."""
    return tuple(dict.fromkeys(token.lower() for token in TOKEN_PATTERN.findall(query)))


def _candidate_for_object(
    obj: SemanticObject,
    query: str,
    terms: tuple[str, ...],
    policy: SeedFitnessPolicy,
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
    breakdown: dict[str, float] = {}
    _add_score(breakdown, "exact_content", 5.0 if normalized_query and normalized_query in normalized_content else 0.0)
    _add_score(breakdown, "exact_heading", 3.0 if normalized_query and normalized_query in normalized_heading else 0.0)
    _add_score(breakdown, "exact_source", 1.0 if normalized_query and normalized_query in normalized_source else 0.0)
    _add_score(breakdown, "content_terms", sum(1.0 for term in terms if term in normalized_content))
    _add_score(breakdown, "heading_terms", sum(0.9 for term in terms if term in normalized_heading))
    _add_score(breakdown, "source_terms", sum(0.25 for term in terms if term in normalized_source))
    _add_score(breakdown, "heading_kind", 0.25 if obj.kind == "heading" else 0.0)
    _add_score(breakdown, "brevity", max(0.0, 0.25 - min(len(obj.content), 1000) / 4000))
    _add_policy_scores(
        breakdown,
        policy=policy,
        normalized_content=normalized_content,
        normalized_source=normalized_source,
        normalized_heading=normalized_heading,
    )

    return SeedSearchCandidate(
        semantic_id=obj.semantic_id,
        source_ref=source_ref,
        kind=obj.kind,
        content_preview=_preview(obj.content),
        score=round(sum(breakdown.values()), 4),
        matched_terms=matched_terms,
        block_index=int(block_index) if isinstance(block_index, int) else None,
        line_span=line_span,
        heading_trail=heading_trail,
        score_breakdown={key: round(value, 4) for key, value in breakdown.items() if value > 0},
    )


def _add_policy_scores(
    breakdown: dict[str, float],
    *,
    policy: SeedFitnessPolicy,
    normalized_content: str,
    normalized_source: str,
    normalized_heading: str,
) -> None:
    if not any((policy.task_id, policy.question, policy.expected_source_suffix, policy.seed_text_hint)):
        return
    task_text = " ".join((policy.task_id, policy.question, policy.seed_text_hint)).lower()
    source_role = _document_role(normalized_source)
    expected_suffix = policy.expected_source_suffix.lower().replace("\\", "/")
    source_matches_expected = bool(expected_suffix and normalized_source.endswith(expected_suffix))

    if source_matches_expected:
        _add_score(breakdown, "expected_source_fit", 4.0)

    if _is_builder_continuation_task(task_text):
        if source_role == "state_tracking":
            _add_score(breakdown, "document_role_fit", 3.0)
        if any(marker in normalized_heading for marker in ("current park point", "latest verification", "next park target")):
            _add_score(breakdown, "heading_section_affinity", 2.0)
        if any(marker in normalized_content for marker in ("tranche:", "next tranche", "next park target", "current park point")):
            _add_score(breakdown, "continuation_marker_proximity", 2.0)

    if _is_operator_command_task(task_text):
        if source_role == "operator_guide":
            _add_score(breakdown, "document_role_fit", 3.0)
        if any(marker in normalized_heading for marker in ("run", "runtime commands", "project runtime inspection commands")):
            _add_score(breakdown, "heading_section_affinity", 2.0)
        if "python -m src.app" in normalized_content:
            _add_score(breakdown, "operator_command_proximity", 2.0)

    if _is_mcp_surface_task(task_text) and source_role == "mcp_surface":
        _add_score(breakdown, "document_role_fit", 3.0)

    if _is_plan_task(task_text) and source_role == "plan":
        _add_score(breakdown, "document_role_fit", 3.0)


def _is_builder_continuation_task(task_text: str) -> bool:
    return any(term in task_text for term in ("current", "park", "tranche", "next implementation", "continuation"))


def _is_operator_command_task(task_text: str) -> bool:
    return any(term in task_text for term in ("command", "operator", "history", "persisted mcp"))


def _is_mcp_surface_task(task_text: str) -> bool:
    return any(term in task_text for term in ("mcp-facing", "mcp surface", "tool registration", "seam"))


def _is_plan_task(task_text: str) -> bool:
    return any(term in task_text for term in ("plan", "post-prototype", "happen next"))


def _document_role(normalized_source: str) -> str:
    if normalized_source.endswith("project_status.md"):
        return "state_tracking"
    if normalized_source.endswith("readme.md"):
        return "operator_guide"
    if normalized_source.endswith("mcp_seam.md"):
        return "mcp_surface"
    if normalized_source.endswith("strangler_plan.md"):
        return "plan"
    return "project_document"


def _candidate_sort_key(candidate: SeedSearchCandidate) -> tuple[float, float, int, str, str]:
    block_index = candidate.block_index if candidate.block_index is not None else 999999
    structural_score = (
        candidate.score_breakdown.get("expected_source_fit", 0.0)
        + candidate.score_breakdown.get("document_role_fit", 0.0)
        + candidate.score_breakdown.get("heading_section_affinity", 0.0)
        + candidate.score_breakdown.get("continuation_marker_proximity", 0.0)
        + candidate.score_breakdown.get("operator_command_proximity", 0.0)
    )
    return (-candidate.score, -structural_score, block_index, candidate.source_ref, candidate.semantic_id)


def _add_score(breakdown: dict[str, float], key: str, value: float) -> None:
    if value <= 0:
        return
    breakdown[key] = breakdown.get(key, 0.0) + value


def _preview(content: str, limit: int = 220) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."
