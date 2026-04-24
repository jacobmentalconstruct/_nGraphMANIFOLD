"""UI command spine pilot tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.config import AppSettings
from src.core.coordination import (
    PROJECT_QUERY_TOOL_NAME,
    McpInspectionHistoryStore,
    build_english_lexicon_baseline,
    build_history_aware_inspector_payload,
    build_python_docs_corpus,
    default_mcp_inspection_history_path,
    ingest_project_documents,
)
from src.ui.gui_main import run_ui_project_query


class UiCommandSpineTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> None:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[{"object":"A thing presented to the senses or mind.",'
            '"class":"A group ranked together.",'
            '"function":"The act of performing a duty."}]',
            encoding="utf-8",
        )

    def _write_python_docs(self, root: Path) -> None:
        docs = root / "assets" / "_corpus_examples" / "python-3.11.15-docs-text"
        (docs / "library").mkdir(parents=True, exist_ok=True)
        (docs / "reference").mkdir(parents=True, exist_ok=True)
        (docs / "tutorial").mkdir(parents=True, exist_ok=True)
        (docs / "library" / "functions.txt").write_text(
            "Built-in Functions\n******************\n\nissubclass(class, classinfo)\n",
            encoding="utf-8",
        )
        (docs / "reference" / "compound_stmts.txt").write_text(
            "Compound statements\n*******************\n\nClass definitions\n=================\n\n"
            "   class Foo(object):\n       pass\n",
            encoding="utf-8",
        )
        (docs / "reference" / "simple_stmts.txt").write_text(
            "Simple statements\n*****************\n\nreturn_stmt ::= \"return\" [expression_list]\n",
            encoding="utf-8",
        )
        (docs / "tutorial" / "controlflow.txt").write_text(
            "More Control Flow Tools\n***********************\n\n"
            "   >>> for i in range(3):\n   ...     print(i)\n",
            encoding="utf-8",
        )

    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# nGraphMANIFOLD\n\nSemantic substrate.\n", encoding="utf-8")
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\nUI Command Spine Pilot.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\nShared command spine and raw inspection payloads.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nSemanticObject preserves provenance and typed relations.\n",
            encoding="utf-8",
        )

    def _build_layers(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)

    def test_ui_project_query_records_shared_interaction_capture(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            settings = AppSettings(
                project_root=root,
                docs_root=root / "_docs",
                data_root=root / "data",
            )

            call = run_ui_project_query(settings, "class object function", limit=3)
            latest = McpInspectionHistoryStore(default_mcp_inspection_history_path(root)).latest()
            inspector = build_history_aware_inspector_payload(
                root,
                history_path=default_mcp_inspection_history_path(root),
            )

        self.assertEqual(call["tool"]["tool_name"], PROJECT_QUERY_TOOL_NAME)
        self.assertEqual(call["capture"]["command"]["source_surface"], "ui")
        self.assertEqual(call["capture"]["command"]["actor"], "human")
        self.assertEqual(call["capture"]["response"]["projection_frame"]["selected_layer"], "python_docs_projection")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.tool_name, PROJECT_QUERY_TOOL_NAME)
        self.assertEqual(inspector.calls[0].selected_layer, "python_docs_projection")


if __name__ == "__main__":
    unittest.main()
