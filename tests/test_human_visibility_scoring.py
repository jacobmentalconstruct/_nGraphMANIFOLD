"""Human-facing inspection usefulness scoring tests."""

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
    HUMAN_VISIBILITY_SCORING_VERSION,
    build_english_lexicon_baseline,
    build_python_docs_corpus,
    default_builder_task_score_path,
    default_context_projection_score_path,
    default_human_visibility_fixtures,
    default_human_visibility_score_path,
    default_mcp_inspection_history_path,
    ingest_project_documents,
    run_context_projection_arbitration_scoring,
    run_human_visibility_scoring,
    run_real_builder_task_scoring,
)
from src.core.coordination.project_documents import default_project_document_cartridge_path
from src.core.persistence import SemanticCartridge


class HumanVisibilityScoringTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> None:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[\n'
            '  {\n'
            '    "teakettle" : "A kettle in which water is boiled for making tea.",\n'
            '    "object" : "A thing presented to the senses or mind.",\n'
            '    "class" : "A group ranked together.",\n'
            '    "function" : "The act of performing a duty.",\n'
            '    "semantic" : "Relating to meaning.",\n'
            '    "provenance" : "Origin or source history.",\n'
            '    "relations" : "Connections among things."\n'
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
        (root / "README.md").write_text(
            "# nGraphMANIFOLD\n\n"
            "Semantic substrate.\n\n"
            "Use `mcp-history` to show persisted MCP inspection history.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n"
            "## Current Park Point\n\n"
            "Current Park Point records the next tranche and implementation target.\n\n"
            "Semantic object provenance relations are project-local doctrine.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\n"
            "Tool Registration Candidate exposes shared command spine and raw inspection payloads.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\n"
            "## Immediate Post-Prototype Work\n\n"
            "Immediate Post-Prototype Work opens controlled inspection usefulness scoring.\n",
            encoding="utf-8",
        )

    def _prepare_project(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)
        history_path = default_mcp_inspection_history_path(root)
        run_real_builder_task_scoring(
            root,
            history_path=history_path,
            score_path=default_builder_task_score_path(root),
            document_profile="core",
        )
        run_context_projection_arbitration_scoring(
            root,
            history_path=history_path,
            score_path=default_context_projection_score_path(root),
        )

    def test_default_fixtures_are_precommitted_visibility_surfaces(self) -> None:
        fixtures = default_human_visibility_fixtures()

        self.assertEqual(
            [fixture.task_id for fixture in fixtures],
            [
                "projection_visibility",
                "seed_visibility",
                "promotion_visibility",
                "status_score_visibility",
            ],
        )
        self.assertTrue(all(fixture.expected_surfaces for fixture in fixtures))

    def test_visibility_scoring_accepts_shared_evidence_without_new_cartridge_truth(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._prepare_project(root)
            cartridge = SemanticCartridge(default_project_document_cartridge_path(root))
            before = cartridge.manifest()
            score_path = default_human_visibility_score_path(root)

            run = run_human_visibility_scoring(
                root,
                history_path=default_mcp_inspection_history_path(root),
                score_path=score_path,
                project_doc_profile="core",
            )
            after = cartridge.manifest()
            score_file_exists = score_path.exists()
            manifest_file_exists = (root / "data" / "cartridges" / "baseline_manifest.json").exists()

        self.assertEqual(run.version, HUMAN_VISIBILITY_SCORING_VERSION)
        self.assertTrue(run.meets_acceptance)
        self.assertTrue(all(score.passed for score in run.scores))
        self.assertTrue(score_file_exists)
        self.assertGreater(run.elapsed_ms, 0)
        self.assertEqual(before.object_count, after.object_count)
        self.assertEqual(before.relation_count, after.relation_count)
        self.assertFalse(manifest_file_exists)

    def test_score_visibility_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._prepare_project(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-score-visibility", "--dump-json", "--project-doc-profile", "core"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["version"], HUMAN_VISIBILITY_SCORING_VERSION)
        self.assertTrue(payload["meets_acceptance"])
        self.assertEqual(len(payload["scores"]), 4)
        self.assertIn("usefulness_report", payload)
        self.assertGreater(payload["elapsed_ms"], 0)


if __name__ == "__main__":
    unittest.main()
