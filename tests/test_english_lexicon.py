"""English lexical baseline tests."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.app import main
from src.core.coordination import build_english_lexicon_baseline, lookup_english_lexicon_entry
from src.core.persistence import SemanticCartridge
from src.core.transformation import (
    iter_dictionary_alpha_entries,
    lexical_entry_to_semantic_object,
    parse_dictionary_entry,
)


class EnglishLexiconTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> Path:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[\n'
            '  {\n'
            '    "tortuous" : "1. Bent in different directions; as, a tortuous train. '
            'Macaulay. 2. Fig.: Deviating from rectitude; indirect; deceitful. '
            '3. (Astrol.) Oblique. --Tor\\"tu*ous*ly, adv.",\n'
            '    "truster" : "1. One who trusts, or credits. 2. (Scots Law) '
            'One who makes a trust; -- the correlative of trustee.",\n'
            '    "true-blue" : "Of inflexible honesty and fidelity; -- a term derived '
            'from the true, or Coventry, blue. See True blue, under Blue."\n'
            '  }\n'
            ']\n',
            encoding="utf-8",
        )
        return source

    def test_parse_dictionary_entry_extracts_schema_hints(self) -> None:
        entry = parse_dictionary_entry(
            "tortuous",
            '1. Bent in different directions; as, a tortuous train. The badger made his dark and tortuous hole. Macaulay. '
            '2. (Astrol.) Oblique. --Tor"tu*ous*ly, adv.',
        )

        self.assertEqual(entry.normalized_headword, "tortuous")
        self.assertEqual(len(entry.senses), 2)
        self.assertIn("Astrol", entry.domain_labels)
        self.assertTrue(entry.derived_forms)
        self.assertIn("a tortuous train.", entry.senses[0].usage_examples)
        self.assertIn("The badger made his dark and tortuous hole.", entry.senses[0].usage_examples)

    def test_stream_dictionary_entries_without_loading_full_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = self._write_dictionary(Path(temp))

            entries = list(iter_dictionary_alpha_entries(source))

        self.assertEqual([entry.headword for entry in entries], ["tortuous", "truster", "true-blue"])
        self.assertEqual(entries[1].domain_labels, ("Scots Law",))

    def test_lexical_entry_semantic_object_preserves_raw_definition(self) -> None:
        entry = parse_dictionary_entry("true-blue", "See True blue, under Blue.")

        obj = lexical_entry_to_semantic_object(entry)

        self.assertEqual(obj.kind, "lexical_entry")
        self.assertEqual(obj.metadata["normalized_headword"], "true-blue")
        self.assertIn("definition_raw", obj.surfaces.verbatim)
        self.assertGreaterEqual(len(obj.relations), 2)

    def test_build_english_lexicon_baseline_writes_limited_cartridge(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_dictionary(root)

            result = build_english_lexicon_baseline(root, limit=2, reset=True)
            cartridge = SemanticCartridge(result.cartridge_path)
            manifest = cartridge.manifest()

        self.assertEqual(result.entries_seen, 2)
        self.assertEqual(result.objects_written, 2)
        self.assertEqual(manifest.object_count, 2)
        self.assertIn("tortuous", result.sample_headwords)

    def test_lookup_english_lexicon_entry_returns_caution_and_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_dictionary(root)
            build_english_lexicon_baseline(root, reset=True)

            result = lookup_english_lexicon_entry(root, "tortuous")

        payload = result.to_dict()
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["candidates"][0]["headword"], "tortuous")
        self.assertGreaterEqual(payload["candidates"][0]["usage_example_count"], 1)
        self.assertIn("Alpha-array entries are reliable", payload["caution"])

    def test_ingest_lexicon_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_dictionary(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["ingest-lexicon", "--limit", "2", "--reset", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["entries_seen"], 2)
        self.assertTrue(payload["cartridge_path"].endswith("base_english_lexicon.sqlite3"))

    def test_lookup_lexicon_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_dictionary(root)
            build_english_lexicon_baseline(root, reset=True)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["lookup-lexicon", "--query", "true-blue", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["candidates"][0]["headword"], "true-blue")


if __name__ == "__main__":
    unittest.main()
