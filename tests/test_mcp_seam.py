"""Phase 8 thin MCP usefulness seam tests."""

from __future__ import annotations

import unittest

from src.core.coordination import (
    MCP_USEFULNESS_ACCEPTANCE_THRESHOLD,
    McpUsefulnessSignal,
    build_mcp_seam_manifest,
    evaluate_mcp_usefulness,
)


class McpUsefulnessSeamTests(unittest.TestCase):
    def test_manifest_exposes_prototype_spine_capabilities(self) -> None:
        manifest = build_mcp_seam_manifest()
        names = {capability.name for capability in manifest.capabilities}

        self.assertEqual(manifest.status, "thin_contract_only")
        self.assertIn("transformation.semantic_objects_from_source", names)
        self.assertIn("analysis.enrich_relations", names)
        self.assertIn("analysis.traverse_cartridge", names)
        self.assertIn("coordination.project_context_query", names)
        self.assertIn("execution.execute_plan", names)
        self.assertIn("persistence.semantic_cartridge", names)

    def test_manifest_declares_mcp_non_goals(self) -> None:
        manifest = build_mcp_seam_manifest()

        self.assertIn("no network server", manifest.non_goals)
        self.assertIn("no full MCP protocol implementation", manifest.non_goals)
        self.assertIn("no external runtime dependency", manifest.non_goals)
        self.assertIn("no autonomous agent loop", manifest.non_goals)

    def test_usefulness_signal_score_is_clamped_average(self) -> None:
        signal = McpUsefulnessSignal(
            capability_name="analysis.traverse_cartridge",
            task_fit=1.2,
            evidence_quality=0.8,
            actionability=0.7,
            friction_reduction=-1.0,
            repeatability=0.5,
        )

        self.assertEqual(signal.score, 0.6)
        self.assertEqual(signal.to_dict()["task_fit"], 1.0)
        self.assertEqual(signal.to_dict()["friction_reduction"], 0.0)

    def test_usefulness_report_tracks_acceptance_threshold(self) -> None:
        report = evaluate_mcp_usefulness(
            [
                McpUsefulnessSignal(
                    capability_name="analysis.traverse_cartridge",
                    task_fit=0.9,
                    evidence_quality=0.8,
                    actionability=0.8,
                    friction_reduction=0.7,
                    repeatability=0.8,
                ),
                McpUsefulnessSignal(
                    capability_name="execution.execute_plan",
                    task_fit=0.75,
                    evidence_quality=0.7,
                    actionability=0.75,
                    friction_reduction=0.7,
                    repeatability=0.75,
                ),
            ]
        )

        self.assertEqual(report.acceptance_threshold, MCP_USEFULNESS_ACCEPTANCE_THRESHOLD)
        self.assertTrue(report.meets_acceptance)
        self.assertGreaterEqual(report.aggregate_score, MCP_USEFULNESS_ACCEPTANCE_THRESHOLD)


if __name__ == "__main__":
    unittest.main()
