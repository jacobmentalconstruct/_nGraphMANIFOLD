"""Canonical semantic object tests."""

from __future__ import annotations

import json
import unittest

from src.core.representation import (
    ProvenanceRecord,
    RelationPredicate,
    SemanticObject,
    SemanticRelation,
    SemanticSurfaceSet,
    SourceSpan,
    TransformStatus,
    canonical_json,
)


class RepresentationTests(unittest.TestCase):
    def _sample_surfaces(self) -> SemanticSurfaceSet:
        return SemanticSurfaceSet(
            verbatim={"content": "alpha beta"},
            structural={"path": ["root", "section"], "position": 1},
            grammatical={"node_kind": "paragraph"},
            statistical={"token_count": 2},
            semantic={"keywords": ["alpha", "beta"]},
        )

    def test_semantic_id_is_deterministic(self) -> None:
        first = SemanticObject.create(
            kind="paragraph",
            content="alpha beta",
            surfaces=self._sample_surfaces(),
            metadata={"b": 2, "a": 1},
        )
        second = SemanticObject.create(
            kind="paragraph",
            content="alpha beta",
            surfaces=self._sample_surfaces(),
            metadata={"a": 1, "b": 2},
        )
        self.assertEqual(first.semantic_id, second.semantic_id)
        self.assertTrue(first.semantic_id.startswith("sem:v1:"))

    def test_semantic_id_ignores_source_occurrence(self) -> None:
        first = SemanticObject.create(
            kind="paragraph",
            content="alpha beta",
            surfaces=self._sample_surfaces(),
            source_ref="C:/one/source.md",
            source_span=SourceSpan(start=0, end=10),
        )
        second = SemanticObject.create(
            kind="paragraph",
            content="alpha beta",
            surfaces=self._sample_surfaces(),
            source_ref="C:/two/source.md",
            source_span=SourceSpan(start=50, end=60),
        )
        self.assertEqual(first.semantic_id, second.semantic_id)
        self.assertNotEqual(first.occurrence_id, second.occurrence_id)
        self.assertTrue(first.occurrence_id and first.occurrence_id.startswith("occ:v1:"))

    def test_semantic_id_changes_when_meaning_payload_changes(self) -> None:
        first = SemanticObject.create(kind="paragraph", content="alpha beta")
        second = SemanticObject.create(kind="paragraph", content="alpha gamma")
        self.assertNotEqual(first.semantic_id, second.semantic_id)

    def test_relation_and_provenance_round_trip(self) -> None:
        relation = SemanticRelation(
            predicate=RelationPredicate.REFERENCES,
            target_ref="sem:v1:target",
            weight=0.8,
            confidence=0.7,
            metadata={"surface": "structural"},
        )
        provenance = ProvenanceRecord(
            source_ref="fixture.md",
            transform_status=TransformStatus.IDENTITY_PRESERVING,
            method="unit-test",
            confidence=0.99,
        )
        obj = SemanticObject.create(
            kind="paragraph",
            content="alpha beta",
            surfaces=self._sample_surfaces(),
            relations=(relation,),
            provenance=(provenance,),
            source_ref="fixture.md",
            source_span=SourceSpan(start=1, end=2, unit="line"),
        )

        restored = SemanticObject.from_dict(json.loads(obj.to_json()))

        self.assertEqual(restored.semantic_id, obj.semantic_id)
        self.assertEqual(restored.occurrence_id, obj.occurrence_id)
        self.assertEqual(restored.relations[0].predicate, RelationPredicate.REFERENCES)
        self.assertEqual(
            restored.provenance[0].transform_status,
            TransformStatus.IDENTITY_PRESERVING,
        )

    def test_canonical_json_sorts_nested_mapping_keys(self) -> None:
        left = canonical_json({"b": {"d": 4, "c": 3}, "a": 1})
        right = canonical_json({"a": 1, "b": {"c": 3, "d": 4}})
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
