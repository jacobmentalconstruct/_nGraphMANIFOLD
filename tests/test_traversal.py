"""Phase 6 cartridge traversal tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.analysis import (
    enrich_relations,
    persist_relation_enrichments,
    traverse_cartridge,
)
from src.core.persistence import SemanticCartridge
from src.core.representation import RelationPredicate
from src.core.transformation import SourceDocument, semantic_objects_from_source


class CartridgeTraversalTests(unittest.TestCase):
    def _cartridge_with_objects(self, temp: str):
        cartridge = SemanticCartridge(Path(temp) / "cartridge.sqlite3")
        objects = semantic_objects_from_source(
            SourceDocument(
                source_ref="fixture.md",
                content=(
                    "# Title\n\n"
                    "First paragraph with [docs](https://example.test/docs).\n\n"
                    "Second paragraph."
                ),
            )
        )
        for obj in objects:
            cartridge.upsert_object(obj)
        report = enrich_relations(objects)
        persist_relation_enrichments(cartridge, report)
        return cartridge, objects

    def test_traversal_walks_persisted_relation_neighbors(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, objects = self._cartridge_with_objects(temp)

            report = traverse_cartridge(
                cartridge,
                objects[1].semantic_id,
                max_depth=1,
            )

            self.assertTrue(report.is_ready)
            self.assertEqual(report.seed_semantic_id, objects[1].semantic_id)
            self.assertIn(objects[0].semantic_id, report.visited_semantic_ids)
            self.assertIn(objects[2].semantic_id, report.visited_semantic_ids)
            self.assertGreaterEqual(report.step_count, 1)

    def test_traversal_records_traceable_scoring_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, objects = self._cartridge_with_objects(temp)

            report = traverse_cartridge(cartridge, objects[1].semantic_id, max_depth=1)
            relation_steps = [
                step
                for step in report.steps
                if step.predicate == RelationPredicate.PRECEDES.value
                and step.reached_semantic_id == objects[2].semantic_id
            ]

            self.assertEqual(len(relation_steps), 1)
            step = relation_steps[0]
            self.assertEqual(step.direction, "outgoing")
            self.assertEqual(step.depth, 1)
            self.assertEqual(step.score, 0.765)
            self.assertEqual(step.cumulative_score, 0.765)
            self.assertEqual(
                step.relation_metadata["enrichment_pass"],
                "phase5_relation_enrichment",
            )

    def test_traversal_preserves_non_semantic_reference_targets_in_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, objects = self._cartridge_with_objects(temp)

            report = traverse_cartridge(cartridge, objects[1].semantic_id, max_depth=1)
            reference_steps = [
                step
                for step in report.steps
                if step.predicate == RelationPredicate.REFERENCES.value
            ]

            self.assertEqual(len(reference_steps), 1)
            self.assertEqual(reference_steps[0].target_ref, "https://example.test/docs")
            self.assertIsNone(reference_steps[0].reached_semantic_id)

    def test_traversal_reports_blockers_for_empty_or_missing_seed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(Path(temp) / "empty.sqlite3")

            report = traverse_cartridge(cartridge, "sem:v1:missing")

            self.assertFalse(report.is_ready)
            self.assertIn("no semantic objects stored", report.blockers)
            self.assertIn("no semantic relations stored", report.blockers)
            self.assertIn("seed semantic object not found", report.blockers)
            self.assertEqual(report.steps, ())

    def test_relations_targeting_reads_incoming_projection_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, objects = self._cartridge_with_objects(temp)

            incoming = cartridge.relations_targeting(objects[1].semantic_id)
            sources = {row["semantic_id"] for row in incoming}
            predicates = {row["relation"]["predicate"] for row in incoming}

            self.assertIn(objects[0].semantic_id, sources)
            self.assertIn(RelationPredicate.PRECEDES.value, predicates)


if __name__ == "__main__":
    unittest.main()
