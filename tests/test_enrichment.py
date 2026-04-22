"""Phase 5 relation enrichment tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.analysis import enrich_relations, persist_relation_enrichments
from src.core.persistence import SemanticCartridge
from src.core.representation import RelationPredicate
from src.core.transformation import SourceDocument, semantic_objects_from_source


class RelationEnrichmentTests(unittest.TestCase):
    def _objects(self):
        return semantic_objects_from_source(
            SourceDocument(
                source_ref="fixture.md",
                content=(
                    "# Title\n\n"
                    "First paragraph with [docs](https://example.test/docs).\n\n"
                    "Second paragraph."
                ),
            )
        )

    def test_enrichment_emits_structural_adjacency_and_reference_relations(self) -> None:
        objects = self._objects()

        report = enrich_relations(objects)
        predicates = [item.relation.predicate for item in report.enrichments]

        self.assertEqual(report.object_count, 3)
        self.assertIn(RelationPredicate.MEMBER_OF, predicates)
        self.assertIn(RelationPredicate.PRECEDES, predicates)
        self.assertIn(RelationPredicate.FOLLOWS, predicates)
        self.assertIn(RelationPredicate.REFERENCES, predicates)

    def test_enrichment_metadata_is_traceable(self) -> None:
        report = enrich_relations(self._objects())

        for enrichment in report.enrichments:
            metadata = enrichment.relation.metadata
            self.assertEqual(metadata["enrichment_pass"], "phase5_relation_enrichment")
            self.assertEqual(metadata["enrichment_version"], "v1")
            self.assertIn("basis", metadata)
            self.assertIn("score_components", metadata)

    def test_adjacency_metadata_tracks_relation_direction(self) -> None:
        objects = self._objects()
        report = enrich_relations(objects)

        follows = [
            enrichment.relation
            for enrichment in report.enrichments
            if enrichment.semantic_id == objects[1].semantic_id
            and enrichment.relation.predicate == RelationPredicate.FOLLOWS
        ][0]
        precedes = [
            enrichment.relation
            for enrichment in report.enrichments
            if enrichment.semantic_id == objects[1].semantic_id
            and enrichment.relation.predicate == RelationPredicate.PRECEDES
        ][0]

        self.assertEqual(follows.metadata["source_block_index"], 1)
        self.assertEqual(follows.metadata["target_block_index"], 0)
        self.assertEqual(precedes.metadata["source_block_index"], 1)
        self.assertEqual(precedes.metadata["target_block_index"], 2)

    def test_persisted_enrichments_are_queryable_without_identity_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(Path(temp) / "cartridge.sqlite3")
            objects = self._objects()
            for obj in objects:
                cartridge.upsert_object(obj)
            original_id = objects[1].semantic_id

            report = enrich_relations(objects)
            persist_relation_enrichments(cartridge, report)

            restored = cartridge.get_object(original_id)
            relations = cartridge.relations_for(original_id)
            predicates = {relation["predicate"] for relation in relations}

            self.assertIsNotNone(restored)
            assert restored is not None
            self.assertEqual(restored.semantic_id, original_id)
            self.assertIn(RelationPredicate.MEMBER_OF.value, predicates)
            self.assertIn(RelationPredicate.FOLLOWS.value, predicates)
            self.assertIn(RelationPredicate.PRECEDES.value, predicates)
            self.assertIn(RelationPredicate.REFERENCES.value, predicates)


if __name__ == "__main__":
    unittest.main()
