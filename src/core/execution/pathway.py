"""Minimal semantic execution pathway for the prototype spine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.analysis import TraversalReport
from src.core.persistence import SemanticCartridge
from src.core.representation import (
    ProvenanceRecord,
    RelationPredicate,
    SemanticObject,
    SemanticRelation,
    SemanticSurfaceSet,
    TransformStatus,
)
from src.core.representation.canonical import normalize_for_identity, versioned_digest

EXECUTION_VERSION = "v1"
EXECUTION_METHOD = "phase7_minimal_execution_pathway"


class ExecutionAction(str, Enum):
    """Prototype execution actions allowed by Phase 7."""

    REPORT_GENERATION = "report_generation"
    NO_OP = "no_op"


class ExecutionStatus(str, Enum):
    """Execution result status."""

    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SemanticIntent:
    """A semantic intent anchored to source semantic objects."""

    intent_id: str
    description: str
    origin_semantic_ids: tuple[str, ...]
    traversal_artifact_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        description: str,
        origin_semantic_ids: tuple[str, ...] | list[str],
        traversal_artifact_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "SemanticIntent":
        origins = tuple(origin_semantic_ids)
        intent_metadata = metadata or {}
        envelope = {
            "description": description,
            "origin_semantic_ids": origins,
            "traversal_artifact_id": traversal_artifact_id,
            "metadata": normalize_for_identity(intent_metadata),
        }
        return cls(
            intent_id=versioned_digest("intent", EXECUTION_VERSION, envelope),
            description=description,
            origin_semantic_ids=origins,
            traversal_artifact_id=traversal_artifact_id,
            metadata=intent_metadata,
        )

    @classmethod
    def from_traversal(
        cls,
        traversal: TraversalReport,
        *,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> "SemanticIntent":
        origins = traversal.visited_semantic_ids or (traversal.seed_semantic_id,)
        return cls.create(
            description=description,
            origin_semantic_ids=origins,
            traversal_artifact_id=traversal.artifact_id,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "description": self.description,
            "origin_semantic_ids": list(self.origin_semantic_ids),
            "traversal_artifact_id": self.traversal_artifact_id,
            "metadata": normalize_for_identity(self.metadata),
        }


@dataclass(frozen=True)
class ExecutionPlan:
    """Inspectable plan that turns semantic intent into bounded action."""

    plan_id: str
    intent: SemanticIntent
    action: ExecutionAction
    steps: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        intent: SemanticIntent,
        action: ExecutionAction = ExecutionAction.REPORT_GENERATION,
        steps: tuple[str, ...] | list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ExecutionPlan":
        plan_steps = tuple(steps or _default_steps(action))
        plan_metadata = metadata or {}
        envelope = {
            "intent": intent.to_dict(),
            "action": action.value,
            "steps": plan_steps,
            "metadata": normalize_for_identity(plan_metadata),
        }
        return cls(
            plan_id=versioned_digest("plan", EXECUTION_VERSION, envelope),
            intent=intent,
            action=action,
            steps=plan_steps,
            metadata=plan_metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "intent": self.intent.to_dict(),
            "action": self.action.value,
            "steps": list(self.steps),
            "metadata": normalize_for_identity(self.metadata),
        }


@dataclass(frozen=True)
class ExecutionResult:
    """Result of a bounded semantic execution plan."""

    result_id: str
    plan: ExecutionPlan
    status: ExecutionStatus
    output_text: str
    result_object: SemanticObject | None
    blockers: tuple[str, ...] = ()

    @property
    def is_complete(self) -> bool:
        return self.status == ExecutionStatus.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "plan_id": self.plan.plan_id,
            "intent_id": self.plan.intent.intent_id,
            "status": self.status.value,
            "output_text": self.output_text,
            "result_semantic_id": self.result_object.semantic_id if self.result_object else None,
            "blockers": list(self.blockers),
        }


def execute_plan(plan: ExecutionPlan) -> ExecutionResult:
    """Execute a bounded prototype plan and return an inspectable result."""
    blockers: list[str] = []
    if not plan.intent.origin_semantic_ids:
        blockers.append("intent has no origin semantic objects")

    status = ExecutionStatus.BLOCKED if blockers else ExecutionStatus.COMPLETED
    output_text = _render_output(plan, status, tuple(blockers))
    result_object = None
    if status == ExecutionStatus.COMPLETED:
        result_object = _result_semantic_object(plan, output_text)

    result_id = versioned_digest(
        "exec",
        EXECUTION_VERSION,
        {
            "plan_id": plan.plan_id,
            "status": status.value,
            "output_text": output_text,
            "result_semantic_id": result_object.semantic_id if result_object else None,
            "blockers": blockers,
        },
    )
    return ExecutionResult(
        result_id=result_id,
        plan=plan,
        status=status,
        output_text=output_text,
        result_object=result_object,
        blockers=tuple(blockers),
    )


def persist_execution_result(
    cartridge: SemanticCartridge,
    result: ExecutionResult,
) -> None:
    """Persist the semantic result object produced by execution."""
    if result.result_object is None:
        raise ValueError("Cannot persist a blocked execution result without a semantic result object")
    cartridge.upsert_object(result.result_object)


def _result_semantic_object(plan: ExecutionPlan, output_text: str) -> SemanticObject:
    source_ref = f"execution:{plan.plan_id}"
    relations = [
        SemanticRelation(
            predicate=RelationPredicate.EXECUTES_AS,
            target_ref=plan.plan_id,
            source_ref=source_ref,
            weight=1.0,
            confidence=1.0,
            metadata={
                "execution_method": EXECUTION_METHOD,
                "intent_id": plan.intent.intent_id,
                "action": plan.action.value,
            },
        )
    ]
    for origin_id in plan.intent.origin_semantic_ids:
        relations.append(
            SemanticRelation(
                predicate=RelationPredicate.DERIVES_FROM,
                target_ref=origin_id,
                source_ref=source_ref,
                weight=1.0,
                confidence=1.0,
                metadata={
                    "execution_method": EXECUTION_METHOD,
                    "intent_id": plan.intent.intent_id,
                    "feedback_role": "origin_semantic_object",
                },
            )
        )

    line_count = len(output_text.splitlines())
    token_count = len(output_text.split())
    surfaces = SemanticSurfaceSet(
        verbatim={"content": output_text},
        structural={
            "intent_id": plan.intent.intent_id,
            "plan_id": plan.plan_id,
            "action": plan.action.value,
            "origin_count": len(plan.intent.origin_semantic_ids),
        },
        grammatical={
            "node_kind": "execution_result",
            "format": "plain_text_report",
        },
        statistical={
            "line_count": line_count,
            "token_count": token_count,
            "char_count": len(output_text),
        },
        semantic={
            "execution_status": ExecutionStatus.COMPLETED.value,
            "traversal_artifact_id": plan.intent.traversal_artifact_id,
        },
    )
    provenance = ProvenanceRecord(
        source_ref=source_ref,
        transform_status=TransformStatus.INTERPRETIVE,
        method=EXECUTION_METHOD,
        derived_from=plan.intent.origin_semantic_ids,
        confidence=1.0,
        metadata={
            "intent_id": plan.intent.intent_id,
            "plan_id": plan.plan_id,
            "action": plan.action.value,
        },
    )
    return SemanticObject.create(
        kind="execution_result",
        content=output_text,
        surfaces=surfaces,
        relations=tuple(relations),
        provenance=(provenance,),
        source_ref=source_ref,
        local_context={
            "intent_id": plan.intent.intent_id,
            "plan_id": plan.plan_id,
            "action": plan.action.value,
        },
        metadata={
            "execution_method": EXECUTION_METHOD,
            "execution_version": EXECUTION_VERSION,
        },
    )


def _render_output(
    plan: ExecutionPlan,
    status: ExecutionStatus,
    blockers: tuple[str, ...],
) -> str:
    lines = [
        "Execution report",
        f"Status: {status.value}",
        f"Action: {plan.action.value}",
        f"Intent: {plan.intent.description}",
        f"Intent ID: {plan.intent.intent_id}",
        f"Plan ID: {plan.plan_id}",
        f"Traversal artifact: {plan.intent.traversal_artifact_id or 'none'}",
        f"Origin count: {len(plan.intent.origin_semantic_ids)}",
    ]
    if blockers:
        lines.append("Blockers:")
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("Origin semantic IDs:")
        lines.extend(f"- {origin_id}" for origin_id in plan.intent.origin_semantic_ids)
    return "\n".join(lines)


def _default_steps(action: ExecutionAction) -> tuple[str, ...]:
    if action == ExecutionAction.NO_OP:
        return (
            "validate semantic intent",
            "record no-op completion",
            "emit semantic feedback result",
        )
    return (
        "validate semantic intent",
        "render traversal-informed report",
        "emit semantic feedback result",
    )
