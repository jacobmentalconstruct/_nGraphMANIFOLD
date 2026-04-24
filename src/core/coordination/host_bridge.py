"""Local file-backed bridge for targeting an already-open host workspace."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .host_workspace import SharedHostState, dispatch_host_command
from .interaction_spine import CommandEnvelope, PROJECT_QUERY_TOOL_NAME, command_envelope_from_dict

HOST_BRIDGE_VERSION = "v1"
DEFAULT_HOST_BRIDGE_TIMEOUT_MS = 5000
DEFAULT_HOST_BRIDGE_HEAVY_TIMEOUT_MS = 180000
DEFAULT_HOST_BRIDGE_MEDIUM_TIMEOUT_MS = 30000
DEFAULT_HOST_BRIDGE_POLL_INTERVAL_MS = 750
DEFAULT_HOST_BRIDGE_WAIT_INTERVAL_MS = 100
DEFAULT_HOST_BRIDGE_STALE_AFTER_SECONDS = 5.0
DEFAULT_HOST_BRIDGE_FILE_RETENTION_SECONDS = 300.0
DEFAULT_HOST_BRIDGE_ATTACH_GRACE_MS = 2500


class HostBridgeError(RuntimeError):
    """Base error for local host bridge failures."""


class HostBridgeUnavailableError(HostBridgeError):
    """Raised when no live host bridge session is available."""


class HostBridgeTimeoutError(HostBridgeError):
    """Raised when a bridged request does not receive a response in time."""


@dataclass(frozen=True)
class HostBridgeSessionManifest:
    """Published manifest for one live UI host bridge session."""

    version: str
    session_id: str
    host_pid: int
    status: str
    created_at: str
    heartbeat_at: str
    supported_tools: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "session_id": self.session_id,
            "host_pid": self.host_pid,
            "status": self.status,
            "created_at": self.created_at,
            "heartbeat_at": self.heartbeat_at,
            "supported_tools": list(self.supported_tools),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HostBridgeSessionManifest":
        return cls(
            version=str(payload.get("version", HOST_BRIDGE_VERSION)),
            session_id=str(payload.get("session_id", "")),
            host_pid=int(payload.get("host_pid", 0)),
            status=str(payload.get("status", "active")),
            created_at=str(payload.get("created_at", "")),
            heartbeat_at=str(payload.get("heartbeat_at", "")),
            supported_tools=tuple(str(item) for item in payload.get("supported_tools", ())),
        )

    def is_stale(self, *, stale_after_seconds: float = DEFAULT_HOST_BRIDGE_STALE_AFTER_SECONDS) -> bool:
        heartbeat = _parse_timestamp(self.heartbeat_at)
        if heartbeat is None:
            return True
        return (datetime.now(timezone.utc) - heartbeat).total_seconds() > stale_after_seconds


@dataclass(frozen=True)
class HostBridgeRequest:
    """One external request targeting the already-open host workspace."""

    version: str
    request_id: str
    session_id: str
    created_at: str
    command: CommandEnvelope
    bridge_policy: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "command": self.command.to_dict(),
            "bridge_policy": self.bridge_policy,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HostBridgeRequest":
        return cls(
            version=str(payload.get("version", HOST_BRIDGE_VERSION)),
            request_id=str(payload.get("request_id", "")),
            session_id=str(payload.get("session_id", "")),
            created_at=str(payload.get("created_at", "")),
            command=command_envelope_from_dict(dict(payload.get("command", {}))),
            bridge_policy=dict(payload.get("bridge_policy", {}) or {}),
        )


@dataclass(frozen=True)
class HostBridgeResponse:
    """Response written by the live host after processing one bridge request."""

    version: str
    request_id: str
    session_id: str
    responded_at: str
    status: str
    command_id: str
    tool_name: str
    payload: dict[str, Any] | None
    error: dict[str, Any] | None = None
    snapshot_summary: dict[str, Any] | None = None
    bridge_policy: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "responded_at": self.responded_at,
            "status": self.status,
            "command_id": self.command_id,
            "tool_name": self.tool_name,
            "payload": self.payload,
            "error": self.error,
            "snapshot_summary": self.snapshot_summary,
            "bridge_policy": self.bridge_policy,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HostBridgeResponse":
        return cls(
            version=str(payload.get("version", HOST_BRIDGE_VERSION)),
            request_id=str(payload.get("request_id", "")),
            session_id=str(payload.get("session_id", "")),
            responded_at=str(payload.get("responded_at", "")),
            status=str(payload.get("status", "error")),
            command_id=str(payload.get("command_id", "")),
            tool_name=str(payload.get("tool_name", "")),
            payload=payload.get("payload"),
            error=payload.get("error"),
            snapshot_summary=payload.get("snapshot_summary"),
            bridge_policy=dict(payload.get("bridge_policy", {}) or {}),
        )


def resolve_host_bridge_timeout_policy(
    tool_name: str,
    *,
    requested_timeout_ms: int | None = None,
) -> dict[str, Any]:
    """Return the effective timeout policy for one bridged command."""
    command_default_ms = _command_default_timeout_ms(tool_name)
    timeout_ms = command_default_ms
    timeout_source = "command_policy_default"
    if requested_timeout_ms is not None:
        timeout_ms = max(1, int(requested_timeout_ms))
        timeout_source = "caller_override"
    runtime_class = "heavy" if command_default_ms >= DEFAULT_HOST_BRIDGE_HEAVY_TIMEOUT_MS else "medium" if command_default_ms > DEFAULT_HOST_BRIDGE_TIMEOUT_MS else "standard"
    return {
        "tool_name": tool_name,
        "timeout_ms": timeout_ms,
        "timeout_source": timeout_source,
        "command_default_timeout_ms": command_default_ms,
        "global_default_timeout_ms": DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
        "runtime_class": runtime_class,
        "supports_override": True,
    }


def build_host_bridge_timeout_policy_manifest() -> dict[str, Any]:
    """Return a compact machine-readable summary of bridge timeout defaults."""
    tool_names = (
        PROJECT_QUERY_TOOL_NAME,
        "ngraph.host.status_view",
        "ngraph.host.tool_registry_view",
        "ngraph.host.search_seeds",
        "ngraph.host.history_view",
        "ngraph.host.stream_view",
        "ngraph.host.cockpit_view",
        "ngraph.host.builder_score_view",
        "ngraph.host.projection_score_view",
        "ngraph.host.promote_call",
        "ngraph.host.read_panels",
    )
    return {
        "transport_kind": "file_backed_local",
        "global_default_timeout_ms": DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
        "attach_grace_ms": DEFAULT_HOST_BRIDGE_ATTACH_GRACE_MS,
        "stale_after_seconds": DEFAULT_HOST_BRIDGE_STALE_AFTER_SECONDS,
        "file_retention_seconds": DEFAULT_HOST_BRIDGE_FILE_RETENTION_SECONDS,
        "poll_interval_ms": DEFAULT_HOST_BRIDGE_POLL_INTERVAL_MS,
        "wait_interval_ms": DEFAULT_HOST_BRIDGE_WAIT_INTERVAL_MS,
        "tool_policies": {
            tool_name: resolve_host_bridge_timeout_policy(tool_name)
            for tool_name in tool_names
        },
    }


def build_host_bridge_runtime_snapshot(project_root: Path | str) -> dict[str, Any]:
    """Return a compact runtime snapshot of the current local bridge state."""
    bridge_root = default_host_bridge_root(project_root)
    request_dir = _request_dir(bridge_root)
    response_dir = _response_dir(bridge_root)
    session = load_host_bridge_session(project_root)
    heartbeat_age_seconds = 0.0
    if session is not None:
        heartbeat = _parse_timestamp(session.heartbeat_at)
        if heartbeat is not None:
            heartbeat_age_seconds = round(
                (datetime.now(timezone.utc) - heartbeat).total_seconds(),
                3,
            )
    return {
        "transport_kind": "file_backed_local",
        "bridge_root": str(bridge_root),
        "session_present": session is not None,
        "session_id": session.session_id if session is not None else "",
        "session_status": session.status if session is not None else "inactive",
        "supported_tool_count": len(session.supported_tools) if session is not None else 0,
        "pending_request_count": sum(1 for _ in request_dir.glob("*.json")) if request_dir.exists() else 0,
        "pending_response_count": sum(1 for _ in response_dir.glob("*.json")) if response_dir.exists() else 0,
        "heartbeat_age_seconds": heartbeat_age_seconds,
    }


def default_host_bridge_root(project_root: Path | str) -> Path:
    """Return the project-owned host bridge root."""
    return Path(project_root).resolve() / "data" / "host_bridge"


def default_host_bridge_supported_tools() -> tuple[str, ...]:
    """Return the tools that may target the live host in bridge v1."""
    from .host_workspace import (
        HOST_BUILDER_SCORE_TOOL_NAME,
        HOST_COCKPIT_TOOL_NAME,
        HOST_HISTORY_VIEW_TOOL_NAME,
        HOST_PROMOTE_CALL_TOOL_NAME,
        HOST_PROJECTION_SCORE_TOOL_NAME,
        HOST_READ_PANELS_TOOL_NAME,
        HOST_SEED_SEARCH_TOOL_NAME,
        HOST_STATUS_TOOL_NAME,
        HOST_STREAM_TOOL_NAME,
        HOST_TOOLS_TOOL_NAME,
    )

    return (
        PROJECT_QUERY_TOOL_NAME,
        HOST_STATUS_TOOL_NAME,
        HOST_TOOLS_TOOL_NAME,
        HOST_SEED_SEARCH_TOOL_NAME,
        HOST_HISTORY_VIEW_TOOL_NAME,
        HOST_STREAM_TOOL_NAME,
        HOST_COCKPIT_TOOL_NAME,
        HOST_BUILDER_SCORE_TOOL_NAME,
        HOST_PROJECTION_SCORE_TOOL_NAME,
        HOST_PROMOTE_CALL_TOOL_NAME,
        HOST_READ_PANELS_TOOL_NAME,
    )


def activate_host_bridge_session(
    project_root: Path | str,
    *,
    supported_tools: tuple[str, ...] | None = None,
    created_at: str | None = None,
) -> HostBridgeSessionManifest:
    """Create or refresh the live host bridge session manifest."""
    bridge_root = default_host_bridge_root(project_root)
    _ensure_bridge_dirs(bridge_root)
    cleanup_host_bridge_transport(
        project_root,
        stale_after_seconds=DEFAULT_HOST_BRIDGE_FILE_RETENTION_SECONDS,
    )
    timestamp = created_at or _utc_now()
    manifest = HostBridgeSessionManifest(
        version=HOST_BRIDGE_VERSION,
        session_id=f"hostsession:{HOST_BRIDGE_VERSION}:{uuid.uuid4().hex}",
        host_pid=os.getpid(),
        status="active",
        created_at=timestamp,
        heartbeat_at=timestamp,
        supported_tools=tuple(supported_tools or default_host_bridge_supported_tools()),
    )
    _write_json_atomic(_session_manifest_path(bridge_root), manifest.to_dict())
    return manifest


def heartbeat_host_bridge_session(
    project_root: Path | str,
    session_id: str,
) -> HostBridgeSessionManifest:
    """Refresh the heartbeat for the active host session."""
    bridge_root = default_host_bridge_root(project_root)
    manifest = load_host_bridge_session(project_root, include_stale=True)
    if manifest is None or manifest.session_id != session_id:
        raise HostBridgeUnavailableError("No matching host bridge session is active.")
    updated = HostBridgeSessionManifest(
        version=manifest.version,
        session_id=manifest.session_id,
        host_pid=manifest.host_pid,
        status="active",
        created_at=manifest.created_at,
        heartbeat_at=_utc_now(),
        supported_tools=manifest.supported_tools,
    )
    _write_json_atomic(_session_manifest_path(bridge_root), updated.to_dict())
    return updated


def close_host_bridge_session(project_root: Path | str, session_id: str) -> None:
    """Close the active host bridge session if it matches the current manifest."""
    session_path = _session_manifest_path(default_host_bridge_root(project_root))
    if not session_path.exists():
        return
    manifest = load_host_bridge_session(project_root, include_stale=True)
    if manifest is None or manifest.session_id != session_id:
        return
    try:
        session_path.unlink()
    except OSError:
        return


def load_host_bridge_session(
    project_root: Path | str,
    *,
    stale_after_seconds: float = DEFAULT_HOST_BRIDGE_STALE_AFTER_SECONDS,
    include_stale: bool = False,
) -> HostBridgeSessionManifest | None:
    """Load the current host bridge session manifest when available."""
    session_path = _session_manifest_path(default_host_bridge_root(project_root))
    payload = _read_json(session_path)
    if payload is None:
        return None
    manifest = HostBridgeSessionManifest.from_dict(payload)
    if include_stale:
        return manifest
    if manifest.is_stale(stale_after_seconds=stale_after_seconds):
        try:
            session_path.unlink()
        except OSError:
            pass
        return None
    return manifest


def pending_host_bridge_request_count(project_root: Path | str) -> int:
    """Return the current count of pending bridge request files."""
    request_dir = _request_dir(default_host_bridge_root(project_root))
    if not request_dir.exists():
        return 0
    return sum(1 for _ in request_dir.glob("*.json"))


def cleanup_host_bridge_transport(
    project_root: Path | str,
    *,
    stale_after_seconds: float = DEFAULT_HOST_BRIDGE_FILE_RETENTION_SECONDS,
) -> dict[str, int]:
    """Remove stale bridge transport files while preserving current live state."""
    bridge_root = default_host_bridge_root(project_root)
    if not bridge_root.exists():
        return {"removed_requests": 0, "removed_responses": 0, "removed_session": 0}
    now = datetime.now(timezone.utc)
    removed_requests = _cleanup_dir_by_age(_request_dir(bridge_root), now, stale_after_seconds=stale_after_seconds)
    removed_responses = _cleanup_dir_by_age(
        _response_dir(bridge_root),
        now,
        stale_after_seconds=stale_after_seconds,
    )
    removed_session = 0
    session = load_host_bridge_session(project_root, stale_after_seconds=stale_after_seconds, include_stale=True)
    if session is not None and session.is_stale(stale_after_seconds=stale_after_seconds):
        _safe_unlink(_session_manifest_path(bridge_root))
        removed_session = 1
    return {
        "removed_requests": removed_requests,
        "removed_responses": removed_responses,
        "removed_session": removed_session,
    }


def enqueue_host_bridge_request(
    project_root: Path | str,
    command: CommandEnvelope,
    *,
    session: HostBridgeSessionManifest | None = None,
    bridge_policy: dict[str, Any] | None = None,
) -> HostBridgeRequest:
    """Write one bridge request file targeting the current live host session."""
    manifest = session or require_live_host_bridge_session(project_root)
    if command.tool_name not in manifest.supported_tools:
        raise HostBridgeError(f"Tool is not bridge-enabled: {command.tool_name}")
    request = HostBridgeRequest(
        version=HOST_BRIDGE_VERSION,
        request_id=f"hostreq:{HOST_BRIDGE_VERSION}:{uuid.uuid4().hex}",
        session_id=manifest.session_id,
        created_at=_utc_now(),
        command=command,
        bridge_policy=dict(bridge_policy or {}),
    )
    bridge_root = default_host_bridge_root(project_root)
    _ensure_bridge_dirs(bridge_root)
    path = _request_file_path(bridge_root, request.request_id, request.created_at)
    _write_json_atomic(path, request.to_dict())
    return request


def process_pending_host_bridge_requests(
    project_root: Path | str,
    state: SharedHostState,
    *,
    session: HostBridgeSessionManifest | None = None,
    history_limit: int | None = None,
    max_requests: int = 4,
) -> tuple[HostBridgeResponse, ...]:
    """Process pending bridge requests through the shared host dispatcher."""
    manifest = session or load_host_bridge_session(project_root)
    if manifest is None:
        return ()
    cleanup_host_bridge_transport(
        project_root,
        stale_after_seconds=DEFAULT_HOST_BRIDGE_FILE_RETENTION_SECONDS,
    )
    bridge_root = default_host_bridge_root(project_root)
    responses: list[HostBridgeResponse] = []
    for request_path in sorted(_request_dir(bridge_root).glob("*.json"))[: max(1, int(max_requests))]:
        payload = _read_json(request_path)
        if payload is None:
            _safe_unlink(request_path)
            continue
        request = HostBridgeRequest.from_dict(payload)
        response = _process_one_bridge_request(
            Path(project_root).resolve(),
            request,
            state,
            manifest=manifest,
            history_limit=history_limit or state.history_limit,
        )
        _write_json_atomic(_response_file_path(bridge_root, request.request_id), response.to_dict())
        _safe_unlink(request_path)
        responses.append(response)
    return tuple(responses)


def wait_for_host_bridge_response(
    project_root: Path | str,
    request_id: str,
    *,
    timeout_ms: int = DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
    wait_interval_ms: int = DEFAULT_HOST_BRIDGE_WAIT_INTERVAL_MS,
    delete_after_read: bool = True,
) -> HostBridgeResponse:
    """Wait for the host to respond to a previously enqueued bridge request."""
    response_path = _response_file_path(default_host_bridge_root(project_root), request_id)
    deadline = time.monotonic() + max(1, int(timeout_ms)) / 1000.0
    while time.monotonic() < deadline:
        payload = _read_json(response_path)
        if payload is not None:
            if delete_after_read:
                _safe_unlink(response_path)
            return HostBridgeResponse.from_dict(payload)
        time.sleep(max(10, int(wait_interval_ms)) / 1000.0)
    raise HostBridgeTimeoutError(f"Timed out waiting for host bridge response: {request_id}")


def dispatch_command_via_host_bridge(
    project_root: Path | str,
    command: CommandEnvelope,
    *,
    timeout_ms: int | None = None,
    wait_interval_ms: int = DEFAULT_HOST_BRIDGE_WAIT_INTERVAL_MS,
) -> HostBridgeResponse:
    """Send one supported command to the live host and wait for the response."""
    manifest = require_live_host_bridge_session(project_root)
    bridge_policy = resolve_host_bridge_timeout_policy(
        command.tool_name,
        requested_timeout_ms=timeout_ms,
    )
    request = enqueue_host_bridge_request(
        project_root,
        command,
        session=manifest,
        bridge_policy=bridge_policy,
    )
    response = wait_for_host_bridge_response(
        project_root,
        request.request_id,
        timeout_ms=int(bridge_policy["timeout_ms"]),
        wait_interval_ms=wait_interval_ms,
    )
    if response.status != "ok":
        raise HostBridgeError(str((response.error or {}).get("message", "Host bridge request failed.")))
    return response


def require_live_host_bridge_session(project_root: Path | str) -> HostBridgeSessionManifest:
    """Return the live host bridge session manifest or raise an error."""
    manifest = load_host_bridge_session(project_root)
    if manifest is None:
        raise HostBridgeUnavailableError("No live host bridge session is available.")
    return manifest


def wait_for_live_host_bridge_session(
    project_root: Path | str,
    *,
    timeout_ms: int = DEFAULT_HOST_BRIDGE_ATTACH_GRACE_MS,
    wait_interval_ms: int = DEFAULT_HOST_BRIDGE_WAIT_INTERVAL_MS,
) -> HostBridgeSessionManifest | None:
    """Wait briefly for a live host session to appear during startup churn."""
    deadline = time.monotonic() + max(1, int(timeout_ms)) / 1000.0
    while time.monotonic() < deadline:
        manifest = load_host_bridge_session(project_root)
        if manifest is not None:
            return manifest
        time.sleep(max(10, int(wait_interval_ms)) / 1000.0)
    return load_host_bridge_session(project_root)


def _process_one_bridge_request(
    project_root: Path,
    request: HostBridgeRequest,
    state: SharedHostState,
    *,
    manifest: HostBridgeSessionManifest,
    history_limit: int,
) -> HostBridgeResponse:
    if request.session_id != manifest.session_id:
        return _bridge_error_response(
            request,
            message="Request targeted a different host session.",
            code="session_mismatch",
        )
    if request.command.tool_name not in manifest.supported_tools:
        return _bridge_error_response(
            request,
            message=f"Tool is not bridge-enabled: {request.command.tool_name}",
            code="unsupported_tool",
        )
    try:
        result = dispatch_host_command(
            project_root,
            request.command,
            state=state,
            history_limit=history_limit,
        )
    except Exception as exc:
        return _bridge_error_response(
            request,
            message=str(exc),
            code="dispatch_failed",
        )
    return HostBridgeResponse(
        version=HOST_BRIDGE_VERSION,
        request_id=request.request_id,
        session_id=manifest.session_id,
        responded_at=_utc_now(),
        status="ok",
        command_id=request.command.command_id,
        tool_name=request.command.tool_name,
        payload=result.payload,
        snapshot_summary={
            "record_count": result.snapshot.record_count,
            "active_tool_name": result.snapshot.active_command.get("tool_name", "")
            if result.snapshot.active_command
            else "",
            "active_call_id": result.snapshot.active_interaction.get("call_id", "")
            if result.snapshot.active_interaction
            else "",
        },
        bridge_policy=dict(request.bridge_policy or {}),
    )


def _bridge_error_response(
    request: HostBridgeRequest,
    *,
    message: str,
    code: str,
) -> HostBridgeResponse:
    return HostBridgeResponse(
        version=HOST_BRIDGE_VERSION,
        request_id=request.request_id,
        session_id=request.session_id,
        responded_at=_utc_now(),
        status="error",
        command_id=request.command.command_id,
        tool_name=request.command.tool_name,
        payload=None,
        error={"code": code, "message": message},
        bridge_policy=dict(request.bridge_policy or {}),
    )


def _ensure_bridge_dirs(bridge_root: Path) -> None:
    bridge_root.mkdir(parents=True, exist_ok=True)
    _request_dir(bridge_root).mkdir(parents=True, exist_ok=True)
    _response_dir(bridge_root).mkdir(parents=True, exist_ok=True)


def _session_manifest_path(bridge_root: Path) -> Path:
    return bridge_root / "session.json"


def _request_dir(bridge_root: Path) -> Path:
    return bridge_root / "requests"


def _response_dir(bridge_root: Path) -> Path:
    return bridge_root / "responses"


def _request_file_path(bridge_root: Path, request_id: str, created_at: str) -> Path:
    safe_stamp = created_at.replace(":", "").replace("-", "").replace("T", "_").replace("Z", "Z")
    safe_request = request_id.replace(":", "_")
    return _request_dir(bridge_root) / f"{safe_stamp}_{safe_request}.json"


def _response_file_path(bridge_root: Path, request_id: str) -> Path:
    safe_request = request_id.replace(":", "_")
    return _response_dir(bridge_root) / f"{safe_request}.json"


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp-{os.getpid()}-{uuid.uuid4().hex}")
    text = json.dumps(payload, indent=2, sort_keys=True)
    temp_path.write_text(text, encoding="utf-8")
    temp_path.replace(path)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        return


def _cleanup_dir_by_age(
    directory: Path,
    now: datetime,
    *,
    stale_after_seconds: float,
) -> int:
    if not directory.exists():
        return 0
    removed = 0
    for path in directory.glob("*.json"):
        try:
            modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if (now - modified).total_seconds() > stale_after_seconds:
            _safe_unlink(path)
            removed += 1
    return removed


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _command_default_timeout_ms(tool_name: str) -> int:
    if tool_name == "ngraph.host.builder_score_view":
        return DEFAULT_HOST_BRIDGE_HEAVY_TIMEOUT_MS
    if tool_name == "ngraph.host.projection_score_view":
        return DEFAULT_HOST_BRIDGE_MEDIUM_TIMEOUT_MS
    return DEFAULT_HOST_BRIDGE_TIMEOUT_MS
