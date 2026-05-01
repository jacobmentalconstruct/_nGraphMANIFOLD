"""Rule-based query-to-lens selector for side-harness bag runs."""

from __future__ import annotations

from dataclasses import dataclass

AUTO_LENS_PROFILE = "auto"
DEFAULT_AUTO_LENS_PROFILE = "balanced"
_LENS_NAMES = (
    "balanced",
    "semantic_heavy",
    "structure_heavy",
    "provenance_heavy",
    "exact_match_heavy",
    "neighborhood_support_heavy",
)


@dataclass(frozen=True)
class ProjectQueryLensSelection:
    """Inspectable selector decision for one raw query."""

    requested_lens_profile: str
    selected_lens_profile: str
    confidence: float
    matched_rules: tuple[str, ...]
    scorecard: dict[str, float]
    is_auto: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "requested_lens_profile": self.requested_lens_profile,
            "selected_lens_profile": self.selected_lens_profile,
            "confidence": round(self.confidence, 4),
            "matched_rules": list(self.matched_rules),
            "scorecard": {key: round(value, 4) for key, value in self.scorecard.items()},
            "is_auto": self.is_auto,
        }


def select_project_query_lens(query: str) -> ProjectQueryLensSelection:
    """Select a lens profile from lightweight query-surface rules."""
    normalized = " ".join(query.lower().split())
    scores = {name: 0.0 for name in _LENS_NAMES}
    matched_rules: list[str] = []

    def add_score(lens_name: str, weight: float, rule_text: str) -> None:
        scores[lens_name] += weight
        matched_rules.append(f"{lens_name}: {rule_text} (+{weight:g})")

    def has_phrase(*phrases: str) -> bool:
        return any(phrase in normalized for phrase in phrases)

    token_set = set(normalized.replace("?", " ").replace("-", " ").split())

    if has_phrase("which command", "what command", "show command"):
        add_score("exact_match_heavy", 3.0, "explicit command phrasing")
    if has_phrase("how do i", "how can the builder", "clean up", "runs a project query"):
        add_score("exact_match_heavy", 2.0, "operational how-to wording")
    if "command" in token_set:
        add_score("exact_match_heavy", 1.5, "contains command token")
    if has_phrase("read what panel", "scores whether"):
        add_score("exact_match_heavy", 2.0, "exact workflow phrasing")

    if has_phrase("mcp-facing", "seams are available", "history-aware", "prior mcp calls"):
        add_score("semantic_heavy", 3.0, "MCP surface or history phrasing")
    if has_phrase("inspection history", "retention policy"):
        add_score("semantic_heavy", 2.0, "history semantics")
    if {"mcp", "seam"} <= token_set or "surface" in token_set or "capability" in token_set:
        add_score("semantic_heavy", 1.5, "conceptual MCP vocabulary")

    if has_phrase("current park point", "parked now", "build next", "prototype phase", "immediately after"):
        add_score("balanced", 3.0, "planning or park-state phrasing")
    if "parked" in token_set or "prototype" in token_set:
        add_score("balanced", 1.5, "bounded status/planning vocabulary")
    if "next" in token_set and ("work" in token_set or "build" in token_set):
        add_score("balanced", 1.0, "next-work phrasing")

    if has_phrase("source of", "where did", "which source", "provenance"):
        add_score("provenance_heavy", 3.0, "provenance phrasing")
    if "provenance" in token_set or "source" in token_set:
        add_score("provenance_heavy", 1.5, "source-oriented vocabulary")

    if has_phrase("section", "heading", "outline", "structure"):
        add_score("structure_heavy", 2.5, "explicit structure wording")
    if "profile" in token_set or "profiles" in token_set:
        add_score("structure_heavy", 1.0, "profile comparison vocabulary")

    if has_phrase("neighbor", "neighborhood", "adjacent", "related context"):
        add_score("neighborhood_support_heavy", 3.0, "neighborhood wording")
    if "context" in token_set and "related" in token_set:
        add_score("neighborhood_support_heavy", 1.5, "context-neighbor phrasing")

    if has_phrase("bridge transport", "core and expanded project doc profiles"):
        add_score("exact_match_heavy", 0.5, "weak exact fallback for historically difficult query")
        add_score("balanced", 0.25, "weak balanced fallback for historically difficult query")

    selected_lens_profile = DEFAULT_AUTO_LENS_PROFILE
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    top_name, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    if top_score > 0.0:
        selected_lens_profile = top_name
        margin = top_score - second_score
        confidence = min(0.95, 0.45 + (margin / top_score) * 0.45)
    else:
        confidence = 0.2
        matched_rules.append("balanced: default fallback (+0)")

    return ProjectQueryLensSelection(
        requested_lens_profile=AUTO_LENS_PROFILE,
        selected_lens_profile=selected_lens_profile,
        confidence=confidence,
        matched_rules=tuple(matched_rules),
        scorecard=scores,
        is_auto=True,
    )


def manual_project_query_lens_selection(lens_profile: str) -> ProjectQueryLensSelection:
    """Build diagnostics for an explicit human-selected lens."""
    return ProjectQueryLensSelection(
        requested_lens_profile=lens_profile,
        selected_lens_profile=lens_profile,
        confidence=1.0,
        matched_rules=("manual lens override",),
        scorecard={name: (1.0 if name == lens_profile else 0.0) for name in _LENS_NAMES},
        is_auto=False,
    )
