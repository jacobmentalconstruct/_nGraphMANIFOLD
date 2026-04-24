"""Traversal seed search tests."""

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
    run_seed_search_traversal,
    search_project_document_seeds,
)


class SeedSearchTests(unittest.TestCase):
    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(
            "# Test Project\n\nA compact overview for semantic traversal.",
            encoding="utf-8",
        )
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n## Current Park Point\n\n"
            "Completed: History-Aware MCP Inspector.\n\n"
            "Next: Traversal Search And Seed Selection.",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\nThe seam exposes traversal captures for MCP inspection.",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nUse bounded tranches and avoid broad rewrites.",
            encoding="utf-8",
        )

    def test_seed_search_ranks_project_status_for_current_park_query(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            result = search_project_document_seeds(root, "Current Park Point", limit=3)

        payload = result.to_dict()
        self.assertGreaterEqual(payload["candidate_count"], 1)
        self.assertIsNotNone(payload["selected_seed"])
        self.assertTrue(payload["selected_seed"]["source_ref"].endswith("PROJECT_STATUS.md"))
        self.assertIn("current", payload["selected_seed"]["matched_terms"])
        self.assertIsNotNone(payload["selected_flow"])
        self.assertTrue(
            any(obj["role"] == "selected" for obj in payload["selected_flow"]["objects"])
        )
        self.assertIn("score_breakdown", payload["selected_seed"])

    def test_seed_search_traversal_records_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            result = run_seed_search_traversal(
                root,
                "MCP inspection",
                history_path=root / "data" / "mcp_inspection" / "history.sqlite3",
            )

        payload = result.to_dict()
        self.assertEqual(payload["tool_call"]["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertIsNotNone(payload["history_record"])
        self.assertGreaterEqual(payload["search"]["candidate_count"], 1)

    def test_seed_search_command_emits_selected_seed_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "mcp-search-seeds",
                            "--query",
                            "Traversal Search",
                            "--seed-limit",
                            "2",
                            "--dump-json",
                        ]
                    )
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["tool_call"]["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertLessEqual(len(payload["search"]["candidates"]), 2)
        self.assertIsNotNone(payload["search"]["selected_seed"])
        self.assertIsNotNone(payload["search"]["selected_flow"])


if __name__ == "__main__":
    unittest.main()
