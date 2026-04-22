"""Persistent MCP inspection history tests."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.app import main
from src.core.coordination import (
    TRAVERSAL_TOOL_NAME,
    McpInspectionHistoryStore,
    build_default_registered_tool_call,
    default_mcp_inspection_history_path,
)


class McpInspectionHistoryTests(unittest.TestCase):
    def test_history_store_records_registered_tool_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = McpInspectionHistoryStore(Path(temp) / "history.sqlite3")
            result = build_default_registered_tool_call(Path(temp) / "tool.sqlite3")

            record = store.record_call(result.to_dict())
            latest = store.latest()

        self.assertEqual(record.tool_name, TRAVERSAL_TOOL_NAME)
        self.assertIsNotNone(latest)
        self.assertEqual(latest.call_id, record.call_id)
        self.assertEqual(latest.aggregate_score, 0.93)

    def test_history_snapshot_returns_recent_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = McpInspectionHistoryStore(Path(temp) / "history.sqlite3")
            first = build_default_registered_tool_call(Path(temp) / "first.sqlite3")
            second = build_default_registered_tool_call(Path(temp) / "second.sqlite3")

            store.record_call(first.to_dict())
            store.record_call(second.to_dict())
            snapshot = store.snapshot(limit=1)

        self.assertEqual(snapshot.record_count, 2)
        self.assertEqual(len(snapshot.records), 1)
        self.assertIn(snapshot.records[0].call_id, {first.call_id, second.call_id})

    def test_default_history_path_is_project_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = default_mcp_inspection_history_path(Path(temp))

        self.assertEqual(path.name, "history.sqlite3")
        self.assertIn("mcp_inspection", str(path))

    def test_mcp_inspect_dump_json_persists_history_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stdout = io.StringIO()
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-inspect", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertGreaterEqual(payload["record_count"], 1)
        self.assertEqual(payload["records"][0]["tool_name"], TRAVERSAL_TOOL_NAME)

    def test_mcp_history_dump_json_reads_persisted_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["mcp-inspect", "--dump-json"])
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-history", "--dump-json", "--history-limit", "1"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertGreaterEqual(payload["record_count"], 1)
        self.assertEqual(len(payload["records"]), 1)


if __name__ == "__main__":
    unittest.main()
