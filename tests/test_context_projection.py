"""Context projection tests."""

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
    build_english_lexicon_baseline,
    build_python_docs_corpus,
    ingest_project_documents,
    project_context_query,
    tokenize_query,
)


class ContextProjectionTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> None:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[\n'
            '  {\n'
            '    "object" : "1. A thing presented to the senses or the mind. 2. An end or aim.",\n'
            '    "function" : "The act of performing a duty; in mathematics, a relation between quantities.",\n'
            '    "provenance" : "Origin; source; provenience.",\n'
            '    "class" : "A group ranked together as possessing common characteristics."\n'
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
            "Built-in Functions\n"
            "******************\n"
            "\n"
            "all(iterable)\n"
            "\n"
            "   Equivalent to:\n"
            "\n"
            "      def all(iterable):\n"
            "          for element in iterable:\n"
            "              if not element:\n"
            "                  return False\n"
            "          return True\n"
            "\n"
            "issubclass(class, classinfo)\n",
            encoding="utf-8",
        )
        (docs / "reference" / "compound_stmts.txt").write_text(
            "Compound statements\n"
            "*******************\n"
            "\n"
            "Class definitions\n"
            "=================\n"
            "\n"
            "   class Foo(object):\n"
            "       pass\n",
            encoding="utf-8",
        )
        (docs / "reference" / "simple_stmts.txt").write_text(
            "Simple statements\n"
            "*****************\n"
            "\n"
            "   return_stmt ::= \"return\" [expression_list]\n",
            encoding="utf-8",
        )
        (docs / "tutorial" / "controlflow.txt").write_text(
            "More Control Flow Tools\n"
            "***********************\n"
            "\n"
            "   >>> for i in range(3):\n"
            "   ...     print(i)\n",
            encoding="utf-8",
        )

    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# nGraphMANIFOLD\n\nSemantic substrate prototype.\n", encoding="utf-8")
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n## Current Park Point\n\nContext Projection / Rebinding Layer.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\nTraversal evidence and raw inspection payloads.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\n## Phase 2: Canonical Semantic Object\n\n"
            "SemanticObject preserves provenance and typed relations.\n",
            encoding="utf-8",
        )

    def _build_layers(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)

    def test_tokenize_query_preserves_code_terms(self) -> None:
        terms = tokenize_query("for element in iterable return False")

        self.assertIn("for", terms)
        self.assertIn("in", terms)
        self.assertIn("return", terms)
        self.assertNotIn("the", terms)

    def test_project_context_query_separates_object_layers(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)

            result = project_context_query(root, "object", limit=3)

        payload = result.to_dict()
        projections = {item["layer"]["name"]: item for item in payload["frame"]["projections"]}
        self.assertIn("english_lexical_prior", projections)
        self.assertIn("python_docs_projection", projections)
        self.assertIn("project_local_docs", projections)
        self.assertGreater(projections["english_lexical_prior"]["candidate_count"], 0)
        self.assertGreater(projections["python_docs_projection"]["candidate_count"], 0)
        self.assertGreater(projections["project_local_docs"]["candidate_count"], 0)

    def test_code_shaped_query_selects_python_layer(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)

            result = project_context_query(root, "for element in iterable return False", limit=3)

        payload = result.to_dict()
        self.assertEqual(payload["frame"]["selected_layer"], "python_docs_projection")
        selected = payload["frame"]["selected_candidate"]
        self.assertIn(selected["kind"], {"python_code_example", "python_doctest_example"})
        self.assertIsNotNone(payload["frame"]["selected_flow"])
        self.assertEqual(payload["frame"]["selected_flow"]["objects"][0]["role"], "selected")
        self.assertGreaterEqual(len(payload["frame"]["selected_flow"]["objects"]), 1)

    def test_project_doctrine_query_selects_project_layer(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)

            result = project_context_query(root, "semantic object provenance relations", limit=3)

        payload = result.to_dict()
        self.assertEqual(payload["frame"]["selected_layer"], "project_local_docs")
        self.assertIn("not final semantic grounding", payload["frame"]["caution"])

    def test_project_query_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["project-query", "--query", "object", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        frame = payload["capture"]["response"]["projection_frame"]
        self.assertEqual(payload["capture"]["command"]["payload"]["query"], "object")
        self.assertEqual(frame["raw_query"], "object")
        self.assertIn("english_lexical_prior", frame["context_stack"])


if __name__ == "__main__":
    unittest.main()
