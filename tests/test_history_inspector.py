"""History-aware MCP inspector tests."""

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
    McpInspectionHistoryStore,
    build_default_registered_tool_call,
    build_history_aware_inspector_payload,
    default_builder_task_score_path,
)


class HistoryAwareInspectorTests(unittest.TestCase):
    def test_history_aware_payload_summarizes_recent_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            result = build_default_registered_tool_call(root / "tool.sqlite3")
            McpInspectionHistoryStore(history_path).record_call(result.to_dict())

            payload = build_history_aware_inspector_payload(
                root,
                history_path=history_path,
                limit=5,
            )

        self.assertEqual(payload.record_count, 1)
        self.assertEqual(len(payload.calls), 1)
        self.assertGreater(payload.calls[0].step_count, 0)
        self.assertIn("Recent calls", payload.to_summary_text())
        self.assertIn("raw", payload.to_dict())

    def test_history_aware_payload_maps_score_artifact_task_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            result = build_default_registered_tool_call(root / "tool.sqlite3")
            call = result.to_dict()
            McpInspectionHistoryStore(history_path).record_call(call)
            score_path = default_builder_task_score_path(root)
            score_path.parent.mkdir(parents=True, exist_ok=True)
            score_path.write_text(
                json.dumps(
                    {
                        "meets_acceptance": True,
                        "usefulness_report": {"aggregate_score": 0.93},
                        "scores": [
                            {
                                "call_id": call["call_id"],
                                "fixture": {"task_id": "current_tranche_lookup"},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = build_history_aware_inspector_payload(
                root,
                history_path=history_path,
            )

        self.assertEqual(payload.calls[0].task_id, "current_tranche_lookup")
        self.assertIn("latest builder score: 0.93", payload.to_summary_text())

    def test_mcp_history_view_dump_json_emits_summary_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["mcp-inspect", "--dump-json"])
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-history-view", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertIn("summary_text", payload)
        self.assertIn("calls", payload)
        self.assertIn("raw", payload)


if __name__ == "__main__":
    unittest.main()
