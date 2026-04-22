"""Thin MCP usefulness seam for builder-facing prototype capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.representation.canonical import normalize_for_identity, versioned_digest

MCP_SEAM_VERSION = "v1"
MCP_USEFULNESS_ACCEPTANCE_THRESHOLD = 0.7


@dataclass(frozen=True)
class McpCapabilityDescriptor:
    """Capability shape intended for a future MCP wrapper."""

    name: str
    layer: str
    purpose: str
    input_shape: dict[str, str]
    output_shape: dict[str, str]
    usefulness_weight: float
    readiness: str = "prototype"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "layer": self.layer,
            "purpose": self.purpose,
            "input_shape": normalize_for_identity(self.input_shape),
            "output_shape": normalize_for_identity(self.output_shape),
            "usefulness_weight": self.usefulness_weight,
            "readiness": self.readiness,
        }


@dataclass(frozen=True)
class McpUsefulnessSignal:
    """One builder-usefulness score for an exposed capability."""

    capability_name: str
    task_fit: float
    evidence_quality: float
    actionability: float
    friction_reduction: float
    repeatability: float
    notes: str = ""

    @property
    def score(self) -> float:
        values = (
            _clamp01(self.task_fit),
            _clamp01(self.evidence_quality),
            _clamp01(self.actionability),
            _clamp01(self.friction_reduction),
            _clamp01(self.repeatability),
        )
        return round(sum(values) / len(values), 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "task_fit": _clamp01(self.task_fit),
            "evidence_quality": _clamp01(self.evidence_quality),
            "actionability": _clamp01(self.actionability),
            "friction_reduction": _clamp01(self.friction_reduction),
            "repeatability": _clamp01(self.repeatability),
            "score": self.score,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class McpUsefulnessReport:
    """Aggregate usefulness report for MCP seam evaluation."""

    report_id: str
    signals: tuple[McpUsefulnessSignal, ...]
    aggregate_score: float
    acceptance_threshold: float

    @property
    def meets_acceptance(self) -> bool:
        return self.aggregate_score >= self.acceptance_threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "signals": [signal.to_dict() for signal in self.signals],
            "aggregate_score": self.aggregate_score,
            "acceptance_threshold": self.acceptance_threshold,
            "meets_acceptance": self.meets_acceptance,
        }


@dataclass(frozen=True)
class McpSeamManifest:
    """Stable manifest for future MCP-facing capability exposure."""

    seam_id: str
    version: str
    status: str
    capabilities: tuple[McpCapabilityDescriptor, ...]
    scoring_dimensions: tuple[str, ...]
    non_goals: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seam_id": self.seam_id,
            "version": self.version,
            "status": self.status,
            "capabilities": [capability.to_dict() for capability in self.capabilities],
            "scoring_dimensions": list(self.scoring_dimensions),
            "non_goals": list(self.non_goals),
        }


def build_mcp_seam_manifest() -> McpSeamManifest:
    """Return the current thin seam manifest without starting a server."""
    capabilities = (
        McpCapabilityDescriptor(
            name="transformation.semantic_objects_from_source",
            layer="transformation",
            purpose="turn source text into canonical semantic objects",
            input_shape={"source_ref": "string", "content": "string"},
            output_shape={"semantic_objects": "list[SemanticObject]"},
            usefulness_weight=0.85,
        ),
        McpCapabilityDescriptor(
            name="analysis.enrich_relations",
            layer="analysis",
            purpose="emit structural, adjacency, and reference relation projections",
            input_shape={"semantic_objects": "list[SemanticObject]"},
            output_shape={"relation_enrichment_report": "RelationEnrichmentReport"},
            usefulness_weight=0.8,
        ),
        McpCapabilityDescriptor(
            name="analysis.traverse_cartridge",
            layer="analysis",
            purpose="walk persisted relation projections from a seed semantic object",
            input_shape={"cartridge": "SemanticCartridge", "seed_semantic_id": "string"},
            output_shape={"traversal_report": "TraversalReport"},
            usefulness_weight=0.95,
        ),
        McpCapabilityDescriptor(
            name="coordination.project_context_query",
            layer="coordination",
            purpose="project a query through separated context layers and return shared inspection evidence",
            input_shape={"query": "string", "limit": "integer", "context_stack": "list[string]"},
            output_shape={
                "command": "CommandEnvelope",
                "result": "ToolResultEnvelope",
                "projection_frame": "QueryProjectionFrame",
            },
            usefulness_weight=0.95,
        ),
        McpCapabilityDescriptor(
            name="execution.execute_plan",
            layer="execution",
            purpose="turn semantic intent into a bounded report or no-op result",
            input_shape={"execution_plan": "ExecutionPlan"},
            output_shape={"execution_result": "ExecutionResult"},
            usefulness_weight=0.9,
        ),
        McpCapabilityDescriptor(
            name="persistence.semantic_cartridge",
            layer="persistence",
            purpose="persist and query semantic objects, relations, and provenance",
            input_shape={"db_path": "path", "semantic_object": "SemanticObject"},
            output_shape={"manifest": "CartridgeManifest", "relations": "list[relation]"},
            usefulness_weight=0.9,
        ),
    )
    non_goals = (
        "no network server",
        "no full MCP protocol implementation",
        "no external runtime dependency",
        "no autonomous agent loop",
        "no hidden coupling to quarantined reference or tool bins",
    )
    seam_id = versioned_digest(
        "mcpseam",
        MCP_SEAM_VERSION,
        {
            "capabilities": [capability.to_dict() for capability in capabilities],
            "non_goals": non_goals,
        },
    )
    return McpSeamManifest(
        seam_id=seam_id,
        version=MCP_SEAM_VERSION,
        status="thin_contract_only",
        capabilities=capabilities,
        scoring_dimensions=(
            "task_fit",
            "evidence_quality",
            "actionability",
            "friction_reduction",
            "repeatability",
        ),
        non_goals=non_goals,
    )


def evaluate_mcp_usefulness(
    signals: tuple[McpUsefulnessSignal, ...] | list[McpUsefulnessSignal],
    acceptance_threshold: float = MCP_USEFULNESS_ACCEPTANCE_THRESHOLD,
) -> McpUsefulnessReport:
    """Aggregate usefulness scores for MCP seam tuning."""
    signal_tuple = tuple(signals)
    aggregate = 0.0
    if signal_tuple:
        aggregate = round(sum(signal.score for signal in signal_tuple) / len(signal_tuple), 4)
    threshold = _clamp01(acceptance_threshold)
    report_id = versioned_digest(
        "mcpscore",
        MCP_SEAM_VERSION,
        {
            "signals": [signal.to_dict() for signal in signal_tuple],
            "aggregate_score": aggregate,
            "acceptance_threshold": threshold,
        },
    )
    return McpUsefulnessReport(
        report_id=report_id,
        signals=signal_tuple,
        aggregate_score=aggregate,
        acceptance_threshold=threshold,
    )


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
