"""Scoring fixtures for context projection layer arbitration."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .interaction_spine import PROJECT_QUERY_TOOL_NAME, run_project_query_interaction
from .mcp_inspection_history import McpInspectionHistoryStore
from .mcp_seam import McpUsefulnessReport, McpUsefulnessSignal, evaluate_mcp_usefulness

CONTEXT_PROJECTION_SCORING_VERSION = "v1"


@dataclass(frozen=True)
class ContextProjectionArbitrationFixture:
    """One expected layer-selection fixture for project-query tuning."""

    task_id: str
    query: str
    expected_layer: str
    rationale: str
    limit: int = 3

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "query": self.query,
            "expected_layer": self.expected_layer,
            "rationale": self.rationale,
            "limit": self.limit,
        }


@dataclass(frozen=True)
class ContextProjectionArbitrationScore:
    """Scored result for one layer-arbitration fixture."""

    fixture: ContextProjectionArbitrationFixture
    selected_layer: str
    layer_scores: dict[str, float]
    candidate_counts: dict[str, int]
    selected_evidence: tuple[str, ...]
    signal: McpUsefulnessSignal
    call_id: str

    @property
    def passed(self) -> bool:
        return self.selected_layer == self.fixture.expected_layer

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture": self.fixture.to_dict(),
            "selected_layer": self.selected_layer,
            "expected_layer": self.fixture.expected_layer,
            "passed": self.passed,
            "layer_scores": self.layer_scores,
            "candidate_counts": self.candidate_counts,
            "selected_evidence": list(self.selected_evidence),
            "signal": self.signal.to_dict(),
            "call_id": self.call_id,
        }


@dataclass(frozen=True)
class ContextProjectionArbitrationRun:
    """Aggregate scoring run for query layer arbitration."""

    version: str
    project_root: str
    history_path: str
    elapsed_ms: int
    scores: tuple[ContextProjectionArbitrationScore, ...]
    usefulness_report: McpUsefulnessReport

    @property
    def meets_acceptance(self) -> bool:
        return self.usefulness_report.meets_acceptance and all(score.passed for score in self.scores)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "history_path": self.history_path,
            "elapsed_ms": self.elapsed_ms,
            "scores": [score.to_dict() for score in self.scores],
            "usefulness_report": self.usefulness_report.to_dict(),
            "meets_acceptance": self.meets_acceptance,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_context_projection_score_path(project_root: Path | str) -> Path:
    """Return the project-owned arbitration score artifact path."""
    return Path(project_root) / "data" / "mcp_inspection" / "context_projection_scores.json"


def default_context_projection_arbitration_fixtures() -> tuple[ContextProjectionArbitrationFixture, ...]:
    """Return the first bounded context-rebinding score fixtures."""
    return (
        ContextProjectionArbitrationFixture(
            task_id="english_plain_lookup",
            query="teakettle",
            expected_layer="english_lexical_prior",
            rationale="a plain lexical headword should stay anchored to the English prior",
        ),
        ContextProjectionArbitrationFixture(
            task_id="python_rebinding_lookup",
            query="class object function",
            expected_layer="python_docs_projection",
            rationale="code-shaped terms should rebind through the Python docs layer",
        ),
        ContextProjectionArbitrationFixture(
            task_id="project_doctrine_lookup",
            query="builder constraint contract tranche",
            expected_layer="project_local_docs",
            rationale="project doctrine terms should resolve through local project documents",
        ),
    )


def run_context_projection_arbitration_scoring(
    project_root: Path | str,
    *,
    history_path: Path | str,
    score_path: Path | str | None = None,
    fixtures: tuple[
        ContextProjectionArbitrationFixture, ...
    ] = default_context_projection_arbitration_fixtures(),
) -> ContextProjectionArbitrationRun:
    """Run project-query scoring fixtures and record each call in inspection history."""
    root = Path(project_root).resolve()
    history = McpInspectionHistoryStore(history_path)
    scores: list[ContextProjectionArbitrationScore] = []
    started = time.perf_counter()

    for fixture in fixtures:
        capture = run_project_query_interaction(
            root,
            fixture.query,
            limit=fixture.limit,
            actor="builder",
            source_surface="scoring",
        )
        call = {
            "call_id": capture.capture_id,
            "tool": {
                "tool_name": PROJECT_QUERY_TOOL_NAME,
                "capability_name": capture.capability["name"],
                "title": "Project Query Through Context Layers",
                "readiness": "registration_candidate",
            },
            "status": "ok",
            "capture": capture.to_dict(),
        }
        history.record_call(call)
        frame = capture.response["projection_frame"]
        selected_layer = str(frame.get("selected_layer") or "")
        selected_candidate = frame.get("selected_candidate") or {}
        layer_scores = _layer_scores(frame)
        candidate_counts = _candidate_counts(frame)
        selected_evidence = tuple(str(item) for item in selected_candidate.get("evidence", ()))
        signal = _score_fixture(
            fixture=fixture,
            selected_layer=selected_layer,
            layer_scores=layer_scores,
            candidate_counts=candidate_counts,
            selected_evidence=selected_evidence,
        )
        scores.append(
            ContextProjectionArbitrationScore(
                fixture=fixture,
                selected_layer=selected_layer,
                layer_scores=layer_scores,
                candidate_counts=candidate_counts,
                selected_evidence=selected_evidence,
                signal=signal,
                call_id=capture.capture_id,
            )
        )

    report = evaluate_mcp_usefulness(tuple(score.signal for score in scores))
    run = ContextProjectionArbitrationRun(
        version=CONTEXT_PROJECTION_SCORING_VERSION,
        project_root=str(root),
        history_path=str(history_path),
        elapsed_ms=max(1, int((time.perf_counter() - started) * 1000)),
        scores=tuple(scores),
        usefulness_report=report,
    )
    if score_path is not None:
        output_path = Path(score_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(run.to_json(), encoding="utf-8")
    return run


def _score_fixture(
    *,
    fixture: ContextProjectionArbitrationFixture,
    selected_layer: str,
    layer_scores: dict[str, float],
    candidate_counts: dict[str, int],
    selected_evidence: tuple[str, ...],
) -> McpUsefulnessSignal:
    expected_score = layer_scores.get(fixture.expected_layer, 0.0)
    selected_score = layer_scores.get(selected_layer, 0.0)
    expected_candidates = candidate_counts.get(fixture.expected_layer, 0)
    passed = selected_layer == fixture.expected_layer
    score_delta = round(selected_score - expected_score, 4)
    return McpUsefulnessSignal(
        capability_name=f"context_projection.{fixture.task_id}",
        task_fit=1.0 if passed else 0.2,
        evidence_quality=1.0 if selected_evidence else 0.35,
        actionability=0.9 if passed and expected_candidates > 0 else 0.3,
        friction_reduction=0.9 if passed else 0.3,
        repeatability=1.0,
        notes=(
            f"expected={fixture.expected_layer}; selected={selected_layer}; "
            f"selected_score={selected_score}; expected_score={expected_score}; "
            f"score_delta={score_delta}; candidates={candidate_counts}"
        ),
    )


def _layer_scores(frame: dict[str, Any]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for projection in frame.get("projections", ()):
        layer = projection.get("layer", {})
        name = str(layer.get("name") or "")
        if name:
            scores[name] = float(projection.get("layer_score", 0.0))
    return scores


def _candidate_counts(frame: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for projection in frame.get("projections", ()):
        layer = projection.get("layer", {})
        name = str(layer.get("name") or "")
        if name:
            counts[name] = int(projection.get("candidate_count", 0))
    return counts
