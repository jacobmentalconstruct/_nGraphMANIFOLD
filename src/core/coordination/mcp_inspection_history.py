"""Persistent history for local MCP inspection captures."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from src.core.representation.canonical import canonical_json

MCP_INSPECTION_HISTORY_VERSION = "v1"
DEFAULT_MCP_ROLLING_TRACE_LIMIT = 250

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS mcp_inspection_history (
    call_id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    capability_name TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    status TEXT NOT NULL,
    aggregate_score REAL NOT NULL,
    pinned INTEGER NOT NULL DEFAULT 0,
    operator_metadata_json TEXT NOT NULL DEFAULT '{}',
    call_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mcp_inspection_history_captured_at
ON mcp_inspection_history(captured_at);

CREATE INDEX IF NOT EXISTS idx_mcp_inspection_history_tool
ON mcp_inspection_history(tool_name);
"""


@dataclass(frozen=True)
class McpInspectionHistoryRecord:
    """One persisted registered MCP tool call and raw capture."""

    call_id: str
    tool_name: str
    capability_name: str
    captured_at: str
    status: str
    aggregate_score: float
    pinned: bool
    operator_metadata: dict[str, Any]
    call: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "capability_name": self.capability_name,
            "captured_at": self.captured_at,
            "status": self.status,
            "aggregate_score": self.aggregate_score,
            "pinned": self.pinned,
            "operator_metadata": self.operator_metadata,
            "call": self.call,
        }


@dataclass(frozen=True)
class McpInspectionRetentionSummary:
    """Readable summary of active trace vs durable retained records."""

    rolling_trace_limit: int
    active_reasoning_count: int
    durable_evidence_count: int
    prunable_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "rolling_trace_limit": self.rolling_trace_limit,
            "active_reasoning_count": self.active_reasoning_count,
            "durable_evidence_count": self.durable_evidence_count,
            "prunable_count": self.prunable_count,
        }


@dataclass(frozen=True)
class McpInspectionHistorySnapshot:
    """Inspectable summary plus recent records."""

    history_path: str
    version: str
    record_count: int
    retention: McpInspectionRetentionSummary
    records: tuple[McpInspectionHistoryRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "history_path": self.history_path,
            "version": self.version,
            "record_count": self.record_count,
            "retention": self.retention.to_dict(),
            "records": [record.to_dict() for record in self.records],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


class McpInspectionHistoryStore:
    """SQLite-backed store for MCP inspection call history."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        if self.db_path != Path(":memory:"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(mcp_inspection_history)").fetchall()
            }
            if "pinned" not in columns:
                conn.execute(
                    "ALTER TABLE mcp_inspection_history ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0"
                )
            if "operator_metadata_json" not in columns:
                conn.execute(
                    "ALTER TABLE mcp_inspection_history ADD COLUMN operator_metadata_json TEXT NOT NULL DEFAULT '{}'"
                )
            conn.execute("PRAGMA user_version = 1")

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_call(self, call: dict[str, Any]) -> McpInspectionHistoryRecord:
        """Persist one registered tool call result."""
        self.initialize()
        record = _record_from_call(call)
        with self.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO mcp_inspection_history(
                    call_id, tool_name, capability_name, captured_at, status,
                    aggregate_score, pinned, operator_metadata_json, call_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.call_id,
                    record.tool_name,
                    record.capability_name,
                    record.captured_at,
                    record.status,
                    record.aggregate_score,
                    1 if record.pinned else 0,
                    canonical_json(record.operator_metadata),
                    canonical_json(record.call),
                ),
            )
        return record

    def update_call_record(
        self,
        call_id: str,
        *,
        pinned: bool | None = None,
        operator_metadata: dict[str, Any] | None = None,
    ) -> bool:
        self.initialize()
        current = self.get_call(call_id)
        if current is None:
            return False
        next_pinned = current.pinned if pinned is None else bool(pinned)
        next_metadata = dict(current.operator_metadata)
        if operator_metadata:
            next_metadata.update(operator_metadata)
        with self.connection() as conn:
            cursor = conn.execute(
                """
                UPDATE mcp_inspection_history
                SET pinned = ?, operator_metadata_json = ?
                WHERE call_id = ?
                """,
                (
                    1 if next_pinned else 0,
                    canonical_json(next_metadata),
                    str(call_id),
                ),
            )
            return int(cursor.rowcount) > 0

    def pin_call(self, call_id: str, *, pinned: bool = True) -> bool:
        return self.update_call_record(call_id, pinned=pinned)

    def prune_rolling_trace(self, *, rolling_trace_limit: int = DEFAULT_MCP_ROLLING_TRACE_LIMIT) -> int:
        self.initialize()
        bounded_limit = max(1, int(rolling_trace_limit))
        with self.connection() as conn:
            prunable_rows = conn.execute(
                """
                SELECT call_id
                FROM mcp_inspection_history
                WHERE pinned = 0
                ORDER BY captured_at DESC, call_id DESC
                LIMIT -1 OFFSET ?
                """,
                (bounded_limit,),
            ).fetchall()
            if not prunable_rows:
                return 0
            call_ids = tuple(str(row["call_id"]) for row in prunable_rows)
            placeholders = ",".join("?" for _ in call_ids)
            conn.execute(
                f"DELETE FROM mcp_inspection_history WHERE call_id IN ({placeholders})",
                call_ids,
            )
            return len(call_ids)

    def retention_summary(
        self,
        *,
        rolling_trace_limit: int = DEFAULT_MCP_ROLLING_TRACE_LIMIT,
    ) -> McpInspectionRetentionSummary:
        self.initialize()
        bounded_limit = max(1, int(rolling_trace_limit))
        with self.connection() as conn:
            durable_count = int(
                conn.execute(
                    "SELECT COUNT(*) FROM mcp_inspection_history WHERE pinned = 1"
                ).fetchone()[0]
            )
            unpinned_count = int(
                conn.execute(
                    "SELECT COUNT(*) FROM mcp_inspection_history WHERE pinned = 0"
                ).fetchone()[0]
            )
        active_reasoning_count = min(unpinned_count, bounded_limit)
        prunable_count = max(0, unpinned_count - bounded_limit)
        return McpInspectionRetentionSummary(
            rolling_trace_limit=bounded_limit,
            active_reasoning_count=active_reasoning_count,
            durable_evidence_count=durable_count,
            prunable_count=prunable_count,
        )

    def latest(self) -> McpInspectionHistoryRecord | None:
        self.initialize()
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM mcp_inspection_history
                ORDER BY captured_at DESC, call_id DESC
                LIMIT 1
                """
            ).fetchone()
        return _record_from_row(row) if row is not None else None

    def get_call(self, call_id: str) -> McpInspectionHistoryRecord | None:
        self.initialize()
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM mcp_inspection_history
                WHERE call_id = ?
                LIMIT 1
                """,
                (str(call_id),),
            ).fetchone()
        return _record_from_row(row) if row is not None else None

    def snapshot(
        self,
        limit: int = 10,
        *,
        rolling_trace_limit: int = DEFAULT_MCP_ROLLING_TRACE_LIMIT,
    ) -> McpInspectionHistorySnapshot:
        self.initialize()
        bounded_limit = max(1, int(limit))
        retention = self.retention_summary(rolling_trace_limit=rolling_trace_limit)
        with self.connection() as conn:
            count = int(conn.execute("SELECT COUNT(*) FROM mcp_inspection_history").fetchone()[0])
            rows = conn.execute(
                """
                SELECT *
                FROM mcp_inspection_history
                ORDER BY captured_at DESC, call_id DESC
                LIMIT ?
                """,
                (bounded_limit,),
            ).fetchall()
        return McpInspectionHistorySnapshot(
            history_path=str(self.db_path),
            version=MCP_INSPECTION_HISTORY_VERSION,
            record_count=count,
            retention=retention,
            records=tuple(_record_from_row(row) for row in rows),
        )


def default_mcp_inspection_history_path(project_root: Path | str) -> Path:
    """Return the project-owned default history database path."""
    return Path(project_root) / "data" / "mcp_inspection" / "history.sqlite3"


def _record_from_call(call: dict[str, Any]) -> McpInspectionHistoryRecord:
    capture = call.get("capture", {})
    tool = call.get("tool", {})
    usefulness = capture.get("usefulness_report", {})
    return McpInspectionHistoryRecord(
        call_id=str(call["call_id"]),
        tool_name=str(tool.get("tool_name", "")),
        capability_name=str(tool.get("capability_name", capture.get("capability", {}).get("name", ""))),
        captured_at=str(capture.get("captured_at", "")),
        status=str(call.get("status", "")),
        aggregate_score=float(usefulness.get("aggregate_score", 0.0)),
        pinned=bool(call.get("pinned", False)),
        operator_metadata=dict(call.get("operator_metadata", {}) or {}),
        call=dict(call),
    )


def _record_from_row(row: sqlite3.Row) -> McpInspectionHistoryRecord:
    return McpInspectionHistoryRecord(
        call_id=row["call_id"],
        tool_name=row["tool_name"],
        capability_name=row["capability_name"],
        captured_at=row["captured_at"],
        status=row["status"],
        aggregate_score=float(row["aggregate_score"]),
        pinned=bool(row["pinned"]),
        operator_metadata=json.loads(row["operator_metadata_json"] or "{}"),
        call=json.loads(row["call_json"]),
    )


def default_pinned_call_ids_for_score_artifacts(project_root: Path | str) -> tuple[str, ...]:
    """Return call ids referenced by current accepted score artifacts, when any."""
    root = Path(project_root).resolve()
    candidates = (
        root / "data" / "mcp_inspection" / "builder_task_scores.json",
        root / "data" / "mcp_inspection" / "context_projection_scores.json",
    )
    pinned: list[str] = []
    for path in candidates:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for score in payload.get("scores", ()):
            call_id = str(score.get("call_id", "")).strip()
            if call_id:
                pinned.append(call_id)
    return tuple(dict.fromkeys(pinned))


def sync_history_pins_from_score_artifacts(
    project_root: Path | str,
    history_path: Path | str,
) -> tuple[str, ...]:
    """Pin history records referenced by current score artifacts when present."""
    call_ids = default_pinned_call_ids_for_score_artifacts(project_root)
    if not call_ids:
        return ()
    store = McpInspectionHistoryStore(history_path)
    pinned: list[str] = []
    for call_id in call_ids:
        if store.pin_call(call_id):
            pinned.append(call_id)
    return tuple(pinned)


def prune_default_history_trace(
    project_root: Path | str,
    history_path: Path | str,
    *,
    rolling_trace_limit: int = DEFAULT_MCP_ROLLING_TRACE_LIMIT,
) -> dict[str, Any]:
    """Apply the default rolling-trace policy and return a readable summary."""
    pinned_ids = sync_history_pins_from_score_artifacts(project_root, history_path)
    store = McpInspectionHistoryStore(history_path)
    pruned_count = store.prune_rolling_trace(rolling_trace_limit=rolling_trace_limit)
    retention = store.retention_summary(rolling_trace_limit=rolling_trace_limit)
    return {
        "history_path": str(Path(history_path)),
        "rolling_trace_limit": retention.rolling_trace_limit,
        "pinned_call_ids": list(pinned_ids),
        "pruned_count": pruned_count,
        "retention": retention.to_dict(),
        "pruned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def promote_history_call(
    project_root: Path | str,
    history_path: Path | str,
    *,
    call_id: str = "",
    pinned: bool = True,
    label: str = "",
    reason: str = "",
    note: str = "",
) -> dict[str, Any]:
    """Promote or demote one history call with score-artifact guardrails."""
    store = McpInspectionHistoryStore(history_path)
    target = store.get_call(call_id) if call_id else store.latest()
    if target is None:
        raise ValueError("No matching history call was found for promotion control.")
    score_locked_ids = set(default_pinned_call_ids_for_score_artifacts(project_root))
    score_locked = target.call_id in score_locked_ids
    if not pinned and score_locked:
        raise ValueError("Score-referenced calls cannot be demoted through operator controls.")
    metadata_update = _promotion_metadata_update(target.operator_metadata, label=label, reason=reason, note=note)
    changed = store.update_call_record(
        target.call_id,
        pinned=pinned,
        operator_metadata=metadata_update,
    )
    updated = store.get_call(target.call_id)
    retention_policy = prune_default_history_trace(project_root, history_path)
    return {
        "call_id": target.call_id,
        "requested_pinned": bool(pinned),
        "changed": bool(changed),
        "score_locked": score_locked,
        "operator_metadata_changed": bool(metadata_update),
        "record": updated.to_dict() if updated is not None else None,
        "retention_policy": retention_policy,
    }


def _promotion_metadata_update(
    current: dict[str, Any],
    *,
    label: str,
    reason: str,
    note: str,
) -> dict[str, Any]:
    update: dict[str, Any] = {}
    normalized_label = (label or "").strip()
    normalized_reason = (reason or "").strip()
    normalized_note = (note or "").strip()
    if normalized_label:
        update["label"] = normalized_label
    if normalized_reason:
        update["reason"] = normalized_reason
    if normalized_note:
        update["note"] = normalized_note
    if update:
        update["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not current.get("created_at"):
            update["created_at"] = update["updated_at"]
    return update
