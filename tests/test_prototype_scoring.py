"""Prototype tuning and scoring harness tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.coordination import (
    MCP_USEFULNESS_ACCEPTANCE_THRESHOLD,
    default_builder_task_fixtures,
    run_prototype_tuning_fixture,
)


class PrototypeScoringTests(unittest.TestCase):
    def test_default_builder_task_fixtures_are_repeatable(self) -> None:
        fixtures = default_builder_task_fixtures()

        self.assertEqual(len(fixtures), 3)
        self.assertEqual(
            {fixture.fixture_id for fixture in fixtures},
            {
                "relation_evidence_trace",
                "execution_report_trace",
                "persistence_round_trip",
            },
        )

    def test_tuning_fixture_runs_full_spine_and_meets_acceptance(self) -> None:
        fixture = default_builder_task_fixtures()[0]
        with tempfile.TemporaryDirectory() as temp:
            run = run_prototype_tuning_fixture(
                fixture,
                Path(temp) / "scoring.sqlite3",
            )

        self.assertTrue(run.meets_acceptance)
        self.assertGreaterEqual(
            run.usefulness_report.aggregate_score,
            MCP_USEFULNESS_ACCEPTANCE_THRESHOLD,
        )
        self.assertGreater(run.object_count, 0)
        self.assertGreater(run.relation_count, 0)
        self.assertGreater(run.traversal_step_count, 0)
        self.assertTrue(run.execution_complete)
        self.assertIsNotNone(run.result_semantic_id)

    def test_tuning_report_scores_all_mcp_seam_capabilities(self) -> None:
        fixture = default_builder_task_fixtures()[1]
        with tempfile.TemporaryDirectory() as temp:
            run = run_prototype_tuning_fixture(
                fixture,
                Path(temp) / "scoring.sqlite3",
            )

        scored_names = {signal.capability_name for signal in run.usefulness_report.signals}
        manifest_names = {capability.name for capability in run.seam_manifest.capabilities}

        self.assertEqual(scored_names, manifest_names)
        self.assertEqual(len(run.usefulness_report.signals), 6)

    def test_recommended_next_capability_prefers_traversal_after_passing_scores(self) -> None:
        fixture = default_builder_task_fixtures()[2]
        with tempfile.TemporaryDirectory() as temp:
            run = run_prototype_tuning_fixture(
                fixture,
                Path(temp) / "scoring.sqlite3",
            )

        self.assertTrue(run.meets_acceptance)
        self.assertEqual(run.recommended_next_capability, "analysis.traverse_cartridge")


if __name__ == "__main__":
    unittest.main()
