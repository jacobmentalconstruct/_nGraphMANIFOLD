"""Real builder-task scoring tests."""

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
    DEFAULT_BUILDER_TASK_DOCUMENT_PROFILE,
    default_builder_task_score_path,
    default_mcp_inspection_history_path,
    default_real_builder_tasks,
    run_real_builder_task_scoring,
)


class RealBuilderTaskScoringTests(unittest.TestCase):
    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(
            "# Test Project\n\nShow persisted calls with `python -m src.app mcp-history --dump-json`.",
            encoding="utf-8",
        )
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n## Current Park Point\n\nTranche: Test\n\nNext: Continue.",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\n## Tool Registration Candidate\n\nRegistered traversal surface.",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\n## Immediate Post-Prototype Work\n\nScore real builder tasks.",
            encoding="utf-8",
        )
        (root / "_docs" / "TODO.md").write_text(
            "# TODO\n\nDecide whether interaction envelopes remain inspection-only.",
            encoding="utf-8",
        )
        (root / "_docs" / "EXPERIENTIAL_WORKFLOW.md").write_text(
            "# Experiential Workflow\n\nScoring and visibility keep experiments disciplined.",
            encoding="utf-8",
        )
        (root / "_docs" / "PROTOTYPE_TUNING.md").write_text(
            "# Prototype Tuning\n\nBuilder score and projection score remain accepted.",
            encoding="utf-8",
        )

    def test_default_real_builder_tasks_cover_continuation_questions(self) -> None:
        tasks = default_real_builder_tasks()

        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0].task_id, "current_tranche_lookup")
        self.assertEqual(tasks[-1].expected_source_suffix, "README.md")
        self.assertEqual(DEFAULT_BUILDER_TASK_DOCUMENT_PROFILE, "expanded")

    def test_real_builder_task_scoring_meets_acceptance_on_project_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            run = run_real_builder_task_scoring(
                root,
                history_path=default_mcp_inspection_history_path(root),
                score_path=default_builder_task_score_path(root),
            )

        self.assertTrue(run.meets_acceptance)
        self.assertEqual(len(run.scores), 4)
        self.assertGreaterEqual(run.usefulness_report.aggregate_score, 0.7)
        self.assertTrue(Path(run.history_path).name, "history.sqlite3")
        self.assertEqual(run.document_profile, "expanded")
        self.assertIn("_docs/TODO.md", run.document_paths)

    def test_real_builder_task_scoring_writes_score_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            score_path = default_builder_task_score_path(root)

            run_real_builder_task_scoring(
                root,
                history_path=default_mcp_inspection_history_path(root),
                score_path=score_path,
            )

            payload = json.loads(score_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "v1")
        self.assertTrue(payload["meets_acceptance"])

    def test_mcp_score_tasks_command_emits_scoring_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-score-tasks", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["meets_acceptance"])
        self.assertEqual(len(payload["scores"]), 4)
        self.assertEqual(payload["document_profile"], "core")


if __name__ == "__main__":
    unittest.main()
