"""Python documentation projection corpus tests."""

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
    build_python_docs_corpus,
    default_python_docs_cartridge_path,
    default_python_docs_source_path,
)
from src.core.persistence import SemanticCartridge
from src.core.transformation import extract_python_docs_file, summarize_python_ast


class PythonDocsCorpusTests(unittest.TestCase):
    def _write_python_docs(self, root: Path) -> Path:
        docs = root / "assets" / "_corpus_examples" / "python-3.11.15-docs-text"
        (docs / "library").mkdir(parents=True, exist_ok=True)
        (docs / "reference").mkdir(parents=True, exist_ok=True)
        (docs / "library" / "functions.txt").write_text(
            "Built-in Functions\n"
            "******************\n"
            "\n"
            "all(iterable)\n"
            "\n"
            "   Return True if all elements of the iterable are true.\n"
            "\n"
            "   Equivalent to:\n"
            "\n"
            "      def all(iterable):\n"
            "          for element in iterable:\n"
            "              if not element:\n"
            "                  return False\n"
            "          return True\n"
            "\n"
            "bin(x)\n"
            "\n"
            "   >>> bin(3)\n"
            "   '0b11'\n",
            encoding="utf-8",
        )
        (docs / "reference" / "compound_stmts.txt").write_text(
            "Compound statements\n"
            "*******************\n"
            "\n"
            "The if statement\n"
            "================\n"
            "\n"
            "   if_stmt ::= \"if\" assignment_expression \":\" suite\n"
            "               [\"else\" \":\" suite]\n",
            encoding="utf-8",
        )
        (docs / "reference" / "simple_stmts.txt").write_text(
            "Simple statements\n"
            "*****************\n"
            "\n"
            "   return_stmt ::= \"return\" [expression_list]\n",
            encoding="utf-8",
        )
        (docs / "tutorial" ).mkdir(parents=True, exist_ok=True)
        (docs / "tutorial" / "controlflow.txt").write_text(
            "More Control Flow Tools\n"
            "***********************\n"
            "\n"
            "   >>> for i in range(3):\n"
            "   ...     print(i)\n",
            encoding="utf-8",
        )
        return docs

    def test_ast_summary_extracts_structural_surface(self) -> None:
        summary = summarize_python_ast(
            "def all(iterable):\n"
            "    for element in iterable:\n"
            "        if not element:\n"
            "            return False\n"
            "    return True\n"
        )

        self.assertTrue(summary.is_parseable)
        self.assertIn("all", summary.defined_names)
        self.assertIn("For", summary.control_flow)
        self.assertIn("If", summary.control_flow)

    def test_extract_python_docs_file_classifies_doc_units(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            docs = self._write_python_docs(Path(temp))
            records = extract_python_docs_file(docs / "library" / "functions.txt", docs)

        kinds = [record.kind for record in records]
        self.assertIn("python_doc_section", kinds)
        self.assertIn("python_api_signature", kinds)
        self.assertIn("python_code_example", kinds)
        self.assertIn("python_doctest_example", kinds)
        code_record = next(record for record in records if record.kind == "python_code_example")
        self.assertTrue(code_record.ast_summary)
        self.assertTrue(code_record.ast_summary.is_parseable)

    def test_build_python_docs_corpus_writes_projection_cartridge(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_python_docs(root)

            result = build_python_docs_corpus(root, reset=True)
            cartridge = SemanticCartridge(result.cartridge_path)
            manifest = cartridge.manifest()
            objects = cartridge.all_objects()

        self.assertGreater(result.records_seen, 0)
        self.assertEqual(result.object_count, manifest.object_count)
        self.assertGreater(result.relation_count, 0)
        self.assertGreaterEqual(result.ast_parseable_count, 2)
        self.assertEqual(result.signature_count, 2)
        self.assertTrue(any(obj.kind == "python_grammar_rule" for obj in objects))
        self.assertTrue(any(obj.kind == "python_code_example" for obj in objects))

    def test_default_paths_are_project_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            source = default_python_docs_source_path(root)
            cartridge = default_python_docs_cartridge_path(root)

        self.assertTrue(str(source).endswith("python-3.11.15-docs-text"))
        self.assertEqual(cartridge.name, "python_docs.sqlite3")
        self.assertIn("cartridges", str(cartridge))

    def test_ingest_python_docs_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_python_docs(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["ingest-python-docs", "--reset", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertGreater(payload["records_seen"], 0)
        self.assertTrue(payload["cartridge_path"].endswith("python_docs.sqlite3"))
        self.assertGreaterEqual(payload["ast_parseable_count"], 2)


if __name__ == "__main__":
    unittest.main()
