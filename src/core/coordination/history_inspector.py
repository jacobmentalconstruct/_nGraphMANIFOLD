"""History-aware MCP inspector payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .builder_task_scoring import default_builder_task_score_path
from .context_projection_scoring import default_context_projection_score_path
from .mcp_inspection_history import McpInspectionHistoryStore
from .interaction_spine import PROJECT_QUERY_TOOL_NAME
from .seed_search import seed_flow_window_for_semantic_id

HISTORY_AWARE_INSPECTOR_VERSION = "v1"


@dataclass(frozen=True)
class HistoryInspectorCallSummary:
    """Compact summary of one persisted MCP call."""

    call_id: str
    captured_at: str
    tool_name: str
    capability_name: str
    status: str
    aggregate_score: float
    step_count: int
    blocker_count: int
    selected_layer: str = ""
    candidate_count: int = 0
    task_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "captured_at": self.captured_at,
            "tool_name": self.tool_name,
            "capability_name": self.capability_name,
            "status": self.status,
            "aggregate_score": self.aggregate_score,
            "step_count": self.step_count,
            "blocker_count": self.blocker_count,
            "selected_layer": self.selected_layer,
            "candidate_count": self.candidate_count,
            "task_id": self.task_id,
        }


@dataclass(frozen=True)
class HistoryAwareInspectorPayload:
    """Readable summary plus raw history payload for the inspector."""

    version: str
    history_path: str
    record_count: int
    latest_score_artifact: dict[str, Any] | None
    calls: tuple[HistoryInspectorCallSummary, ...]
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "history_path": self.history_path,
            "record_count": self.record_count,
            "latest_score_artifact": self.latest_score_artifact,
            "calls": [call.to_dict() for call in self.calls],
            "raw": self.raw,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def to_summary_text(self) -> str:
        lines = [
            "nGraphMANIFOLD MCP History",
            f"records: {self.record_count}",
            f"history: {self.history_path}",
        ]
        if self.latest_score_artifact:
            report = self.latest_score_artifact.get("usefulness_report", {})
            lines.append(
                "latest builder score: "
                f"{report.get('aggregate_score', 'n/a')} "
                f"accepted={self.latest_score_artifact.get('meets_acceptance', 'n/a')}"
            )
        lines.append("")
        lines.append("Recent calls:")
        for call in self.calls:
            task = f" task={call.task_id}" if call.task_id else ""
            projection = ""
            if call.selected_layer:
                projection = f" selected_layer={call.selected_layer} candidates={call.candidate_count}"
            lines.append(
                f"- {call.captured_at} {call.tool_name} score={call.aggregate_score} "
                f"steps={call.step_count} blockers={call.blocker_count}{projection}{task}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class InteractionStreamItem:
    """One readable command/result pair projected from inspection history."""

    call_id: str
    captured_at: str
    tool_name: str
    status: str
    query: str
    response: str
    selected_layer: str = ""
    selected_kind: str = ""
    selected_score: float = 0.0
    source_ref: str = ""
    content_preview: str = ""
    aggregate_score: float = 0.0
    projection_flow: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "captured_at": self.captured_at,
            "tool_name": self.tool_name,
            "status": self.status,
            "query": self.query,
            "response": self.response,
            "selected_layer": self.selected_layer,
            "selected_kind": self.selected_kind,
            "selected_score": self.selected_score,
            "source_ref": self.source_ref,
            "content_preview": self.content_preview,
            "aggregate_score": self.aggregate_score,
            "projection_flow": list(self.projection_flow),
        }


@dataclass(frozen=True)
class InteractionStreamPayload:
    """Chronological stream of readable query/response objects."""

    version: str
    history_path: str
    record_count: int
    items: tuple[InteractionStreamItem, ...]
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "history_path": self.history_path,
            "record_count": self.record_count,
            "items": [item.to_dict() for item in self.items],
            "raw": self.raw,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def to_stream_text(self) -> str:
        lines = [
            "nGraphMANIFOLD Interaction Stream",
            f"records: {self.record_count}",
            f"history: {self.history_path}",
            "",
        ]
        for index, item in enumerate(self.items, start=1):
            lines.append(f"[{index}] {item.captured_at} {item.tool_name} status={item.status}")
            lines.append(f"    Q: {item.query or '(no query text)'}")
            lines.append(f"    R: {item.response or '(no response summary)'}")
            if item.selected_layer:
                lines.append(
                    "       "
                    f"layer={item.selected_layer} kind={item.selected_kind or 'n/a'} "
                    f"score={item.selected_score}"
                )
            if item.content_preview:
                lines.append(f"       preview={item.content_preview}")
            if item.source_ref:
                lines.append(f"       source={item.source_ref}")
            lines.append(f"       call_id={item.call_id} aggregate={item.aggregate_score}")
            lines.append("")
        return "\n".join(lines)


@dataclass(frozen=True)
class VisibilityCockpitPayload:
    """Unified read-only visibility payload for the prototype cockpit."""

    version: str
    history_path: str
    record_count: int
    latest_builder_score: dict[str, Any] | None
    latest_projection_score: dict[str, Any] | None
    latest_projection: dict[str, Any] | None
    latest_seed: dict[str, Any] | None
    stream: InteractionStreamPayload
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "history_path": self.history_path,
            "record_count": self.record_count,
            "latest_builder_score": self.latest_builder_score,
            "latest_projection_score": self.latest_projection_score,
            "latest_projection": self.latest_projection,
            "latest_seed": self.latest_seed,
            "stream": self.stream.to_dict(),
            "raw": self.raw,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def build_history_aware_inspector_payload(
    project_root: Path | str,
    *,
    history_path: Path | str,
    limit: int = 10,
) -> HistoryAwareInspectorPayload:
    """Return summarized recent history plus raw snapshot data."""
    snapshot = McpInspectionHistoryStore(history_path).snapshot(limit=limit)
    score_artifact = _read_score_artifact(default_builder_task_score_path(project_root))
    task_ids_by_call = _task_ids_by_call(score_artifact)
    calls = tuple(
        _summarize_record(record.to_dict(), task_ids_by_call)
        for record in snapshot.records
    )
    return HistoryAwareInspectorPayload(
        version=HISTORY_AWARE_INSPECTOR_VERSION,
        history_path=snapshot.history_path,
        record_count=snapshot.record_count,
        latest_score_artifact=score_artifact,
        calls=calls,
        raw=snapshot.to_dict(),
    )


def build_interaction_stream_payload(
    project_root: Path | str,
    *,
    history_path: Path | str,
    limit: int = 50,
) -> InteractionStreamPayload:
    """Return recent command/result pairs in chronological display order."""
    del project_root
    snapshot = McpInspectionHistoryStore(history_path).snapshot(limit=limit)
    items = tuple(
        _stream_item_from_record(record.to_dict())
        for record in reversed(snapshot.records)
    )
    return InteractionStreamPayload(
        version=HISTORY_AWARE_INSPECTOR_VERSION,
        history_path=snapshot.history_path,
        record_count=snapshot.record_count,
        items=items,
        raw=snapshot.to_dict(),
    )


def build_visibility_cockpit_payload(
    project_root: Path | str,
    *,
    history_path: Path | str,
    limit: int = 12,
) -> VisibilityCockpitPayload:
    """Return one read-only cockpit payload combining scores, stream, and latest selections."""
    root = Path(project_root).resolve()
    snapshot = McpInspectionHistoryStore(history_path).snapshot(limit=limit)
    builder_score = _read_score_artifact(default_builder_task_score_path(root))
    projection_score = _read_score_artifact(default_context_projection_score_path(root))
    stream = build_interaction_stream_payload(root, history_path=history_path, limit=limit)
    latest_projection = _latest_project_query_projection(snapshot.to_dict())
    latest_seed = _latest_builder_seed(root, builder_score)
    return VisibilityCockpitPayload(
        version=HISTORY_AWARE_INSPECTOR_VERSION,
        history_path=snapshot.history_path,
        record_count=snapshot.record_count,
        latest_builder_score=builder_score,
        latest_projection_score=projection_score,
        latest_projection=latest_projection,
        latest_seed=latest_seed,
        stream=stream,
        raw={
            "history_snapshot": snapshot.to_dict(),
            "builder_score_artifact": builder_score,
            "projection_score_artifact": projection_score,
            "latest_projection": latest_projection,
            "latest_seed": latest_seed,
        },
    )


def _summarize_record(
    record: dict[str, Any],
    task_ids_by_call: dict[str, str],
) -> HistoryInspectorCallSummary:
    call = record["call"]
    capture = call.get("capture", {})
    traversal = capture.get("response", {}).get("traversal_report", {})
    evidence = capture.get("result", {}).get("evidence_summary", {})
    return HistoryInspectorCallSummary(
        call_id=record["call_id"],
        captured_at=record["captured_at"],
        tool_name=record["tool_name"],
        capability_name=record["capability_name"],
        status=record["status"],
        aggregate_score=float(record["aggregate_score"]),
        step_count=len(traversal.get("steps", [])),
        blocker_count=len(traversal.get("blockers", [])),
        selected_layer=str(evidence.get("selected_layer") or ""),
        candidate_count=int(evidence.get("candidate_count", 0)),
        task_id=task_ids_by_call.get(record["call_id"], ""),
    )


def _stream_item_from_record(record: dict[str, Any]) -> InteractionStreamItem:
    call = record["call"]
    capture = call.get("capture", {})
    query, response, selected = _query_response_summary(capture)
    return InteractionStreamItem(
        call_id=record["call_id"],
        captured_at=record["captured_at"],
        tool_name=record["tool_name"],
        status=record["status"],
        query=query,
        response=response,
        selected_layer=str(selected.get("selected_layer") or ""),
        selected_kind=str(selected.get("kind") or selected.get("selected_candidate_kind") or ""),
        selected_score=float(selected.get("score") or selected.get("selected_candidate_score") or 0.0),
        source_ref=str(selected.get("source_ref") or ""),
        content_preview=_compact(str(selected.get("content_preview") or "")),
        aggregate_score=float(record["aggregate_score"]),
        projection_flow=tuple(dict(item) for item in _projection_flow_items(capture)),
    )


def _query_response_summary(capture: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    command = capture.get("command", {})
    command_payload = command.get("payload", {})
    if command_payload.get("query"):
        query = str(command_payload.get("query"))
        frame = capture.get("response", {}).get("projection_frame", {})
        selected = dict(frame.get("selected_candidate") or {})
        selected_layer = str(frame.get("selected_layer") or selected.get("layer_name") or "")
        selected["selected_layer"] = selected_layer
        response = (
            f"{selected_layer or 'n/a'} selected "
            f"{selected.get('kind', 'candidate')} "
            f"score={selected.get('score', 'n/a')}"
        )
        return query, response, selected

    request = capture.get("request", {})
    if request.get("seed_semantic_id"):
        traversal = capture.get("response", {}).get("traversal_report", {})
        query = f"traverse seed {request.get('seed_semantic_id')}"
        response = (
            f"traversal steps={len(traversal.get('steps', []))} "
            f"blockers={len(traversal.get('blockers', []))}"
        )
        return query, response, {}

    evidence = capture.get("result", {}).get("evidence_summary", {})
    if evidence.get("terms"):
        query = " ".join(str(term) for term in evidence.get("terms", []))
        response = (
            f"{evidence.get('selected_layer', 'n/a')} selected "
            f"{evidence.get('selected_candidate_kind', 'candidate')} "
            f"score={evidence.get('selected_candidate_score', 'n/a')}"
        )
        return query, response, dict(evidence)

    return "", "", {}


def _projection_flow_items(capture: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    frame = capture.get("response", {}).get("projection_frame", {})
    flow = frame.get("selected_flow") or {}
    objects = flow.get("objects") or ()
    return tuple(dict(item) for item in objects[:3] if isinstance(item, dict))


def _latest_project_query_projection(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    for record in snapshot.get("records", ()):
        if record.get("tool_name") != PROJECT_QUERY_TOOL_NAME:
            continue
        call = record.get("call", {})
        capture = call.get("capture", {})
        frame = capture.get("response", {}).get("projection_frame", {})
        selected = frame.get("selected_candidate") or {}
        return {
            "call_id": record.get("call_id", ""),
            "captured_at": record.get("captured_at", ""),
            "query": capture.get("command", {}).get("payload", {}).get("query", ""),
            "selected_layer": frame.get("selected_layer"),
            "selected_candidate": selected,
            "selected_flow": frame.get("selected_flow"),
            "layer_summaries": [
                {
                    "name": projection.get("layer", {}).get("name", ""),
                    "layer_score": projection.get("layer_score", 0.0),
                    "candidate_count": projection.get("candidate_count", 0),
                }
                for projection in frame.get("projections", ())
            ],
            "evidence_summary": capture.get("result", {}).get("evidence_summary", {}),
        }
    return None


def _latest_builder_seed(
    project_root: Path,
    builder_score_artifact: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not builder_score_artifact:
        return None
    scores = builder_score_artifact.get("scores", [])
    if not scores:
        return None
    preferred = next(
        (
            score for score in scores
            if score.get("fixture", {}).get("task_id") == "current_tranche_lookup"
        ),
        scores[0],
    )
    semantic_id = str(preferred.get("seed_semantic_id") or "")
    if not semantic_id:
        return None
    flow = seed_flow_window_for_semantic_id(project_root, semantic_id)
    fixture = preferred.get("fixture", {})
    return {
        "task_id": fixture.get("task_id", ""),
        "question": fixture.get("question", ""),
        "seed_semantic_id": semantic_id,
        "seed_source_ref": preferred.get("seed_source_ref", ""),
        "traversal_step_count": preferred.get("traversal_step_count", 0),
        "blocker_count": preferred.get("blocker_count", 0),
        "call_id": preferred.get("call_id", ""),
        "seed_flow": flow.to_dict() if flow else None,
    }


def _compact(value: str, *, limit: int = 180) -> str:
    compacted = " ".join(value.split())
    if len(compacted) <= limit:
        return compacted
    return compacted[: limit - 3] + "..."


def _read_score_artifact(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _task_ids_by_call(score_artifact: dict[str, Any] | None) -> dict[str, str]:
    if not score_artifact:
        return {}
    mapping: dict[str, str] = {}
    for score in score_artifact.get("scores", []):
        call_id = score.get("call_id")
        task_id = score.get("fixture", {}).get("task_id", "")
        if call_id and task_id:
            mapping[str(call_id)] = str(task_id)
    return mapping
