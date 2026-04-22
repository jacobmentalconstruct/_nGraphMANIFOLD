"""Shared command spine tests for UI/MCP projection alignment."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.core.coordination import (
    PROJECT_QUERY_TOOL_NAME,
    McpInspectionHistoryStore,
    build_english_lexicon_baseline,
    build_history_aware_inspector_payload,
    build_python_docs_corpus,
    call_registered_mcp_tool,
    command_envelope_to_semantic_object,
    create_command_envelope,
    ingest_project_documents,
    run_project_query_interaction,
    tool_result_envelope_to_semantic_object,
)


class InteractionSpineTests(unittest.TestCase):
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
            "# Project Status\n\nContext Projection / Rebinding Layer.\n",
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

    def test_command_envelope_id_is_deterministic_when_timestamp_is_fixed(self) -> None:
        first = create_command_envelope(
            tool_name=PROJECT_QUERY_TOOL_NAME,
            payload={"query": "object", "limit": 3},
            actor="human",
            source_surface="cli",
            created_at="2026-04-22T00:00:00Z",
        )
        second = create_command_envelope(
            tool_name=PROJECT_QUERY_TOOL_NAME,
            payload={"limit": 3, "query": "object"},
            actor="human",
            source_surface="cli",
            created_at="2026-04-22T00:00:00Z",
        )

        self.assertEqual(first.command_id, second.command_id)
        self.assertEqual(first.to_dict()["tool_name"], PROJECT_QUERY_TOOL_NAME)

    def test_project_query_interaction_capture_contains_command_and_result(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)

            capture = run_project_query_interaction(root, "class object function", limit=3)

        payload = capture.to_dict()
        self.assertEqual(payload["command"]["tool_name"], PROJECT_QUERY_TOOL_NAME)
        self.assertEqual(payload["result"]["status"], "ok")
        self.assertEqual(
            payload["response"]["projection_frame"]["selected_layer"],
            "python_docs_projection",
        )
        self.assertGreater(payload["usefulness_report"]["aggregate_score"], 0.7)

    def test_envelopes_project_to_semantic_objects_without_persistence(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            capture = run_project_query_interaction(root, "class object function", limit=3)

        command_object = command_envelope_to_semantic_object(capture.command)
        result_object = tool_result_envelope_to_semantic_object(capture.result)

        self.assertEqual(command_object.kind, "interaction_command")
        self.assertEqual(command_object.surfaces.structural["tool_name"], PROJECT_QUERY_TOOL_NAME)
        self.assertEqual(result_object.kind, "interaction_result")
        self.assertEqual(result_object.surfaces.semantic["selected_layer"], "python_docs_projection")
        self.assertEqual(result_object.relations[0].target_ref, capture.command.command_id)

    def test_project_query_call_records_in_history_and_inspector_summary(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            result = call_registered_mcp_tool(
                PROJECT_QUERY_TOOL_NAME,
                {"query": "class object function", "limit": 3},
                project_root=root,
            )
            store = McpInspectionHistoryStore(root / "history.sqlite3")
            store.record_call(result.to_dict())

            inspector = build_history_aware_inspector_payload(
                root,
                history_path=root / "history.sqlite3",
            )

        self.assertEqual(inspector.calls[0].tool_name, PROJECT_QUERY_TOOL_NAME)
        self.assertEqual(inspector.calls[0].selected_layer, "python_docs_projection")
        self.assertIn("selected_layer=python_docs_projection", inspector.to_summary_text())
        self.assertIn("command", json.dumps(inspector.raw))


if __name__ == "__main__":
    unittest.main()
