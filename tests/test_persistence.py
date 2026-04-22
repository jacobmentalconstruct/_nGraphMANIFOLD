"""Semantic cartridge persistence tests."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.core.persistence import SCHEMA_VERSION, SemanticCartridge, expected_tables
from src.core.representation import (
    ProvenanceRecord,
    RelationPredicate,
    SemanticObject,
    SemanticRelation,
    SemanticSurfaceSet,
    SourceSpan,
    TransformStatus,
)


class PersistenceTests(unittest.TestCase):
    def _db_path(self, temp_dir: str) -> Path:
        return Path(temp_dir) / "semantic-cartridge.sqlite3"

    def _semantic_object(self) -> SemanticObject:
        return SemanticObject.create(
            kind="paragraph",
            content="alpha beta",
            surfaces=SemanticSurfaceSet(
                verbatim={"content": "alpha beta"},
                structural={"section": "intro"},
                grammatical={"node_kind": "paragraph"},
                statistical={"token_count": 2},
                semantic={"keywords": ["alpha", "beta"]},
            ),
            relations=(
                SemanticRelation(
                    predicate=RelationPredicate.REFERENCES,
                    target_ref="sem:v1:target",
                    weight=0.75,
                    confidence=0.8,
                ),
            ),
            provenance=(
                ProvenanceRecord(
                    source_ref="fixture.md",
                    transform_status=TransformStatus.IDENTITY_PRESERVING,
                    method="unit-test",
                ),
            ),
            source_ref="fixture.md",
            source_span=SourceSpan(start=1, end=2, unit="line"),
            local_context={"heading": "Intro"},
        )

    def test_initialize_creates_expected_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self._db_path(temp)
            cartridge = SemanticCartridge(path)
            cartridge.initialize()

            conn = sqlite3.connect(path)
            try:
                table_names = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                user_version = conn.execute("PRAGMA user_version").fetchone()[0]
            finally:
                conn.close()

            self.assertTrue(set(expected_tables()).issubset(table_names))
            self.assertEqual(user_version, SCHEMA_VERSION)

    def test_object_round_trip_preserves_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(self._db_path(temp))
            obj = self._semantic_object()

            cartridge.upsert_object(obj)
            restored = cartridge.get_object(obj.semantic_id)

            self.assertIsNotNone(restored)
            assert restored is not None
            self.assertEqual(restored.semantic_id, obj.semantic_id)
            self.assertEqual(restored.occurrence_id, obj.occurrence_id)
            self.assertEqual(restored.content, "alpha beta")

    def test_occurrence_relation_and_provenance_are_queryable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(self._db_path(temp))
            obj = self._semantic_object()

            cartridge.upsert_object(obj)

            assert obj.occurrence_id is not None
            occurrence = cartridge.get_occurrence(obj.occurrence_id)
            relations = cartridge.relations_for(obj.semantic_id)
            provenance = cartridge.provenance_for(obj.semantic_id)

            self.assertEqual(occurrence["source_ref"], "fixture.md")
            self.assertEqual(relations[0]["predicate"], RelationPredicate.REFERENCES.value)
            self.assertEqual(provenance[0]["transform_status"], TransformStatus.IDENTITY_PRESERVING.value)

    def test_manifest_and_readiness_counts_update(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(self._db_path(temp))

            initial = cartridge.readiness()
            self.assertFalse(initial.is_ready)
            self.assertIn("no semantic objects stored", initial.blockers)

            cartridge.upsert_object(self._semantic_object())
            manifest = cartridge.manifest()
            readiness = cartridge.readiness()

            self.assertTrue(manifest.is_ready)
            self.assertEqual(manifest.object_count, 1)
            self.assertEqual(manifest.occurrence_count, 1)
            self.assertEqual(manifest.relation_count, 1)
            self.assertEqual(manifest.provenance_count, 1)
            self.assertTrue(readiness.is_ready)
            self.assertEqual(readiness.blockers, ())

    def test_upsert_replaces_relation_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(self._db_path(temp))
            obj = self._semantic_object()
            cartridge.upsert_object(obj)
            cartridge.upsert_object(obj)

            relations = cartridge.relations_for(obj.semantic_id)
            manifest = cartridge.manifest()

            self.assertEqual(len(relations), 1)
            self.assertEqual(manifest.relation_count, 1)

    def test_upsert_objects_refreshes_manifest_once_for_batch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(self._db_path(temp))
            first = self._semantic_object()
            second = SemanticObject.create(
                kind="paragraph",
                content="gamma delta",
                source_ref="fixture.md",
                source_span=SourceSpan(start=3, end=4, unit="line"),
            )

            count = cartridge.upsert_objects((first, second))
            manifest = cartridge.manifest()

            self.assertEqual(count, 2)
            self.assertEqual(manifest.object_count, 2)
            self.assertEqual(manifest.occurrence_count, 2)

    def test_upsert_relations_preserves_non_enrichment_relations(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge = SemanticCartridge(self._db_path(temp))
            obj = self._semantic_object()
            cartridge.upsert_object(obj)

            cartridge.upsert_relations(
                obj.semantic_id,
                (
                    SemanticRelation(
                        predicate=RelationPredicate.MEMBER_OF,
                        target_ref="fixture.md",
                        source_ref="fixture.md",
                        metadata={
                            "enrichment_pass": "phase5_relation_enrichment",
                            "basis": "unit-test",
                        },
                    ),
                ),
            )

            predicates = {
                relation["predicate"]
                for relation in cartridge.relations_for(obj.semantic_id)
            }

            self.assertEqual(
                predicates,
                {RelationPredicate.REFERENCES.value, RelationPredicate.MEMBER_OF.value},
            )


if __name__ == "__main__":
    unittest.main()
