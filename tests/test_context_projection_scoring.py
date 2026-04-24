"""Context projection arbitration scoring tests."""

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
    PROJECT_QUERY_TOOL_NAME,
    McpInspectionHistoryStore,
    build_english_lexicon_baseline,
    build_python_docs_corpus,
    default_context_projection_arbitration_fixtures,
    default_context_projection_score_path,
    default_mcp_inspection_history_path,
    ingest_project_documents,
    run_context_projection_arbitration_scoring,
)


class ContextProjectionScoringTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> None:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[\n'
            '  {\n'
            '    "teakettle" : "A kettle in which water is boiled for making tea.",\n'
            '    "object" : "A thing presented to the senses or mind.",\n'
            '    "class" : "A group ranked together.",\n'
            '    "function" : "The act of performing a duty."\n'
            '  }\n'
            ']\n',
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
            "   >>> def function(a):\n   ...     return a\n",
            encoding="utf-8",
        )

    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# nGraphMANIFOLD\n\nSemantic substrate.\n", encoding="utf-8")
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n## Current Park Point\n\n"
            "Tranche: Layer Arbitration And Rebinding Scoring.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\nShared command spine and raw inspection payloads.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\n## Builder Constraint Contract\n\n"
            "The builder constraint contract controls tranche boundaries and project doctrine.\n",
            encoding="utf-8",
        )

    def _build_layers(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)

    def test_default_arbitration_fixtures_cover_three_context_layers(self) -> None:
        fixtures = default_context_projection_arbitration_fixtures()

        self.assertEqual(len(fixtures), 3)
        self.assertEqual(
            {fixture.expected_layer for fixture in fixtures},
            {"english_lexical_prior", "python_docs_projection", "project_local_docs"},
        )

    def test_arbitration_scoring_records_expected_layer_results(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            history_path = default_mcp_inspection_history_path(root)

            run = run_context_projection_arbitration_scoring(
                root,
                history_path=history_path,
                score_path=default_context_projection_score_path(root),
            )
            history = McpInspectionHistoryStore(history_path).snapshot(limit=5)

        self.assertTrue(run.meets_acceptance)
        self.assertEqual(run.usefulness_report.aggregate_score, 0.96)
        self.assertEqual(
            [score.selected_layer for score in run.scores],
            ["english_lexical_prior", "python_docs_projection", "project_local_docs"],
        )
        self.assertTrue(all(score.passed for score in run.scores))
        self.assertGreater(run.elapsed_ms, 0)
        self.assertTrue(all(record.tool_name == PROJECT_QUERY_TOOL_NAME for record in history.records[:3]))

    def test_project_query_score_command_emits_scoring_run(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["project-query-score", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["meets_acceptance"])
        self.assertEqual(payload["scores"][1]["selected_layer"], "python_docs_projection")
        self.assertGreater(payload["elapsed_ms"], 0)


if __name__ == "__main__":
    unittest.main()
