"""Project document ingestion candidate tests."""

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
    DEFAULT_PROJECT_DOCUMENTS,
    EXPANDED_PROJECT_DOCUMENTS,
    TRAVERSAL_TOOL_NAME,
    default_project_document_cartridge_path,
    ingest_project_documents_for_traversal,
    resolve_project_document_profile,
)


class ProjectDocumentIngestionTests(unittest.TestCase):
    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(
            "# Test Project\n\nCurrent builder-visible overview.",
            encoding="utf-8",
        )
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n## Current Park Point\n\nTranche: Test\n\nNext: Continue.",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\nRegistered tool candidate: ngraph.analysis.traverse_cartridge.",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nUse bounded tranches and preserve non-goals.",
            encoding="utf-8",
        )

    def test_default_document_set_is_bounded(self) -> None:
        self.assertEqual(
            DEFAULT_PROJECT_DOCUMENTS,
            (
                "README.md",
                "_docs/PROJECT_STATUS.md",
                "_docs/MCP_SEAM.md",
                "_docs/STRANGLER_PLAN.md",
            ),
        )

    def test_expanded_document_profile_adds_controlled_operator_docs(self) -> None:
        profile, paths = resolve_project_document_profile("expanded")

        self.assertEqual(profile, "expanded")
        self.assertEqual(paths, EXPANDED_PROJECT_DOCUMENTS)
        self.assertIn("_docs/TODO.md", paths)
        self.assertIn("_docs/EXPERIENTIAL_WORKFLOW.md", paths)
        self.assertIn("_docs/PROTOTYPE_TUNING.md", paths)

    def test_project_documents_ingest_and_call_registered_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            result = ingest_project_documents_for_traversal(root)

        payload = result.to_dict()
        self.assertGreater(payload["object_count"], 0)
        self.assertGreater(payload["relation_count"], 0)
        self.assertEqual(payload["tool_call"]["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertTrue(payload["tool_call"]["capture"]["usefulness_report"]["meets_acceptance"])
        self.assertTrue(payload["seed_source_ref"].endswith("PROJECT_STATUS.md"))

    def test_default_cartridge_path_is_project_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = default_project_document_cartridge_path(Path(temp))

        self.assertEqual(path.name, "project_documents.sqlite3")
        self.assertIn("cartridges", str(path))

    def test_project_ingest_command_emits_result_and_records_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_project_docs(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-ingest-docs", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["tool_call"]["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertEqual(len(payload["document_paths"]), 4)


if __name__ == "__main__":
    unittest.main()
