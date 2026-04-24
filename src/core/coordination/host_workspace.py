"""Shared host state and dispatcher for the desktop workspace."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import AppSettings
from ..engine import ApplicationEngine
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
from .mcp_inspection_history import (
    McpInspectionHistoryStore,
    default_mcp_inspection_history_path,
    promote_history_call,
    prune_default_history_trace,
)
from .mcp_tool_registry import PROJECT_QUERY_CAPABILITY_NAME, TRAVERSAL_TOOL_NAME, build_mcp_tool_registry
from .seed_search import run_seed_search_traversal
from .builder_task_scoring import run_real_builder_task_scoring
from .context_projection_scoring import run_context_projection_arbitration_scoring

HOST_WORKSPACE_VERSION = "v1"
HOST_STATUS_TOOL_NAME = "ngraph.host.status_view"
HOST_TOOLS_TOOL_NAME = "ngraph.host.tool_registry_view"
HOST_HISTORY_VIEW_TOOL_NAME = "ngraph.host.history_view"
HOST_STREAM_TOOL_NAME = "ngraph.host.stream_view"
HOST_COCKPIT_TOOL_NAME = "ngraph.host.cockpit_view"
HOST_SEED_SEARCH_TOOL_NAME = "ngraph.host.search_seeds"
HOST_PROMOTE_CALL_TOOL_NAME = "ngraph.host.promote_call"
HOST_READ_PANELS_TOOL_NAME = "ngraph.host.read_panels"
HOST_BUILDER_SCORE_TOOL_NAME = "ngraph.host.builder_score_view"
HOST_PROJECTION_SCORE_TOOL_NAME = "ngraph.host.projection_score_view"
HOST_PANEL_ORDER = ("stream", "history", "cockpit", "status", "tools", "projection", "seed", "scores", "raw")
HOST_PANEL_TITLES = {
    "stream": "Command Stream",
    "history": "History Summary",
    "cockpit": "Cockpit",
    "status": "Status",
    "tools": "Tool Registry",
    "projection": "Active Projection",
    "seed": "Active Seed Flow",
    "scores": "Scores",
    "raw": "Raw JSON",
}


@dataclass(frozen=True)
class HostWorkspaceSnapshot:
    """Live host snapshot derived from durable history and current session cache."""

    version: str
    history_path: str
    record_count: int
    retention: dict[str, Any]
    recent_calls: tuple[HistoryInspectorCallSummary, ...]
    stream_items: tuple[InteractionStreamItem, ...]
    latest_builder_score: dict[str, Any] | None
    latest_projection_score: dict[str, Any] | None
    active_projection: dict[str, Any] | None
    active_seed: dict[str, Any] | None
    active_interaction: dict[str, Any] | None
    active_command: dict[str, Any] | None
    active_tab: str
    panels: dict[str, dict[str, Any]]
    raw_payload_cache: dict[str, Any]
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "history_path": self.history_path,
            "record_count": self.record_count,
            "retention": self.retention,
            "recent_calls": [call.to_dict() for call in self.recent_calls],
            "stream_items": [item.to_dict() for item in self.stream_items],
            "latest_builder_score": self.latest_builder_score,
            "latest_projection_score": self.latest_projection_score,
            "active_projection": self.active_projection,
            "active_seed": self.active_seed,
            "active_interaction": self.active_interaction,
            "active_command": self.active_command,
            "active_tab": self.active_tab,
            "panels": self.panels,
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
    active_tab: str = "stream"
    snapshot: HostWorkspaceSnapshot | None = None

    def refresh(self) -> HostWorkspaceSnapshot:
        self.snapshot = build_host_workspace_snapshot(
            self.project_root,
            history_path=self.history_path,
            history_limit=self.history_limit,
            active_call_id=self.active_call_id,
            active_tool_name=self.active_tool_name,
            active_tab=self.active_tab,
            raw_payload_cache=self.raw_payload_cache,
        )
        return self.snapshot

    def cache_payload(self, key: str, payload: dict[str, Any]) -> None:
        self.raw_payload_cache[key] = payload

    def set_active_call(self, call_id: str, tool_name: str) -> None:
        self.active_call_id = call_id
        self.active_tool_name = tool_name

    def set_active_tab(self, panel_name: str) -> None:
        if panel_name in HOST_PANEL_ORDER:
            self.active_tab = panel_name


def build_host_workspace_snapshot(
    project_root: Path | str,
    *,
    history_path: Path | str | None = None,
    history_limit: int = 12,
    active_call_id: str = "",
    active_tool_name: str = "",
    active_tab: str = "stream",
    raw_payload_cache: dict[str, Any] | None = None,
) -> HostWorkspaceSnapshot:
    """Build one canonical host snapshot from history, score artifacts, and live cache."""
    root = Path(project_root).resolve()
    resolved_history_path = Path(history_path) if history_path else default_mcp_inspection_history_path(root)
    retention_policy = prune_default_history_trace(root, resolved_history_path)
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
    resolved_active_tab = active_tab if active_tab in HOST_PANEL_ORDER else "stream"
    panels = build_host_panel_registry(
        history_path=resolved_history_path,
        record_count=history_payload.record_count,
        retention=dict(history_payload.raw.get("retention", {})),
        status_payload=cache.get("status") if isinstance(cache.get("status"), dict) else _build_status_payload(root),
        tool_registry_payload=(
            cache.get("tool_registry")
            if isinstance(cache.get("tool_registry"), dict)
            else build_mcp_tool_registry().to_dict()
        ),
        stream_payload=stream_payload.to_dict(),
        history_payload=history_payload.to_dict(),
        cockpit_payload=cockpit_payload.to_dict(),
        active_projection=active_projection,
        active_seed=active_seed,
        latest_builder_score=cockpit_payload.latest_builder_score,
        latest_projection_score=cockpit_payload.latest_projection_score,
        raw_payload_cache=cache,
        raw_payload={
            "retention_policy": retention_policy,
            "history": history_payload.to_dict(),
            "stream": stream_payload.to_dict(),
            "cockpit": cockpit_payload.to_dict(),
            "active_interaction": active_interaction,
            "active_projection": active_projection,
            "active_seed": active_seed,
        },
    )
    raw = {
        "retention_policy": retention_policy,
        "history": history_payload.to_dict(),
        "stream": stream_payload.to_dict(),
        "cockpit": cockpit_payload.to_dict(),
        "active_interaction": active_interaction,
        "active_projection": active_projection,
        "active_seed": active_seed,
        "active_tab": resolved_active_tab,
        "panels": panels,
    }
    return HostWorkspaceSnapshot(
        version=HOST_WORKSPACE_VERSION,
        history_path=str(resolved_history_path),
        record_count=history_payload.record_count,
        retention=dict(history_payload.raw.get("retention", {})),
        recent_calls=history_payload.calls,
        stream_items=stream_payload.items,
        latest_builder_score=cockpit_payload.latest_builder_score,
        latest_projection_score=cockpit_payload.latest_projection_score,
        active_projection=active_projection,
        active_seed=active_seed,
        active_interaction=active_interaction,
        active_command=active_command,
        active_tab=resolved_active_tab,
        panels=panels,
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
    elif command.tool_name == HOST_STATUS_TOOL_NAME:
        payload = _build_status_payload(root)
        host_state.cache_payload("status", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_TOOLS_TOOL_NAME:
        payload = build_mcp_tool_registry().to_dict()
        host_state.cache_payload("tool_registry", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_STREAM_TOOL_NAME:
        snapshot = host_state.refresh()
        payload = build_interaction_stream_payload(
            root,
            history_path=resolved_history_path,
            limit=int(command.payload.get("history_limit", history_limit)),
            tool_filter=str(command.payload.get("tool_filter", "")),
            layer_filter=str(command.payload.get("layer_filter", "")),
        ).to_dict()
        host_state.cache_payload("stream", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_COCKPIT_TOOL_NAME:
        snapshot = host_state.refresh()
        payload = build_visibility_cockpit_payload(
            root,
            history_path=resolved_history_path,
            limit=int(command.payload.get("history_limit", max(6, history_limit))),
            tool_filter=str(command.payload.get("tool_filter", "")),
            layer_filter=str(command.payload.get("layer_filter", "")),
        ).to_dict()
        host_state.cache_payload("cockpit", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_BUILDER_SCORE_TOOL_NAME:
        payload = run_real_builder_task_scoring(
            root,
            history_path=resolved_history_path,
            score_path=default_builder_task_score_path(root),
        ).to_dict()
        host_state.cache_payload("builder_score", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_PROJECTION_SCORE_TOOL_NAME:
        payload = run_context_projection_arbitration_scoring(
            root,
            history_path=resolved_history_path,
            score_path=default_context_projection_score_path(root),
        ).to_dict()
        host_state.cache_payload("projection_score", payload)
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_PROMOTE_CALL_TOOL_NAME:
        payload = promote_history_call(
            root,
            resolved_history_path,
            call_id=str(command.payload.get("call_id", "")),
            pinned=bool(command.payload.get("pinned", True)),
        )
        host_state.cache_payload("promotion", payload)
        record = payload.get("record") or {}
        if record.get("call_id"):
            host_state.set_active_call(str(record.get("call_id", "")), str(record.get("tool_name", "")))
        snapshot = host_state.refresh()
    elif command.tool_name == HOST_READ_PANELS_TOOL_NAME:
        snapshot = host_state.refresh()
        payload = read_host_panels(
            snapshot,
            mode=str(command.payload.get("mode", "active")),
            panel_name=str(command.payload.get("panel_name", "")),
        )
        host_state.cache_payload("panel_read", payload)
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


def read_host_panels(
    snapshot: HostWorkspaceSnapshot,
    *,
    mode: str = "active",
    panel_name: str = "",
) -> dict[str, Any]:
    """Read host panel contents for the active, named, or full workspace set."""
    normalized_mode = (mode or "active").strip().lower()
    normalized_panel = (panel_name or "").strip().lower()
    if normalized_mode not in {"active", "panel", "all"}:
        raise ValueError(f"Unsupported host panel read mode: {mode}")
    if normalized_mode == "active":
        active = snapshot.panels.get(snapshot.active_tab) or snapshot.panels.get("stream")
        return {
            "mode": "active",
            "active_tab": snapshot.active_tab,
            "panel_names": list(snapshot.panels.keys()),
            "panel": active,
        }
    if normalized_mode == "panel":
        if not normalized_panel:
            raise ValueError("panel_name is required when mode='panel'")
        panel = snapshot.panels.get(normalized_panel)
        if panel is None:
            raise ValueError(f"Unknown host panel: {panel_name}")
        return {
            "mode": "panel",
            "active_tab": snapshot.active_tab,
            "panel_names": list(snapshot.panels.keys()),
            "panel": panel,
        }
    return {
        "mode": "all",
        "active_tab": snapshot.active_tab,
        "panel_names": list(snapshot.panels.keys()),
        "panels": snapshot.panels,
    }


def build_host_panel_registry(
    *,
    history_path: Path,
    record_count: int,
    retention: dict[str, Any],
    status_payload: dict[str, Any],
    tool_registry_payload: dict[str, Any],
    stream_payload: dict[str, Any],
    history_payload: dict[str, Any],
    cockpit_payload: dict[str, Any],
    active_projection: dict[str, Any] | None,
    active_seed: dict[str, Any] | None,
    latest_builder_score: dict[str, Any] | None,
    latest_projection_score: dict[str, Any] | None,
    raw_payload_cache: dict[str, Any],
    raw_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build the canonical named panel registry for the host workspace."""
    scores_text = _scores_text(
        record_count=record_count,
        retention=retention,
        latest_builder_score=latest_builder_score,
        latest_projection_score=latest_projection_score,
        raw_payload_cache=raw_payload_cache,
    )
    return {
        "stream": {
            "name": "stream",
            "title": HOST_PANEL_TITLES["stream"],
            "text": _stream_text(
                record_count=record_count,
                history_path=history_path,
                retention=retention,
                stream_payload=stream_payload,
            ),
            "data": stream_payload,
        },
        "history": {
            "name": "history",
            "title": HOST_PANEL_TITLES["history"],
            "text": _history_text(
                record_count=record_count,
                history_path=history_path,
                retention=retention,
                history_payload=history_payload,
            ),
            "data": history_payload,
        },
        "cockpit": {
            "name": "cockpit",
            "title": HOST_PANEL_TITLES["cockpit"],
            "text": _cockpit_text(
                stream_payload=stream_payload,
                active_projection=active_projection,
                active_seed=active_seed,
                scores_text=scores_text,
            ),
            "data": cockpit_payload,
        },
        "status": {
            "name": "status",
            "title": HOST_PANEL_TITLES["status"],
            "text": _status_text(status_payload),
            "data": status_payload,
        },
        "tools": {
            "name": "tools",
            "title": HOST_PANEL_TITLES["tools"],
            "text": _tools_text(tool_registry_payload),
            "data": tool_registry_payload,
        },
        "projection": {
            "name": "projection",
            "title": HOST_PANEL_TITLES["projection"],
            "text": _projection_text(active_projection),
            "data": active_projection or {},
        },
        "seed": {
            "name": "seed",
            "title": HOST_PANEL_TITLES["seed"],
            "text": _seed_text(active_seed),
            "data": active_seed or {},
        },
        "scores": {
            "name": "scores",
            "title": HOST_PANEL_TITLES["scores"],
            "text": scores_text,
            "data": {
                "latest_builder_score": latest_builder_score,
                "latest_projection_score": latest_projection_score,
                "record_count": record_count,
                "retention": retention,
                "raw_payload_cache_keys": sorted(raw_payload_cache.keys()),
            },
        },
        "raw": {
            "name": "raw",
            "title": HOST_PANEL_TITLES["raw"],
            "text": json.dumps(raw_payload, indent=2, sort_keys=True),
            "data": raw_payload,
        },
    }


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


def _stream_text(
    *,
    record_count: int,
    history_path: Path,
    retention: dict[str, Any],
    stream_payload: dict[str, Any],
) -> str:
    items = stream_payload.get("items", [])
    lines = [
        "nGraphMANIFOLD Command Stream",
        f"records: {record_count}",
        f"history: {history_path}",
        (
            "rolling trace: "
            f"{retention.get('active_reasoning_count', 'n/a')} active / "
            f"{retention.get('durable_evidence_count', 'n/a')} durable / "
            f"limit={retention.get('rolling_trace_limit', 'n/a')}"
        ),
        "",
    ]
    if not items:
        lines.append("No interaction records yet.")
        return "\n".join(lines)
    for index, item in enumerate(items[:8], start=1):
        lines.append(f"[{index}] {item.get('captured_at', '')} {item.get('tool_name', '')} status={item.get('status', '')}")
        lines.append(f"    query: {item.get('query') or '(no query text)'}")
        lines.append(f"    result: {item.get('response') or '(no response summary)'}")
        if item.get("selected_layer"):
            lines.append(
                f"    layer={item.get('selected_layer')} kind={item.get('selected_kind') or 'n/a'} "
                f"score={item.get('selected_score')}"
            )
        if item.get("source_ref"):
            lines.append(f"    source={item.get('source_ref')}")
        lines.append("")
    return "\n".join(lines)


def _history_text(
    *,
    record_count: int,
    history_path: Path,
    retention: dict[str, Any],
    history_payload: dict[str, Any],
) -> str:
    calls = history_payload.get("calls", [])
    lines = [
        "nGraphMANIFOLD History Summary",
        f"records: {record_count}",
        f"history: {history_path}",
        (
            "rolling trace: "
            f"{retention.get('active_reasoning_count', 'n/a')} active / "
            f"{retention.get('durable_evidence_count', 'n/a')} durable / "
            f"limit={retention.get('rolling_trace_limit', 'n/a')}"
        ),
        "",
        "Recent Calls:",
    ]
    if not calls:
        lines.append("No persisted calls yet.")
        return "\n".join(lines)
    for call in calls[:10]:
        projection = ""
        if call.get("selected_layer"):
            projection = (
                f" selected_layer={call.get('selected_layer')} candidates={call.get('candidate_count')}"
            )
        task = f" task={call.get('task_id')}" if call.get("task_id") else ""
        lines.append(
            f"- {call.get('captured_at')} {call.get('tool_name')} score={call.get('aggregate_score')} "
            f"steps={call.get('step_count')} blockers={call.get('blocker_count')}{projection}{task}"
        )
    return "\n".join(lines)


def _projection_text(active_projection: dict[str, Any] | None) -> str:
    if not active_projection:
        return "No active projection yet."
    selected = active_projection.get("selected_candidate") or {}
    flow = active_projection.get("selected_flow") or {}
    lines = [
        "nGraphMANIFOLD Active Projection",
        f"query: {active_projection.get('query', 'n/a')}",
        f"selected_layer: {active_projection.get('selected_layer', 'n/a')}",
        f"selected_kind: {selected.get('kind', 'n/a')}",
        f"selected_score: {selected.get('score', 'n/a')}",
        f"source: {selected.get('source_ref', 'n/a')}",
        "",
        "Layer Summary:",
    ]
    for item in active_projection.get("layer_summaries", []):
        lines.append(
            f"- {item.get('name', 'n/a')} score={item.get('layer_score', 'n/a')} "
            f"candidates={item.get('candidate_count', 'n/a')}"
        )
    lines.append("")
    lines.append("Selected Flow:")
    for item in flow.get("objects", []):
        lines.append(
            f"- {item.get('role')} rank {item.get('rank')} {item.get('kind')} "
            f"score={item.get('score')}: {item.get('content_preview', '')}"
        )
    if not flow.get("objects"):
        lines.append("- n/a")
    return "\n".join(lines)


def _seed_text(active_seed: dict[str, Any] | None) -> str:
    if not active_seed:
        return "No active seed flow yet."
    selected = active_seed.get("selected_seed") or {}
    flow = active_seed.get("selected_flow") or {}
    traversal = active_seed.get("traversal_report") or {}
    lines = [
        "nGraphMANIFOLD Active Seed Flow",
        f"query: {active_seed.get('query', 'n/a')}",
        f"candidate_count: {active_seed.get('candidate_count', 'n/a')}",
        f"selected_source: {selected.get('source_ref', 'n/a')}",
        f"selected_kind: {selected.get('kind', 'n/a')}",
        f"tool: {active_seed.get('tool_name', 'n/a')}",
        f"steps: {len(traversal.get('steps', []))}",
        f"blockers: {len(traversal.get('blockers', []))}",
        "",
        "Seed Flow:",
    ]
    for item in flow.get("objects", []):
        lines.append(
            f"- {item.get('role')} block {item.get('block_index')} {item.get('kind')}: "
            f"{item.get('content_preview', '')}"
        )
    if not flow.get("objects"):
        lines.append("- n/a")
    return "\n".join(lines)


def _scores_text(
    *,
    record_count: int,
    retention: dict[str, Any],
    latest_builder_score: dict[str, Any] | None,
    latest_projection_score: dict[str, Any] | None,
    raw_payload_cache: dict[str, Any],
) -> str:
    builder_report = (latest_builder_score or {}).get("usefulness_report", {})
    projection_report = (latest_projection_score or {}).get("usefulness_report", {})
    lines = [
        "nGraphMANIFOLD Score Summaries",
        f"builder_score: {builder_report.get('aggregate_score', 'n/a')} accepted={(latest_builder_score or {}).get('meets_acceptance', 'n/a')}",
        f"projection_score: {projection_report.get('aggregate_score', 'n/a')} accepted={(latest_projection_score or {}).get('meets_acceptance', 'n/a')}",
        f"history_records: {record_count}",
        (
            "rolling_trace: "
            f"{retention.get('active_reasoning_count', 'n/a')} active / "
            f"{retention.get('durable_evidence_count', 'n/a')} durable"
        ),
        f"raw_cache_keys: {', '.join(sorted(raw_payload_cache.keys())) or 'none'}",
    ]
    return "\n".join(lines)


def _status_text(status_payload: dict[str, Any]) -> str:
    lines = [
        "nGraphMANIFOLD Status",
        f"status: {status_payload.get('status', 'n/a')}",
        f"project_root: {status_payload.get('project_root', 'n/a')}",
        f"active_tranche: {status_payload.get('active_tranche', 'n/a')}",
        f"next_tranche: {status_payload.get('next_tranche', 'n/a')}",
    ]
    return "\n".join(lines)


def _tools_text(tool_registry_payload: dict[str, Any]) -> str:
    registrations = tool_registry_payload.get("registrations", [])
    lines = [
        "nGraphMANIFOLD Tool Registry",
        f"version: {tool_registry_payload.get('version', 'n/a')}",
        f"registered_tools: {len(registrations)}",
        "",
    ]
    if not registrations:
        lines.append("No tool registrations available.")
        return "\n".join(lines)
    for item in registrations:
        lines.append(
            f"- {item.get('tool_name', 'n/a')} capability={item.get('capability_name', 'n/a')} "
            f"readiness={item.get('readiness', 'n/a')}"
        )
    return "\n".join(lines)


def _cockpit_text(
    *,
    stream_payload: dict[str, Any],
    active_projection: dict[str, Any] | None,
    active_seed: dict[str, Any] | None,
    scores_text: str,
) -> str:
    lines = [
        "nGraphMANIFOLD Cockpit",
        "",
        scores_text,
        "",
        "Latest Projection:",
    ]
    projection = active_projection or {}
    selected = projection.get("selected_candidate") or {}
    if projection:
        lines.extend(
            [
                f"- query: {projection.get('query', 'n/a')}",
                f"- selected_layer: {projection.get('selected_layer', 'n/a')}",
                f"- selected_kind: {selected.get('kind', 'n/a')}",
                f"- selected_score: {selected.get('score', 'n/a')}",
                f"- source: {selected.get('source_ref', 'n/a')}",
            ]
        )
    else:
        lines.append("- none")
    lines.extend(["", "Latest Seed:"])
    seed = active_seed or {}
    selected_seed = seed.get("selected_seed") or {}
    if seed:
        lines.extend(
            [
                f"- query: {seed.get('query', 'n/a')}",
                f"- selected_source: {selected_seed.get('source_ref', 'n/a')}",
                f"- steps: {len((seed.get('traversal_report') or {}).get('steps', []))}",
                f"- blockers: {len((seed.get('traversal_report') or {}).get('blockers', []))}",
            ]
        )
    else:
        lines.append("- none")
    lines.extend(["", "Recent Stream:"])
    items = stream_payload.get("items", [])
    if not items:
        lines.append("- none")
    for index, item in enumerate(items[:6], start=1):
        lines.append(f"[{index}] {item.get('captured_at', '')} {item.get('tool_name', '')} {item.get('query') or '(no query text)'}")
        lines.append(f"    {item.get('response') or '(no response summary)'}")
    return "\n".join(lines)


def _build_status_payload(project_root: Path) -> dict[str, Any]:
    settings = AppSettings(
        project_root=project_root,
        docs_root=project_root / "_docs",
        data_root=project_root / "data",
    )
    status = ApplicationEngine(settings).status()
    return {
        "status": status.status,
        "project_root": str(status.project_root),
        "active_tranche": status.active_tranche,
        "next_tranche": status.next_tranche,
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
