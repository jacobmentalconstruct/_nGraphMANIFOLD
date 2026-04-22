"""Shared command/result spine for UI, CLI, and MCP-shaped actions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.representation import (
    ProvenanceRecord,
    RelationPredicate,
    SemanticObject,
    SemanticRelation,
    SemanticSurfaceSet,
    TransformStatus,
)
from src.core.representation.canonical import canonical_json, versioned_digest

from .mcp_seam import (
    McpCapabilityDescriptor,
    McpUsefulnessReport,
    McpUsefulnessSignal,
    build_mcp_seam_manifest,
    evaluate_mcp_usefulness,
)

INTERACTION_SPINE_VERSION = "v1"
PROJECT_QUERY_CAPABILITY_NAME = "coordination.project_context_query"
PROJECT_QUERY_TOOL_NAME = "ngraph.project.query"
DEFAULT_CONTEXT_STACK = (
    "english_lexical_prior",
    "python_docs_projection",
    "project_local_docs",
)


@dataclass(frozen=True)
class CommandEnvelope:
    """Canonical invocation envelope shared by UI, CLI, and MCP surfaces."""

    command_id: str
    version: str
    actor: str
    source_surface: str
    tool_name: str
    payload: dict[str, Any]
    correlation_id: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "version": self.version,
            "actor": self.actor,
            "source_surface": self.source_surface,
            "tool_name": self.tool_name,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class ToolResultEnvelope:
    """Canonical result envelope for one command execution."""

    result_id: str
    version: str
    command_id: str
    tool_name: str
    status: str
    result_payload: dict[str, Any]
    evidence_summary: dict[str, Any]
    usefulness_score: float
    completed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "version": self.version,
            "command_id": self.command_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "result_payload": self.result_payload,
            "evidence_summary": self.evidence_summary,
            "usefulness_score": self.usefulness_score,
            "completed_at": self.completed_at,
        }


@dataclass(frozen=True)
class InteractionCapture:
    """Inspectable capture joining command, result, capability, and raw response."""

    capture_id: str
    captured_at: str
    capability: dict[str, Any]
    command: CommandEnvelope
    result: ToolResultEnvelope
    response: dict[str, Any]
    usefulness_report: dict[str, Any]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "capture_id": self.capture_id,
            "captured_at": self.captured_at,
            "capability": self.capability,
            "command": self.command.to_dict(),
            "result": self.result.to_dict(),
            "response": self.response,
            "usefulness_report": self.usefulness_report,
            "notes": list(self.notes),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def create_command_envelope(
    *,
    tool_name: str,
    payload: dict[str, Any],
    actor: str = "human",
    source_surface: str = "cli",
    correlation_id: str | None = None,
    created_at: str | None = None,
) -> CommandEnvelope:
    """Create a deterministic command envelope when timestamp/id are supplied."""
    timestamp = created_at or _utc_now()
    normalized_payload = json.loads(canonical_json(payload))
    corr_id = correlation_id or versioned_digest(
        "cmdcorr",
        INTERACTION_SPINE_VERSION,
        {
            "actor": actor,
            "source_surface": source_surface,
            "tool_name": tool_name,
            "payload": normalized_payload,
        },
    )
    command_basis = {
        "version": INTERACTION_SPINE_VERSION,
        "actor": actor,
        "source_surface": source_surface,
        "tool_name": tool_name,
        "payload": normalized_payload,
        "correlation_id": corr_id,
        "created_at": timestamp,
    }
    return CommandEnvelope(
        command_id=versioned_digest("command", INTERACTION_SPINE_VERSION, command_basis),
        version=INTERACTION_SPINE_VERSION,
        actor=actor,
        source_surface=source_surface,
        tool_name=tool_name,
        payload=normalized_payload,
        correlation_id=corr_id,
        created_at=timestamp,
    )


def run_project_query_interaction(
    project_root: Path | str,
    query: str,
    *,
    limit: int = 3,
    context_stack: tuple[str, ...] = DEFAULT_CONTEXT_STACK,
    actor: str = "human",
    source_surface: str = "cli",
    created_at: str | None = None,
) -> InteractionCapture:
    """Run project-query through the shared command/result spine."""
    from .context_projection import project_context_query

    command = create_command_envelope(
        tool_name=PROJECT_QUERY_TOOL_NAME,
        actor=actor,
        source_surface=source_surface,
        created_at=created_at,
        payload={
            "query": query,
            "limit": int(limit),
            "context_stack": list(context_stack),
        },
    )
    projection = project_context_query(
        project_root,
        query,
        limit=limit,
        context_stack=context_stack,
    )
    response = {
        "projection_frame": projection.frame.to_dict(),
        "project_root": projection.project_root,
        "version": projection.version,
    }
    evidence_summary = _projection_evidence_summary(response["projection_frame"])
    usefulness_report = evaluate_mcp_usefulness(
        (_project_query_usefulness_signal(evidence_summary),)
    )
    result = _create_result_envelope(
        command=command,
        status="ok",
        result_payload=response,
        evidence_summary=evidence_summary,
        usefulness_report=usefulness_report,
    )
    captured_at = result.completed_at
    capability = _project_query_capability().to_dict()
    capture_basis = {
        "captured_at": captured_at,
        "capability": capability,
        "command": command.to_dict(),
        "result": result.to_dict(),
        "response": response,
        "usefulness_report": usefulness_report.to_dict(),
    }
    return InteractionCapture(
        capture_id=versioned_digest("interaction", INTERACTION_SPINE_VERSION, capture_basis),
        captured_at=captured_at,
        capability=capability,
        command=command,
        result=result,
        response=response,
        usefulness_report=usefulness_report.to_dict(),
        notes=(
            "shared command spine pilot",
            "history-first persistence only",
            "semantic object projection adapters are available but not persisted",
        ),
    )


def command_envelope_to_semantic_object(command: CommandEnvelope) -> SemanticObject:
    """Project a command envelope into a SemanticObject without persisting it."""
    command_dict = command.to_dict()
    source_ref = f"interaction-command://{command.command_id}"
    surfaces = SemanticSurfaceSet(
        verbatim={"command_json": command_dict},
        structural={
            "actor": command.actor,
            "source_surface": command.source_surface,
            "tool_name": command.tool_name,
            "correlation_id": command.correlation_id,
            "created_at": command.created_at,
        },
        grammatical={
            "schema": "CommandEnvelope",
            "schema_version": command.version,
            "action_type": command.tool_name,
            "payload_keys": sorted(command.payload.keys()),
        },
        statistical={
            "payload_key_count": len(command.payload),
            "payload_json_length": len(canonical_json(command.payload)),
        },
        semantic={
            "invoked_tool": command.tool_name,
            "intent_payload": command.payload,
        },
    )
    provenance = ProvenanceRecord(
        source_ref=source_ref,
        transform_status=TransformStatus.REVERSIBLY_MAPPABLE,
        method="command_envelope_semantic_projection",
        confidence=1.0,
        metadata={"command_id": command.command_id},
    )
    relations = (
        SemanticRelation(
            predicate=RelationPredicate.EXECUTES_AS,
            target_ref=command.tool_name,
            source_ref=source_ref,
            metadata={"basis": "command_tool_name"},
        ),
    )
    return SemanticObject.create(
        kind="interaction_command",
        content=f"{command.tool_name} command from {command.source_surface}",
        surfaces=surfaces,
        relations=relations,
        provenance=(provenance,),
        source_ref=source_ref,
        local_context={"correlation_id": command.correlation_id},
        metadata={"interaction_spine_version": INTERACTION_SPINE_VERSION},
    )


def tool_result_envelope_to_semantic_object(result: ToolResultEnvelope) -> SemanticObject:
    """Project a tool result envelope into a SemanticObject without persisting it."""
    result_dict = result.to_dict()
    source_ref = f"interaction-result://{result.result_id}"
    selected_layer = result.evidence_summary.get("selected_layer", "")
    surfaces = SemanticSurfaceSet(
        verbatim={"result_json": result_dict},
        structural={
            "command_id": result.command_id,
            "tool_name": result.tool_name,
            "status": result.status,
            "completed_at": result.completed_at,
        },
        grammatical={
            "schema": "ToolResultEnvelope",
            "schema_version": result.version,
            "result_type": result.tool_name,
            "payload_keys": sorted(result.result_payload.keys()),
        },
        statistical={
            "usefulness_score": result.usefulness_score,
            "candidate_count": result.evidence_summary.get("candidate_count", 0),
            "projection_count": result.evidence_summary.get("projection_count", 0),
        },
        semantic={
            "selected_layer": selected_layer,
            "selected_candidate_kind": result.evidence_summary.get("selected_candidate_kind", ""),
            "matched_terms": result.evidence_summary.get("matched_terms", []),
            "evidence": result.evidence_summary.get("evidence", []),
        },
    )
    provenance = ProvenanceRecord(
        source_ref=source_ref,
        transform_status=TransformStatus.REVERSIBLY_MAPPABLE,
        method="tool_result_envelope_semantic_projection",
        derived_from=(result.command_id,),
        confidence=1.0,
        metadata={"result_id": result.result_id},
    )
    relations = (
        SemanticRelation(
            predicate=RelationPredicate.DERIVES_FROM,
            target_ref=result.command_id,
            source_ref=source_ref,
            metadata={"basis": "result_command_id"},
        ),
    )
    return SemanticObject.create(
        kind="interaction_result",
        content=f"{result.tool_name} result status={result.status} selected_layer={selected_layer}",
        surfaces=surfaces,
        relations=relations,
        provenance=(provenance,),
        source_ref=source_ref,
        local_context={"command_id": result.command_id},
        metadata={"interaction_spine_version": INTERACTION_SPINE_VERSION},
    )


def _create_result_envelope(
    *,
    command: CommandEnvelope,
    status: str,
    result_payload: dict[str, Any],
    evidence_summary: dict[str, Any],
    usefulness_report: McpUsefulnessReport,
) -> ToolResultEnvelope:
    completed_at = _utc_now()
    result_basis = {
        "version": INTERACTION_SPINE_VERSION,
        "command_id": command.command_id,
        "tool_name": command.tool_name,
        "status": status,
        "result_payload": result_payload,
        "evidence_summary": evidence_summary,
        "usefulness_score": usefulness_report.aggregate_score,
        "completed_at": completed_at,
    }
    return ToolResultEnvelope(
        result_id=versioned_digest("toolresult", INTERACTION_SPINE_VERSION, result_basis),
        version=INTERACTION_SPINE_VERSION,
        command_id=command.command_id,
        tool_name=command.tool_name,
        status=status,
        result_payload=result_payload,
        evidence_summary=evidence_summary,
        usefulness_score=usefulness_report.aggregate_score,
        completed_at=completed_at,
    )


def _projection_evidence_summary(frame: dict[str, Any]) -> dict[str, Any]:
    selected = frame.get("selected_candidate") or {}
    projections = frame.get("projections", [])
    return {
        "selected_layer": frame.get("selected_layer"),
        "selected_candidate_id": selected.get("semantic_id", ""),
        "selected_candidate_kind": selected.get("kind", ""),
        "selected_candidate_score": selected.get("score", 0.0),
        "matched_terms": selected.get("matched_terms", []),
        "evidence": selected.get("evidence", []),
        "projection_count": len(projections),
        "candidate_count": sum(int(item.get("candidate_count", 0)) for item in projections),
        "terms": frame.get("terms", []),
        "context_stack": frame.get("context_stack", []),
    }


def _project_query_usefulness_signal(evidence_summary: dict[str, Any]) -> McpUsefulnessSignal:
    selected = bool(evidence_summary.get("selected_layer"))
    has_evidence = bool(evidence_summary.get("evidence"))
    candidate_count = int(evidence_summary.get("candidate_count", 0))
    projection_count = int(evidence_summary.get("projection_count", 0))
    return McpUsefulnessSignal(
        capability_name=PROJECT_QUERY_CAPABILITY_NAME,
        task_fit=1.0 if selected else 0.25,
        evidence_quality=1.0 if has_evidence and projection_count >= 3 else 0.5,
        actionability=0.9 if selected else 0.2,
        friction_reduction=0.85 if candidate_count > 0 else 0.2,
        repeatability=1.0,
        notes=(
            f"selected_layer={evidence_summary.get('selected_layer')} "
            f"candidates={candidate_count}"
        ),
    )


def _project_query_capability() -> McpCapabilityDescriptor:
    manifest = build_mcp_seam_manifest()
    for capability in manifest.capabilities:
        if capability.name == PROJECT_QUERY_CAPABILITY_NAME:
            return capability
    raise ValueError(f"Capability not found in seam manifest: {PROJECT_QUERY_CAPABILITY_NAME}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
