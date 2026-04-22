"""History-aware MCP inspector payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .builder_task_scoring import default_builder_task_score_path
from .mcp_inspection_history import McpInspectionHistoryStore

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
