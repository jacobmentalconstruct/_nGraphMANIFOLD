"""Loop-safeguard review tests."""

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
    LOOP_REVIEW_STATUS_READY,
    build_loop_safeguards_review,
    default_builder_task_score_path,
    default_context_projection_score_path,
)


class LoopSafeguardsTests(unittest.TestCase):
    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(
            "# Test Project\n\nUse scoring and inspection before expansion.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n"
            "## Proposed Next Tranche\n\n"
            "Loop Safeguards And Controlled Expansion Review.\n\n"
            "Keep the bridge file-backed for the next band, keep core and expanded "
            "project-doc profiles, and review the collaboration loop before widening scope.\n\n"
            "## Latest Verification\n\n"
            "Builder score and projection score remain accepted while the next tranche "
            "anchor resolves through project-local docs.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\n"
            "## Surface Ownership In The Hardening Phase\n\n"
            "The host workspace is the main live operator surface. The stream is the "
            "sliding recent interaction window. The cockpit is the compact shared registry. "
            "The history view is the deeper provenance access surface.\n\n"
            "Interaction truth boundary remains inspection only and not semantic cartridge truth.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nControlled expansion follows loop safeguards.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "TODO.md").write_text(
            "# TODO\n\n"
            "Immediate next step: reassess the larger collaboration loop and its failure modes.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "EXPERIENTIAL_WORKFLOW.md").write_text(
            "# Experiential Workflow\n\n"
            "Scoring and visibility keep experiments disciplined.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "PROTOTYPE_TUNING.md").write_text(
            "# Prototype Tuning\n\n"
            "Builder and projection scores remain accepted before controlled expansion.\n",
            encoding="utf-8",
        )

    def _write_score_artifacts(self, root: Path) -> None:
        builder_path = default_builder_task_score_path(root)
        projection_path = default_context_projection_score_path(root)
        builder_path.parent.mkdir(parents=True, exist_ok=True)
        builder_path.write_text(
            json.dumps(
                {
                    "meets_acceptance": True,
                    "document_profile": "core",
                    "elapsed_ms": 12,
                    "corpus_object_count": 10,
                    "corpus_relation_count": 9,
                    "usefulness_report": {"aggregate_score": 0.93},
                }
            ),
            encoding="utf-8",
        )
        projection_path.write_text(
            json.dumps(
                {
                    "meets_acceptance": True,
                    "elapsed_ms": 8,
                    "usefulness_report": {"aggregate_score": 0.96},
                }
            ),
            encoding="utf-8",
        )

    def test_loop_review_passes_when_core_loop_boundaries_are_visible(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._write_project_docs(root)
            self._write_score_artifacts(root)

            review = build_loop_safeguards_review(root)

        self.assertEqual(review.status, LOOP_REVIEW_STATUS_READY)
        self.assertTrue(review.meets_review_gate)
        self.assertEqual(review.next_tranche, "Loop Safeguards And Controlled Expansion Review")
        self.assertEqual({check.status for check in review.checks}, {"pass"})
        self.assertEqual(review.document_profile, "core")
        self.assertEqual(review.runtime_state["bridge_timeout_policy"]["transport_kind"], "file_backed_local")
        self.assertFalse(review.runtime_state["interaction_truth_policy"]["persist_to_semantic_cartridges"])
        self.assertIn("next_tranche_anchor", {item.evidence_id for item in review.evidence})

    def test_loop_review_warns_when_score_artifacts_are_missing(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._write_project_docs(root)

            review = build_loop_safeguards_review(root)

        score_check = next(check for check in review.checks if check.check_id == "score_clarity")
        self.assertEqual(score_check.status, "warn")
        self.assertTrue(review.meets_review_gate)

    def test_loop_review_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._write_project_docs(root)
            self._write_score_artifacts(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["loop-review", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], LOOP_REVIEW_STATUS_READY)
        self.assertTrue(payload["meets_review_gate"])
        self.assertEqual(payload["document_profile"], "core")


if __name__ == "__main__":
    unittest.main()
