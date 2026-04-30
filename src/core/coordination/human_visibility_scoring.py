"""Scored human-facing inspection usefulness fixtures."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .builder_task_scoring import default_builder_task_score_path
from .context_projection_scoring import default_context_projection_score_path
from .host_workspace import (
    HOST_COCKPIT_TOOL_NAME,
    HOST_HISTORY_VIEW_TOOL_NAME,
    HOST_PROMOTE_CALL_TOOL_NAME,
    HOST_READ_PANELS_TOOL_NAME,
    HOST_STATUS_TOOL_NAME,
    HOST_STREAM_TOOL_NAME,
    HOST_TOOLS_TOOL_NAME,
    HostDispatchResult,
    SharedHostState,
    create_host_command_envelope,
    default_host_state,
    dispatch_host_command,
    read_score_artifacts,
)
from .interaction_spine import PROJECT_QUERY_TOOL_NAME
from .mcp_seam import McpUsefulnessReport, McpUsefulnessSignal, evaluate_mcp_usefulness
from .mcp_tool_registry import TRAVERSAL_TOOL_NAME

HUMAN_VISIBILITY_SCORING_VERSION = "v1"


@dataclass(frozen=True)
class HumanVisibilityFixture:
    """One precommitted human-facing visibility expectation."""

    task_id: str
    purpose: str
    expected_surfaces: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "purpose": self.purpose,
            "expected_surfaces": list(self.expected_surfaces),
        }


@dataclass(frozen=True)
class HumanVisibilityScore:
    """Scored result for one human-facing visibility fixture."""

    fixture: HumanVisibilityFixture
    evidence: dict[str, bool]
    signal: McpUsefulnessSignal
    call_ids: tuple[str, ...] = ()
    notes: str = ""

    @property
    def passed(self) -> bool:
        return bool(self.evidence) and all(self.evidence.values())

    @property
    def missing_evidence(self) -> tuple[str, ...]:
        return tuple(name for name, present in self.evidence.items() if not present)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture": self.fixture.to_dict(),
            "passed": self.passed,
            "evidence": self.evidence,
            "missing_evidence": list(self.missing_evidence),
            "signal": self.signal.to_dict(),
            "call_ids": list(self.call_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class HumanVisibilityScoringRun:
    """Aggregate run for human-facing inspection usefulness."""

    version: str
    project_root: str
    history_path: str
    elapsed_ms: int
    scores: tuple[HumanVisibilityScore, ...]
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


def default_human_visibility_fixtures() -> tuple[HumanVisibilityFixture, ...]:
    """Return precommitted human-facing visibility fixtures."""
    return (
        HumanVisibilityFixture(
            task_id="projection_visibility",
            purpose="project query evidence is visible across projection, stream, cockpit, and panel readback",
            expected_surfaces=("active_projection", "stream", "cockpit", "panel_readback"),
        ),
        HumanVisibilityFixture(
            task_id="seed_visibility",
            purpose="seed search evidence is visible across active seed, stream/history, cockpit, and panel readback",
            expected_surfaces=("active_seed", "stream_or_history", "cockpit", "panel_readback"),
        ),
        HumanVisibilityFixture(
            task_id="promotion_visibility",
            purpose="operator promotion metadata is visible through history, stream, host panels, and raw payloads",
            expected_surfaces=("history", "stream", "host_panel", "raw_payload"),
        ),
        HumanVisibilityFixture(
            task_id="status_score_visibility",
            purpose="status, tool registry, builder score, and projection score are visible from shared host state",
            expected_surfaces=("status", "tools", "builder_score", "projection_score", "scores_panel"),
        ),
    )


def default_human_visibility_score_path(project_root: Path | str) -> Path:
    """Return the project-owned human visibility score artifact path."""
    return Path(project_root) / "data" / "mcp_inspection" / "human_visibility_scores.json"


def run_human_visibility_scoring(
    project_root: Path | str,
    *,
    history_path: Path | str,
    score_path: Path | str | None = None,
    fixtures: tuple[HumanVisibilityFixture, ...] = default_human_visibility_fixtures(),
    history_limit: int = 12,
    project_doc_profile: str = "core",
) -> HumanVisibilityScoringRun:
    """Score whether shared host surfaces expose the same inspection evidence."""
    root = Path(project_root).resolve()
    resolved_history_path = Path(history_path)
    state = default_host_state(root, history_limit=history_limit)
    scores: list[HumanVisibilityScore] = []
    started = time.perf_counter()

    for fixture in fixtures:
        if fixture.task_id == "projection_visibility":
            score = _score_projection_visibility(root, resolved_history_path, state, fixture, history_limit)
        elif fixture.task_id == "seed_visibility":
            score = _score_seed_visibility(
                root,
                resolved_history_path,
                state,
                fixture,
                history_limit,
                project_doc_profile,
            )
        elif fixture.task_id == "promotion_visibility":
            score = _score_promotion_visibility(root, resolved_history_path, state, fixture, history_limit)
        elif fixture.task_id == "status_score_visibility":
            score = _score_status_score_visibility(root, resolved_history_path, state, fixture)
        else:
            evidence = {"known_fixture": False}
            score = _build_score(fixture, evidence, notes=f"Unknown fixture: {fixture.task_id}")
        scores.append(score)

    report = evaluate_mcp_usefulness(tuple(score.signal for score in scores))
    run = HumanVisibilityScoringRun(
        version=HUMAN_VISIBILITY_SCORING_VERSION,
        project_root=str(root),
        history_path=str(resolved_history_path),
        elapsed_ms=max(1, int((time.perf_counter() - started) * 1000)),
        scores=tuple(scores),
        usefulness_report=report,
    )
    if score_path is not None:
        output_path = Path(score_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(run.to_json(), encoding="utf-8")
    return run


def _score_projection_visibility(
    root: Path,
    history_path: Path,
    state: SharedHostState,
    fixture: HumanVisibilityFixture,
    history_limit: int,
) -> HumanVisibilityScore:
    query = "class object function"
    query_result = _dispatch(
        root,
        history_path,
        state,
        PROJECT_QUERY_TOOL_NAME,
        {"query": query, "limit": 3},
    )
    _dispatch(root, history_path, state, HOST_STREAM_TOOL_NAME, {"history_limit": history_limit})
    _dispatch(root, history_path, state, HOST_COCKPIT_TOOL_NAME, {"history_limit": max(6, history_limit)})
    state.set_active_tab("projection")
    panel_result = _dispatch(root, history_path, state, HOST_READ_PANELS_TOOL_NAME, {"mode": "active"})
    snapshot = panel_result.snapshot
    projection = snapshot.active_projection or {}
    panel = panel_result.payload.get("panel", {})
    cockpit_text = snapshot.panels.get("cockpit", {}).get("text", "")
    evidence = {
        "active_projection": projection.get("query") == query
        and bool(projection.get("selected_layer")),
        "stream": any(item.query == query and item.selected_layer for item in snapshot.stream_items),
        "cockpit": query in cockpit_text and "Latest Projection" in cockpit_text,
        "panel_readback": panel.get("name") == "projection" and query in str(panel.get("text", "")),
    }
    return _build_score(
        fixture,
        evidence,
        call_ids=_call_ids(query_result),
        notes=f"query={query}; selected_layer={projection.get('selected_layer', '')}",
    )


def _score_seed_visibility(
    root: Path,
    history_path: Path,
    state: SharedHostState,
    fixture: HumanVisibilityFixture,
    history_limit: int,
    project_doc_profile: str,
) -> HumanVisibilityScore:
    del project_doc_profile
    _dispatch(root, history_path, state, HOST_STREAM_TOOL_NAME, {"history_limit": history_limit})
    _dispatch(root, history_path, state, HOST_HISTORY_VIEW_TOOL_NAME, {"history_limit": history_limit})
    _dispatch(root, history_path, state, HOST_COCKPIT_TOOL_NAME, {"history_limit": max(6, history_limit)})
    state.set_active_tab("seed")
    panel_result = _dispatch(root, history_path, state, HOST_READ_PANELS_TOOL_NAME, {"mode": "active"})
    snapshot = panel_result.snapshot
    active_seed = snapshot.active_seed or {}
    panel = panel_result.payload.get("panel", {})
    cockpit_text = snapshot.panels.get("cockpit", {}).get("text", "")
    history_text = snapshot.panels.get("history", {}).get("text", "")
    seed_query = str(active_seed.get("query", ""))
    evidence = {
        "active_seed": bool(active_seed.get("query")) and bool(active_seed.get("selected_seed")),
        "stream_or_history": any(item.tool_name == TRAVERSAL_TOOL_NAME for item in snapshot.stream_items)
        or TRAVERSAL_TOOL_NAME in history_text
        or bool(active_seed.get("call_id")),
        "cockpit": "Latest Seed" in cockpit_text and (not seed_query or seed_query in cockpit_text),
        "panel_readback": panel.get("name") == "seed" and "Active Seed Flow" in str(panel.get("text", "")),
    }
    return _build_score(
        fixture,
        evidence,
        call_ids=tuple(item for item in (str(active_seed.get("call_id", "")),) if item),
        notes=f"query={seed_query}; selected_seed={bool(active_seed.get('selected_seed'))}",
    )


def _score_promotion_visibility(
    root: Path,
    history_path: Path,
    state: SharedHostState,
    fixture: HumanVisibilityFixture,
    history_limit: int,
) -> HumanVisibilityScore:
    query_result = _dispatch(
        root,
        history_path,
        state,
        PROJECT_QUERY_TOOL_NAME,
        {"query": "semantic object provenance relations", "limit": 3},
    )
    call_id = str(query_result.payload.get("call_id", ""))
    label = "visibility-fixture"
    reason = "shared-evidence"
    promote_result = _dispatch(
        root,
        history_path,
        state,
        HOST_PROMOTE_CALL_TOOL_NAME,
        {
            "call_id": call_id,
            "pinned": True,
            "label": label,
            "reason": reason,
            "note": "Promoted by human visibility scoring.",
        },
    )
    _dispatch(root, history_path, state, HOST_STREAM_TOOL_NAME, {"history_limit": history_limit})
    _dispatch(root, history_path, state, HOST_HISTORY_VIEW_TOOL_NAME, {"history_limit": history_limit})
    state.set_active_tab("history")
    panel_result = _dispatch(root, history_path, state, HOST_READ_PANELS_TOOL_NAME, {"mode": "active"})
    snapshot = panel_result.snapshot
    history_text = snapshot.panels.get("history", {}).get("text", "")
    panel_text = str(panel_result.payload.get("panel", {}).get("text", ""))
    evidence = {
        "history": any(call.operator_label == label and call.operator_reason == reason for call in snapshot.recent_calls),
        "stream": any(item.operator_label == label and item.operator_reason == reason for item in snapshot.stream_items),
        "host_panel": f"operator={label}/{reason}" in history_text or f"operator={label}/{reason}" in panel_text,
        "raw_payload": snapshot.raw_payload_cache.get("promotion", {}).get("record", {}).get("pinned") is True,
    }
    return _build_score(
        fixture,
        evidence,
        call_ids=tuple(item for item in (call_id, str(promote_result.payload.get("call_id", ""))) if item),
        notes=f"call_id={call_id}; label={label}; reason={reason}",
    )


def _score_status_score_visibility(
    root: Path,
    history_path: Path,
    state: SharedHostState,
    fixture: HumanVisibilityFixture,
) -> HumanVisibilityScore:
    status_result = _dispatch(root, history_path, state, HOST_STATUS_TOOL_NAME, {})
    tools_result = _dispatch(root, history_path, state, HOST_TOOLS_TOOL_NAME, {})
    state.set_active_tab("scores")
    panel_result = _dispatch(root, history_path, state, HOST_READ_PANELS_TOOL_NAME, {"mode": "active"})
    snapshot = panel_result.snapshot
    score_artifacts = read_score_artifacts(root)
    scores_text = snapshot.panels.get("scores", {}).get("text", "")
    evidence = {
        "status": bool(status_result.payload.get("active_tranche"))
        and bool(status_result.payload.get("next_tranche")),
        "tools": bool(tools_result.payload.get("tools") or tools_result.payload.get("registrations")),
        "builder_score": bool(score_artifacts.get("builder", {}).get("meets_acceptance")),
        "projection_score": bool(score_artifacts.get("projection", {}).get("meets_acceptance")),
        "scores_panel": "builder_score:" in scores_text and "projection_score:" in scores_text,
    }
    notes = (
        f"builder_score_path={default_builder_task_score_path(root)}; "
        f"projection_score_path={default_context_projection_score_path(root)}"
    )
    return _build_score(fixture, evidence, notes=notes)


def _dispatch(
    root: Path,
    history_path: Path,
    state: SharedHostState,
    tool_name: str,
    payload: dict[str, Any],
) -> HostDispatchResult:
    return dispatch_host_command(
        root,
        create_host_command_envelope(
            tool_name=tool_name,
            payload=payload,
            actor="builder",
            source_surface="visibility_scoring",
        ),
        state=state,
        history_path=history_path,
    )


def _build_score(
    fixture: HumanVisibilityFixture,
    evidence: dict[str, bool],
    *,
    call_ids: tuple[str, ...] = (),
    notes: str = "",
) -> HumanVisibilityScore:
    passed = bool(evidence) and all(evidence.values())
    evidence_quality = round(sum(1 for value in evidence.values() if value) / max(1, len(evidence)), 4)
    signal = McpUsefulnessSignal(
        capability_name=f"human_visibility.{fixture.task_id}",
        task_fit=1.0 if passed else max(0.2, evidence_quality * 0.6),
        evidence_quality=evidence_quality,
        actionability=0.9 if passed else 0.35,
        friction_reduction=0.9 if passed else 0.3,
        repeatability=1.0,
        notes=f"passed={passed}; evidence={evidence}; {notes}".strip(),
    )
    return HumanVisibilityScore(
        fixture=fixture,
        evidence=evidence,
        signal=signal,
        call_ids=call_ids,
        notes=notes,
    )


def _call_ids(result: HostDispatchResult) -> tuple[str, ...]:
    call_id = str(result.payload.get("call_id", ""))
    if call_id:
        return (call_id,)
    tool_call = result.payload.get("tool_call", {})
    tool_call_id = str(tool_call.get("call_id", ""))
    return (tool_call_id,) if tool_call_id else ()
