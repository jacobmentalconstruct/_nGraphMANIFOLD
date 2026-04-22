"""Prototype tuning harness for builder-usefulness scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.analysis import enrich_relations, persist_relation_enrichments, traverse_cartridge
from src.core.execution import ExecutionPlan, SemanticIntent, execute_plan, persist_execution_result
from src.core.persistence import SemanticCartridge
from src.core.transformation import SourceDocument, semantic_objects_from_source

from .mcp_seam import (
    McpSeamManifest,
    McpUsefulnessReport,
    McpUsefulnessSignal,
    build_mcp_seam_manifest,
    evaluate_mcp_usefulness,
)


@dataclass(frozen=True)
class PrototypeTuningFixture:
    """One repeatable builder-task fixture for seam usefulness scoring."""

    fixture_id: str
    task_description: str
    source_ref: str
    content: str
    seed_block_index: int
    intent_description: str

    def source_document(self) -> SourceDocument:
        return SourceDocument(source_ref=self.source_ref, content=self.content)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "task_description": self.task_description,
            "source_ref": self.source_ref,
            "seed_block_index": self.seed_block_index,
            "intent_description": self.intent_description,
        }


@dataclass(frozen=True)
class PrototypeTuningRun:
    """Result of running one fixture through the prototype spine."""

    fixture: PrototypeTuningFixture
    seam_manifest: McpSeamManifest
    usefulness_report: McpUsefulnessReport
    object_count: int
    relation_count: int
    traversal_step_count: int
    execution_complete: bool
    result_semantic_id: str | None
    recommended_next_capability: str | None

    @property
    def meets_acceptance(self) -> bool:
        return self.usefulness_report.meets_acceptance

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture": self.fixture.to_dict(),
            "seam_manifest": self.seam_manifest.to_dict(),
            "usefulness_report": self.usefulness_report.to_dict(),
            "object_count": self.object_count,
            "relation_count": self.relation_count,
            "traversal_step_count": self.traversal_step_count,
            "execution_complete": self.execution_complete,
            "result_semantic_id": self.result_semantic_id,
            "recommended_next_capability": self.recommended_next_capability,
            "meets_acceptance": self.meets_acceptance,
        }


def default_builder_task_fixtures() -> tuple[PrototypeTuningFixture, ...]:
    """Return repeatable fixtures for near-term builder-usefulness scoring."""
    return (
        PrototypeTuningFixture(
            fixture_id="relation_evidence_trace",
            task_description="Find nearby semantic evidence and relation context for a focused source block.",
            source_ref="fixture://relation-evidence",
            content="# Plan\n\nBuild the cartridge spine.\n\nUse [contract](contract://builder) as authority.",
            seed_block_index=1,
            intent_description="Summarize nearby relation evidence for the builder.",
        ),
        PrototypeTuningFixture(
            fixture_id="execution_report_trace",
            task_description="Turn traversal evidence into a traceable report without taking external action.",
            source_ref="fixture://execution-report",
            content="# Execution\n\nGenerate a no-op report from semantic evidence.\n\nRecord feedback relations.",
            seed_block_index=1,
            intent_description="Generate a bounded execution report for builder inspection.",
        ),
        PrototypeTuningFixture(
            fixture_id="persistence_round_trip",
            task_description="Verify semantic objects, relations, traversal, and execution result survive cartridge persistence.",
            source_ref="fixture://persistence-round-trip",
            content="# Persistence\n\nStore semantic objects.\n\nRead relation projections back for analysis.",
            seed_block_index=2,
            intent_description="Report on persisted semantic evidence and feedback.",
        ),
    )


def run_prototype_tuning_fixture(
    fixture: PrototypeTuningFixture,
    db_path: Path | str,
) -> PrototypeTuningRun:
    """Run one fixture through the spine and score builder usefulness."""
    seam_manifest = build_mcp_seam_manifest()
    cartridge = SemanticCartridge(db_path)
    objects = semantic_objects_from_source(fixture.source_document())
    for obj in objects:
        cartridge.upsert_object(obj)

    enrichment_report = enrich_relations(objects)
    persist_relation_enrichments(cartridge, enrichment_report)

    seed = _seed_object_id(objects, fixture.seed_block_index)
    traversal = traverse_cartridge(cartridge, seed, max_depth=2)
    intent = SemanticIntent.from_traversal(
        traversal,
        description=fixture.intent_description,
        metadata={"fixture_id": fixture.fixture_id},
    )
    plan = ExecutionPlan.create(intent=intent)
    execution_result = execute_plan(plan)
    if execution_result.result_object is not None:
        persist_execution_result(cartridge, execution_result)

    manifest = cartridge.manifest()
    signals = _score_fixture(
        object_count=len(objects),
        relation_count=manifest.relation_count,
        traversal_step_count=traversal.step_count,
        execution_complete=execution_result.is_complete,
        result_persisted=execution_result.result_object is not None
        and cartridge.get_object(execution_result.result_object.semantic_id) is not None,
    )
    usefulness_report = evaluate_mcp_usefulness(signals)
    return PrototypeTuningRun(
        fixture=fixture,
        seam_manifest=seam_manifest,
        usefulness_report=usefulness_report,
        object_count=len(objects),
        relation_count=manifest.relation_count,
        traversal_step_count=traversal.step_count,
        execution_complete=execution_result.is_complete,
        result_semantic_id=execution_result.result_object.semantic_id
        if execution_result.result_object
        else None,
        recommended_next_capability=_recommended_next_capability(usefulness_report),
    )


def _seed_object_id(objects: list[Any], seed_block_index: int) -> str:
    for obj in objects:
        if int(obj.surfaces.structural.get("block_index", -1)) == seed_block_index:
            return obj.semantic_id
    if not objects:
        raise ValueError("Fixture produced no semantic objects")
    return objects[0].semantic_id


def _score_fixture(
    *,
    object_count: int,
    relation_count: int,
    traversal_step_count: int,
    execution_complete: bool,
    result_persisted: bool,
) -> tuple[McpUsefulnessSignal, ...]:
    object_signal = 1.0 if object_count > 0 else 0.0
    relation_signal = min(1.0, relation_count / 4.0)
    traversal_signal = min(1.0, traversal_step_count / 3.0)
    execution_signal = 1.0 if execution_complete else 0.0
    persistence_signal = 1.0 if result_persisted else 0.0

    return (
        McpUsefulnessSignal(
            capability_name="transformation.semantic_objects_from_source",
            task_fit=object_signal,
            evidence_quality=object_signal,
            actionability=0.8 if object_signal else 0.0,
            friction_reduction=0.75 if object_signal else 0.0,
            repeatability=1.0,
            notes=f"emitted {object_count} semantic objects",
        ),
        McpUsefulnessSignal(
            capability_name="analysis.enrich_relations",
            task_fit=relation_signal,
            evidence_quality=relation_signal,
            actionability=0.8 if relation_count else 0.0,
            friction_reduction=0.75 if relation_count else 0.0,
            repeatability=1.0,
            notes=f"stored {relation_count} relation projections",
        ),
        McpUsefulnessSignal(
            capability_name="analysis.traverse_cartridge",
            task_fit=traversal_signal,
            evidence_quality=traversal_signal,
            actionability=0.85 if traversal_step_count else 0.0,
            friction_reduction=0.8 if traversal_step_count else 0.0,
            repeatability=1.0,
            notes=f"walked {traversal_step_count} traversal steps",
        ),
        McpUsefulnessSignal(
            capability_name="coordination.project_context_query",
            task_fit=0.8 if traversal_step_count else 0.4,
            evidence_quality=0.8 if relation_count else 0.4,
            actionability=0.8,
            friction_reduction=0.75,
            repeatability=1.0,
            notes="shared command spine is available; projection cartridges are scored in dedicated fixtures",
        ),
        McpUsefulnessSignal(
            capability_name="execution.execute_plan",
            task_fit=execution_signal,
            evidence_quality=0.85 if execution_complete else 0.0,
            actionability=0.85 if execution_complete else 0.0,
            friction_reduction=0.75 if execution_complete else 0.0,
            repeatability=1.0,
            notes="execution completed" if execution_complete else "execution blocked",
        ),
        McpUsefulnessSignal(
            capability_name="persistence.semantic_cartridge",
            task_fit=persistence_signal,
            evidence_quality=persistence_signal,
            actionability=0.8 if result_persisted else 0.0,
            friction_reduction=0.75 if result_persisted else 0.0,
            repeatability=1.0,
            notes="execution result persisted" if result_persisted else "execution result not persisted",
        ),
    )


def _recommended_next_capability(report: McpUsefulnessReport) -> str | None:
    if not report.signals:
        return None
    weakest = min(report.signals, key=lambda signal: signal.score)
    if weakest.score >= report.acceptance_threshold:
        return "analysis.traverse_cartridge"
    return weakest.capability_name
