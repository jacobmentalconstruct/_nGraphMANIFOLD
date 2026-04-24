"""Shared host state and dispatcher for the desktop workspace."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .builder_task_scoring import default_builder_task_score_path
from .context_projection_scoring import default_context_projection_score_path
from .history_inspector import (
    HistoryAwareInspectorPayload,
    HistoryInspectorCallSummary,
    InteractionStreamItem,
    build_history_aware_inspector_payload,
    build_interaction_stream_payload,
    build_visibility_cockpit_payload,
)
from .interaction_spine import (
    DEFAULT_CONTEXT_STACK,
    PROJECT_QUERY_TOOL_NAME,
    CommandEnvelope,
    create_command_envelope,
    run_project_query_interaction,
)
from .mcp_inspection_history import McpInspectionHistoryStore, default_mcp_inspection_history_path
from .mcp_tool_registry import PROJECT_QUERY_CAPABILITY_NAME, TRAVERSAL_TOOL_NAME
from .seed_search import run_seed_search_traversal

HOST_WORKSPACE_VERSION = "v1"
HOST_HISTORY_VIEW_TOOL_NAME = "ngraph.host.history_view"
HOST_STREAM_TOOL_NAME = "ngraph.host.stream_view"
HOST_COCKPIT_TOOL_NAME = "ngraph.host.cockpit_view"
HOST_SEED_SEARCH_TOOL_NAME = "ngraph.host.search_seeds"


@dataclass(frozen=True)
class HostWorkspaceSnapshot:
    """Live host snapshot derived from durable history and current session cache."""

    version: str
    history_path: str
    record_count: int
    recent_calls: tuple[HistoryInspectorCallSummary, ...]
    stream_items: tuple[InteractionStreamItem, ...]
    latest_builder_score: dict[str, Any] | None
    latest_projection_score: dict[str, Any] | None
    active_projection: dict[str, Any] | None
    active_seed: dict[str, Any] | None
    active_interaction: dict[str, Any] | None
    active_command: dict[str, Any] | None
    raw_payload_cache: dict[str, Any]
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "history_path": self.history_path,
            "record_count": self.record_count,
            "recent_calls": [call.to_dict() for call in self.recent_calls],
            "stream_items": [item.to_dict() for item in self.stream_items],
            "latest_builder_score": self.latest_builder_score,
            "latest_projection_score": self.latest_projection_score,
            "active_projection": self.active_projection,
            "active_seed": self.active_seed,
            "active_interaction": self.active_interaction,
            "active_command": self.active_command,
            "raw_payload_cache": self.raw_payload_cache,
            "raw": self.raw,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class HostDispatchResult:
    """Result of one shared host command dispatch."""

    command: CommandEnvelope
    snapshot: HostWorkspaceSnapshot
    payload: dict[str, Any]
    rendered_json: str
    status: str = "ok"


@dataclass
class SharedHostState:
    """Mutable in-process host state with a durable-ledger refresh model."""

    project_root: Path
    history_path: Path
    history_limit: int = 12
    raw_payload_cache: dict[str, Any] = field(default_factory=dict)
    active_call_id: str = ""
    active_tool_name: str = ""
    snapshot: HostWorkspaceSnapshot | None = None

    def refresh(self) -> HostWorkspaceSnapshot:
        self.snapshot = build_host_workspace_snapshot(
            self.project_root,
            history_path=self.history_path,
            history_limit=self.history_limit,
            active_call_id=self.active_call_id,
            active_tool_name=self.active_tool_name,
            raw_payload_cache=self.raw_payload_cache,
        )
        return self.snapshot

    def cache_payload(self, key: str, payload: dict[str, Any]) -> None:
        self.raw_payload_cache[key] = payload

    def set_active_call(self, call_id: str, tool_name: str) -> None:
        self.active_call_id = call_id
        self.active_tool_name = tool_name


def build_host_workspace_snapshot(
    project_root: Path | str,
    *,
    history_path: Path | str | None = None,
    history_limit: int = 12,
    active_call_id: str = "",
    active_tool_name: str = "",
    raw_payload_cache: dict[str, Any] | None = None,
) -> HostWorkspaceSnapshot:
    """Build one canonical host snapshot from history, score artifacts, and live cache."""
    root = Path(project_root).resolve()
    resolved_history_path = Path(history_path) if history_path else default_mcp_inspection_history_path(root)
    history_payload = build_history_aware_inspector_payload(
        root,
        history_path=resolved_history_path,
        limit=history_limit,
    )
    stream_payload = build_interaction_stream_payload(
        root,
        history_path=resolved_history_path,
        limit=max(6, history_limit),
    )
    cockpit_payload = build_visibility_cockpit_payload(
        root,
        history_path=resolved_history_path,
        limit=max(6, history_limit),
    )
    cache = dict(raw_payload_cache or {})
    active_interaction = _active_interaction_from_cache_or_history(
        cache,
        history_payload,
        active_call_id=active_call_id,
    )
    active_projection = _active_projection(cache, active_interaction, cockpit_payload.to_dict())
    active_seed = _active_seed(cache, cockpit_payload.to_dict())
    active_command = active_interaction.get("capture", {}).get("command") if active_interaction else None
    raw = {
        "history": history_payload.to_dict(),
        "stream": stream_payload.to_dict(),
        "cockpit": cockpit_payload.to_dict(),
        "active_interaction": active_interaction,
        "active_projection": active_projection,
        "active_seed": active_seed,
    }
    return HostWorkspaceSnapshot(
        version=HOST_WORKSPACE_VERSION,
        history_path=str(resolved_history_path),
        record_count=history_payload.record_count,
        recent_calls=history_payload.calls,
        stream_items=stream_payload.items,
        latest_builder_score=cockpit_payload.latest_builder_score,
        latest_projection_score=cockpit_payload.latest_projection_score,
        active_projection=active_projection,
        active_seed=active_seed,
        active_interaction=active_interaction,
        active_command=active_command,
        raw_payload_cache=cache,
        raw=raw,
    )


def dispatch_host_command(
    project_root: Path | str,
    command: CommandEnvelope,
    *,
    state: SharedHostState | None = None,
    history_path: Path | str | None = None,
    history_limit: int = 12,
) -> HostDispatchResult:
    """Normalize supported UI and CLI actions through one in-process dispatcher."""
    root = Path(project_root).resolve()
    resolved_history_path = Path(history_path) if history_path else default_mcp_inspection_history_path(root)
    host_state = state or SharedHostState(root, resolved_history_path, history_limit=history_limit)

    if command.tool_name == PROJECT_QUERY_TOOL_NAME:
        call = _dispatch_project_query(root, command, resolved_history_path)
        host_state.cache_payload("active_interaction", call)
        host_state.cache_payload("project_query", call)
        host_state.set_active_call(str(call.get("call_id", "")), PROJECT_QUERY_TOOL_NAME)
        snapshot = host_state.refresh()
        payload = call
    elif command.tool_name == HOST_SEED_SEARCH_TOOL_NAME:
        payload = _dispatch_seed_search(root, command, resolved_history_path)
        tool_call = payload.get("tool_call", {})
        host_state.cache_payload("seed_search", payload)
        host_state.set_active_call(str(tool_call.get("call_id", "")), str(tool_call.get("tool", {}).get("tool_name", "")))
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_HISTORY_VIEW_TOOL_NAME:
        snapshot = host_state.refresh()
        payload = snapshot.raw["history"]
        host_state.cache_payload("history", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_STREAM_TOOL_NAME:
        snapshot = host_state.refresh()
        payload = snapshot.raw["stream"]
        host_state.cache_payload("stream", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_COCKPIT_TOOL_NAME:
        snapshot = host_state.refresh()
        payload = snapshot.raw["cockpit"]
        host_state.cache_payload("cockpit", payload)
        snapshot = host_state.refresh()
    else:
        raise ValueError(f"Unsupported shared host command: {command.tool_name}")

    return HostDispatchResult(
        command=command,
        snapshot=snapshot,
        payload=payload,
        rendered_json=json.dumps(payload, indent=2, sort_keys=True),
    )


def create_host_command_envelope(
    *,
    tool_name: str,
    payload: dict[str, Any],
    actor: str = "human",
    source_surface: str = "cli",
) -> CommandEnvelope:
    """Create a shared host command envelope using the canonical command model."""
    return create_command_envelope(
        tool_name=tool_name,
        payload=payload,
        actor=actor,
        source_surface=source_surface,
    )


def default_host_state(project_root: Path | str, *, history_limit: int = 12) -> SharedHostState:
    """Return the default shared host state bound to the project ledger."""
    root = Path(project_root).resolve()
    return SharedHostState(
        project_root=root,
        history_path=default_mcp_inspection_history_path(root),
        history_limit=history_limit,
    )


def _dispatch_project_query(
    root: Path,
    command: CommandEnvelope,
    history_path: Path,
) -> dict[str, Any]:
    payload = command.payload
    context_stack = tuple(str(item) for item in payload.get("context_stack", DEFAULT_CONTEXT_STACK))
    capture = run_project_query_interaction(
        root,
        str(payload.get("query", "")),
        limit=int(payload.get("limit", 3)),
        context_stack=context_stack,
        actor=command.actor,
        source_surface=command.source_surface,
        created_at=command.created_at,
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
    McpInspectionHistoryStore(history_path).record_call(call)
    return call


def _dispatch_seed_search(
    root: Path,
    command: CommandEnvelope,
    history_path: Path,
) -> dict[str, Any]:
    payload = command.payload
    result = run_seed_search_traversal(
        root,
        str(payload.get("query", "")),
        history_path=history_path,
        limit=int(payload.get("seed_limit", payload.get("limit", 5))),
    )
    return result.to_dict()


def _active_interaction_from_cache_or_history(
    cache: dict[str, Any],
    history_payload: HistoryAwareInspectorPayload,
    *,
    active_call_id: str,
) -> dict[str, Any] | None:
    cached = cache.get("active_interaction")
    if isinstance(cached, dict) and cached.get("call_id"):
        if not active_call_id or str(cached.get("call_id")) == active_call_id:
            return cached
    records = history_payload.raw.get("records", [])
    if active_call_id:
        for record in records:
            if str(record.get("call_id", "")) == active_call_id:
                return dict(record.get("call", {}))
    if records:
        return dict(records[0].get("call", {}))
    return None


def _active_projection(
    cache: dict[str, Any],
    active_interaction: dict[str, Any] | None,
    cockpit_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if active_interaction:
        projection = _projection_from_call(active_interaction)
        if projection:
            return projection
    cached = cache.get("project_query")
    if isinstance(cached, dict):
        projection = _projection_from_call(cached)
        if projection:
            return projection
    return cockpit_payload.get("latest_projection")


def _active_seed(cache: dict[str, Any], cockpit_payload: dict[str, Any]) -> dict[str, Any] | None:
    cached = cache.get("seed_search")
    if isinstance(cached, dict):
        search = cached.get("search", {})
        tool_call = cached.get("tool_call", {})
        return {
            "query": search.get("query", ""),
            "candidate_count": search.get("candidate_count", 0),
            "selected_seed": search.get("selected_seed"),
            "selected_flow": search.get("selected_flow"),
            "tool_name": tool_call.get("tool", {}).get("tool_name", TRAVERSAL_TOOL_NAME),
            "call_id": tool_call.get("call_id", ""),
            "traversal_report": tool_call.get("capture", {}).get("response", {}).get("traversal_report", {}),
        }
    latest_seed = cockpit_payload.get("latest_seed")
    if latest_seed:
        return {
            "query": latest_seed.get("question", ""),
            "candidate_count": 1,
            "selected_seed": {
                "semantic_id": latest_seed.get("seed_semantic_id", ""),
                "source_ref": latest_seed.get("seed_source_ref", ""),
                "kind": "project_document_seed",
            },
            "selected_flow": latest_seed.get("seed_flow"),
            "tool_name": TRAVERSAL_TOOL_NAME,
            "call_id": latest_seed.get("call_id", ""),
            "traversal_report": {
                "steps": [None] * int(latest_seed.get("traversal_step_count", 0)),
                "blockers": [None] * int(latest_seed.get("blocker_count", 0)),
            },
        }
    return None


def _projection_from_call(call: dict[str, Any]) -> dict[str, Any] | None:
    capture = call.get("capture", {})
    frame = capture.get("response", {}).get("projection_frame", {})
    if not frame:
        return None
    return {
        "call_id": call.get("call_id", ""),
        "captured_at": capture.get("captured_at", ""),
        "query": capture.get("command", {}).get("payload", {}).get("query", ""),
        "selected_layer": frame.get("selected_layer"),
        "selected_candidate": frame.get("selected_candidate"),
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


def read_score_artifacts(project_root: Path | str) -> dict[str, dict[str, Any] | None]:
    """Read the durable builder and projection score artifacts."""
    root = Path(project_root).resolve()
    return {
        "builder": _read_json(default_builder_task_score_path(root)),
        "projection": _read_json(default_context_projection_score_path(root)),
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
