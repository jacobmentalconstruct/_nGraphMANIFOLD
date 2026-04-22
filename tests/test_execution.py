"""Phase 7 minimal execution pathway tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.analysis import (
    enrich_relations,
    persist_relation_enrichments,
    traverse_cartridge,
)
from src.core.execution import (
    ExecutionAction,
    ExecutionPlan,
    ExecutionStatus,
    SemanticIntent,
    execute_plan,
    persist_execution_result,
)
from src.core.persistence import SemanticCartridge
from src.core.representation import RelationPredicate, TransformStatus
from src.core.transformation import SourceDocument, semantic_objects_from_source


class MinimalExecutionPathwayTests(unittest.TestCase):
    def _cartridge_traversal(self, temp: str):
        cartridge = SemanticCartridge(Path(temp) / "cartridge.sqlite3")
        objects = semantic_objects_from_source(
            SourceDocument(
                source_ref="fixture.md",
                content="# Title\n\nFirst paragraph.\n\nSecond paragraph.",
            )
        )
        for obj in objects:
            cartridge.upsert_object(obj)
        relation_report = enrich_relations(objects)
        persist_relation_enrichments(cartridge, relation_report)
        traversal = traverse_cartridge(cartridge, objects[1].semantic_id, max_depth=1)
        return cartridge, objects, traversal

    def test_execution_pathway_turns_traversal_into_result_object(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, objects, traversal = self._cartridge_traversal(temp)

            intent = SemanticIntent.from_traversal(
                traversal,
                description="Summarize nearby semantic evidence.",
            )
            plan = ExecutionPlan.create(intent=intent)
            result = execute_plan(plan)

            self.assertTrue(result.is_complete)
            self.assertEqual(result.status, ExecutionStatus.COMPLETED)
            self.assertIsNotNone(result.result_object)
            assert result.result_object is not None
            self.assertEqual(result.result_object.kind, "execution_result")
            self.assertIn(objects[1].semantic_id, intent.origin_semantic_ids)
            self.assertIn("Execution report", result.output_text)

    def test_execution_result_has_feedback_relations_to_origins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, objects, traversal = self._cartridge_traversal(temp)
            intent = SemanticIntent.from_traversal(
                traversal,
                description="Render report.",
            )
            plan = ExecutionPlan.create(intent=intent)
            result = execute_plan(plan)

            assert result.result_object is not None
            predicates = [relation.predicate for relation in result.result_object.relations]
            targets = {relation.target_ref for relation in result.result_object.relations}

            self.assertIn(RelationPredicate.EXECUTES_AS, predicates)
            self.assertIn(RelationPredicate.DERIVES_FROM, predicates)
            self.assertIn(plan.plan_id, targets)
            self.assertIn(objects[1].semantic_id, targets)
            self.assertEqual(
                result.result_object.provenance[0].transform_status,
                TransformStatus.INTERPRETIVE,
            )

            persist_execution_result(cartridge, result)
            stored_relations = cartridge.relations_for(result.result_object.semantic_id)
            stored_targets = {relation["target_ref"] for relation in stored_relations}

            self.assertIn(plan.plan_id, stored_targets)
            self.assertIn(objects[1].semantic_id, stored_targets)

    def test_no_op_plan_is_bounded_and_traceable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, _, traversal = self._cartridge_traversal(temp)
            intent = SemanticIntent.from_traversal(
                traversal,
                description="Acknowledge evidence without external action.",
            )

            plan = ExecutionPlan.create(intent=intent, action=ExecutionAction.NO_OP)
            result = execute_plan(plan)

            self.assertEqual(plan.action, ExecutionAction.NO_OP)
            self.assertIn("record no-op completion", plan.steps)
            self.assertTrue(result.is_complete)
            self.assertIn("Action: no_op", result.output_text)

    def test_execution_blocks_intent_without_origins(self) -> None:
        intent = SemanticIntent.create(
            description="Invalid empty-origin intent.",
            origin_semantic_ids=(),
        )
        plan = ExecutionPlan.create(intent=intent)

        result = execute_plan(plan)

        self.assertEqual(result.status, ExecutionStatus.BLOCKED)
        self.assertFalse(result.is_complete)
        self.assertIsNone(result.result_object)
        self.assertIn("intent has no origin semantic objects", result.blockers)


if __name__ == "__main__":
    unittest.main()
