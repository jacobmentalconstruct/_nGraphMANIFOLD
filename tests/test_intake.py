"""Phase 4 intake adapter tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.persistence import SemanticCartridge
from src.core.representation import TransformStatus
from src.core.transformation import (
    SourceDocument,
    ingest_documents_to_cartridge,
    ingest_source_to_cartridge,
    markdown_heading_text,
    read_text_source,
    semantic_objects_from_source,
    split_text_blocks,
)


class IntakeTests(unittest.TestCase):
    def test_split_text_blocks_tracks_line_spans(self) -> None:
        content = "# Title\n\nFirst paragraph.\nStill first.\n\nSecond paragraph."

        blocks = split_text_blocks(content)

        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0].line_start, 1)
        self.assertEqual(blocks[0].line_end, 1)
        self.assertEqual(blocks[1].line_start, 3)
        self.assertEqual(blocks[1].line_end, 4)
        self.assertEqual(blocks[2].block_index, 2)

    def test_markdown_heading_detection_is_conservative(self) -> None:
        self.assertEqual(markdown_heading_text("# Title"), "Title")
        self.assertEqual(markdown_heading_text("### Deep Title"), "Deep Title")
        self.assertEqual(markdown_heading_text("#"), "")
        self.assertEqual(markdown_heading_text("not # heading"), "")

    def test_source_document_emits_semantic_objects_with_provenance(self) -> None:
        document = SourceDocument(
            source_ref="fixture.md",
            content="# Title\n\nFirst paragraph.",
        )

        objects = semantic_objects_from_source(document)

        self.assertEqual(len(objects), 2)
        self.assertEqual(objects[0].kind, "heading")
        self.assertEqual(objects[1].kind, "text_block")
        self.assertEqual(objects[1].provenance[0].source_ref, "fixture.md")
        self.assertEqual(
            objects[1].provenance[0].transform_status,
            TransformStatus.IDENTITY_PRESERVING,
        )
        self.assertEqual(objects[1].occurrence.source_span.unit, "line")

    def test_read_text_source_and_ingest_to_cartridge(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            source_path = temp_path / "fixture.md"
            source_path.write_text("# Title\n\nFirst paragraph.", encoding="utf-8")
            cartridge = SemanticCartridge(temp_path / "cartridge.sqlite3")

            document = read_text_source(source_path)
            objects = ingest_source_to_cartridge(source_path, cartridge)
            manifest = cartridge.manifest()

            self.assertEqual(document.content, "# Title\n\nFirst paragraph.")
            self.assertEqual(len(objects), 2)
            self.assertEqual(manifest.object_count, 2)
            self.assertTrue(cartridge.get_object(objects[0].semantic_id))

    def test_ingest_documents_to_cartridge_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(Path(temp) / "cartridge.sqlite3")
            objects = ingest_documents_to_cartridge(
                [
                    SourceDocument(
                        source_ref="memory://fixture",
                        content="Alpha block.\n\nBeta block.",
                    )
                ],
                cartridge,
            )

            self.assertEqual(len(objects), 2)
            readiness = cartridge.readiness()
            restored = cartridge.get_object(objects[1].semantic_id)

            self.assertTrue(readiness.is_ready)
            self.assertIsNotNone(restored)
            assert restored is not None
            self.assertEqual(restored.content, "Beta block.")


if __name__ == "__main__":
    unittest.main()
