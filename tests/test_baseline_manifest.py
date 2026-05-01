"""Protected baseline manifest helper tests."""

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
    BASELINE_MANIFEST_VERSION,
    build_english_lexicon_baseline,
    build_python_docs_corpus,
    default_baseline_cartridge_specs,
    default_baseline_manifest_path,
    ingest_project_documents,
    run_baseline_manifest_helper,
    save_baseline_manifest_run,
)


class BaselineManifestTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> None:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[\n'
            '  {\n'
            '    "object" : "A thing presented to the senses or mind.",\n'
            '    "semantic" : "Relating to meaning."\n'
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
            "Built-in Functions\n******************\n\nlen(s)\n",
            encoding="utf-8",
        )
        (docs / "reference" / "compound_stmts.txt").write_text(
            "Compound statements\n*******************\n\nClass definitions\n=================\n\nclass Foo: pass\n",
            encoding="utf-8",
        )
        (docs / "reference" / "simple_stmts.txt").write_text(
            "Simple statements\n*****************\n\nreturn_stmt ::= \"return\" [expression_list]\n",
            encoding="utf-8",
        )
        (docs / "tutorial" / "controlflow.txt").write_text(
            "More Control Flow Tools\n***********************\n\n>>> def function(a):\n...     return a\n",
            encoding="utf-8",
        )

    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# nGraphMANIFOLD\n\nSemantic substrate.\n", encoding="utf-8")
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n## Current Park Point\n\nParked.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text("# MCP Seam\n\nThin inspection seam.\n", encoding="utf-8")
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nControlled replacement.\n",
            encoding="utf-8",
        )

    def _prepare_project(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)

    def test_default_baseline_specs_record_protected_cartridges(self) -> None:
        specs = default_baseline_cartridge_specs()

        self.assertEqual(
            [spec.name for spec in specs],
            ["base_english_lexicon.sqlite3", "python_docs.sqlite3", "project_documents.sqlite3"],
        )
        self.assertTrue(all(spec.build_command for spec in specs))

    def test_baseline_manifest_records_counts_hashes_sources_and_lock_policy(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._prepare_project(root)
            run = run_baseline_manifest_helper(root)
            output_path = save_baseline_manifest_run(run)
            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(run.version, BASELINE_MANIFEST_VERSION)
        self.assertTrue(run.all_ready)
        self.assertEqual(run.cartridge_count, 3)
        self.assertEqual(payload["version"], BASELINE_MANIFEST_VERSION)
        self.assertTrue(output_path.name.endswith("baseline_manifest.json"))
        for cartridge in run.cartridges:
            self.assertEqual(cartridge.status, "ready")
            self.assertGreater(cartridge.object_count, 0)
            self.assertGreater(cartridge.provenance_count, 0)
            self.assertEqual(len(cartridge.file_hash), 64)
            self.assertEqual(cartridge.file_hash_algorithm, "sha256")
            self.assertTrue(cartridge.source_refs)
            self.assertIn("protected:no_in_place_deformation", cartridge.lock_policy)

    def test_baseline_manifest_command_emits_json_and_writes_ignored_artifact(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._prepare_project(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["baseline-manifest", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

            artifact_exists = default_baseline_manifest_path(root).exists()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["version"], BASELINE_MANIFEST_VERSION)
        self.assertEqual(payload["cartridge_count"], 3)
        self.assertTrue(payload["all_ready"])
        self.assertTrue(artifact_exists)


if __name__ == "__main__":
    unittest.main()
