"""Tests for the DEV-LOG mirror renderer."""

from __future__ import annotations

import json
import unittest

from src.core.logging.dev_log_export import JournalEntry, render_dev_log


class DevLogExportTests(unittest.TestCase):
    def test_render_dev_log_renders_structured_phase_metadata(self) -> None:
        entry = JournalEntry(
            id=41,
            created_at="2026-04-24T18:00:00Z",
            kind="phase_park",
            status="parked_complete",
            title="Park: Journal Lessons Learned Structure",
            body="Added a bounded lessons-learned convention for future tranche parks.",
            tags_json='["phase_park","journal","continuity"]',
            related_path="_docs/PROJECT_STATUS.md",
            related_ref="journal_signal",
            metadata_json=json.dumps(
                {
                    "files_changed": ["README.md", "_docs/EXPERIENTIAL_WORKFLOW.md"],
                    "key_decisions": [
                        "Keep lessons learned phase-level rather than turning the journal into a transcript."
                    ],
                    "lessons_learned": [
                        "The existing journal already carried good signal, but it was inconsistent to read externally."
                    ],
                    "evidence_used": [
                        "Contract requires what changed, why it changed, and notable design decisions after meaningful phases."
                    ],
                    "rejected_alternatives": [
                        "Do not rewrite prior journal rows just to make them uniform."
                    ],
                    "verification": {
                        "full_tests": "python -m unittest discover -s tests",
                        "full_test_count": 127,
                    },
                    "next_focus": ["Loop safeguards and controlled expansion review"],
                    "phase": "post_prototype_hardening",
                    "slice": "journal_signal_improvement",
                }
            ),
        )

        rendered = render_dev_log(
            [entry],
            exported_at="2026-04-24T18:10:00+00:00",
            source_of_truth="_docs/_journalDB/app_journal.sqlite3",
        )

        self.assertIn("### Key Decisions", rendered)
        self.assertIn("### Lessons Learned", rendered)
        self.assertIn("### Evidence Used", rendered)
        self.assertIn("### Rejected Alternatives", rendered)
        self.assertIn("### Verification", rendered)
        self.assertIn("### Next Focus", rendered)
        self.assertIn("### Raw Metadata", rendered)
        self.assertIn('"phase": "post_prototype_hardening"', rendered)


if __name__ == "__main__":
    unittest.main()
