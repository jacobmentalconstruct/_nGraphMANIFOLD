"""Persistent history for local MCP inspection captures."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from src.core.representation.canonical import canonical_json

MCP_INSPECTION_HISTORY_VERSION = "v1"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS mcp_inspection_history (
    call_id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    capability_name TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    status TEXT NOT NULL,
    aggregate_score REAL NOT NULL,
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
    call: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "capability_name": self.capability_name,
            "captured_at": self.captured_at,
            "status": self.status,
            "aggregate_score": self.aggregate_score,
            "call": self.call,
        }


@dataclass(frozen=True)
class McpInspectionHistorySnapshot:
    """Inspectable summary plus recent records."""

    history_path: str
    version: str
    record_count: int
    records: tuple[McpInspectionHistoryRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "history_path": self.history_path,
            "version": self.version,
            "record_count": self.record_count,
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
                    aggregate_score, call_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.call_id,
                    record.tool_name,
                    record.capability_name,
                    record.captured_at,
                    record.status,
                    record.aggregate_score,
                    canonical_json(record.call),
                ),
            )
        return record

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

    def snapshot(self, limit: int = 10) -> McpInspectionHistorySnapshot:
        self.initialize()
        bounded_limit = max(1, int(limit))
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
        call=json.loads(row["call_json"]),
    )
