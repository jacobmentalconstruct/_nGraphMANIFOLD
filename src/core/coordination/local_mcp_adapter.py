"""Local adapter pilot for MCP-shaped traversal inspection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.analysis import enrich_relations, persist_relation_enrichments, traverse_cartridge
from src.core.persistence import SemanticCartridge
from src.core.representation.canonical import versioned_digest
from src.core.transformation import SourceDocument, semantic_objects_from_source

from .mcp_seam import (
    McpCapabilityDescriptor,
    McpSeamManifest,
    McpUsefulnessReport,
    McpUsefulnessSignal,
    build_mcp_seam_manifest,
    evaluate_mcp_usefulness,
)

LOCAL_MCP_ADAPTER_VERSION = "v1"
TRAVERSAL_CAPABILITY_NAME = "analysis.traverse_cartridge"


@dataclass(frozen=True)
class LocalMcpInspectionCapture:
    """Raw payload captured around one local MCP-shaped adapter call."""

    capture_id: str
    captured_at: str
    capability: dict[str, Any]
    seam_manifest: dict[str, Any]
    request: dict[str, Any]
    response: dict[str, Any]
    usefulness_report: dict[str, Any]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "capture_id": self.capture_id,
            "captured_at": self.captured_at,
            "capability": self.capability,
            "seam_manifest": self.seam_manifest,
            "request": self.request,
            "response": self.response,
            "usefulness_report": self.usefulness_report,
            "notes": list(self.notes),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def run_traversal_mcp_adapter(
    cartridge: SemanticCartridge,
    seed_semantic_id: str,
    *,
    max_depth: int = 2,
    max_steps: int = 64,
    include_incoming: bool = True,
) -> LocalMcpInspectionCapture:
    """Run the local traversal adapter and capture the raw MCP-shaped payload."""
    seam_manifest = build_mcp_seam_manifest()
    capability = _capability_descriptor(seam_manifest, TRAVERSAL_CAPABILITY_NAME)
    request = {
        "cartridge": {
            "db_path": str(cartridge.db_path),
            "cartridge_id": cartridge.cartridge_id,
        },
        "seed_semantic_id": seed_semantic_id,
        "max_depth": max_depth,
        "max_steps": max_steps,
        "include_incoming": include_incoming,
    }
    traversal_report = traverse_cartridge(
        cartridge,
        seed_semantic_id,
        max_depth=max_depth,
        max_steps=max_steps,
        include_incoming=include_incoming,
    )
    response = {
        "traversal_report": traversal_report.to_dict(),
    }
    usefulness_report = evaluate_mcp_usefulness(
        (
            _traversal_usefulness_signal(
                traversal_step_count=traversal_report.step_count,
                blocker_count=len(traversal_report.blockers),
            ),
        )
    )
    captured_at = _utc_now()
    capture_basis = {
        "captured_at": captured_at,
        "capability_name": capability.name,
        "request": request,
        "response": response,
        "usefulness_report": usefulness_report.to_dict(),
    }
    capture_id = versioned_digest("mcpinspect", LOCAL_MCP_ADAPTER_VERSION, capture_basis)
    return LocalMcpInspectionCapture(
        capture_id=capture_id,
        captured_at=captured_at,
        capability=capability.to_dict(),
        seam_manifest=seam_manifest.to_dict(),
        request=request,
        response=response,
        usefulness_report=usefulness_report.to_dict(),
        notes=(
            "local adapter pilot only",
            "raw capture intended for builder inspection",
        ),
    )


def build_default_traversal_inspection(db_path: Path | str) -> LocalMcpInspectionCapture:
    """Create a small fixture cartridge and capture a traversal adapter call."""
    document = SourceDocument(
        source_ref="fixture://mcp-inspector",
        content=(
            "# MCP Inspector\n\n"
            "Expose the traversal payload as raw visible data.\n\n"
            "Use [contract](contract://builder) as the governing constraint."
        ),
    )
    cartridge = SemanticCartridge(db_path)
    objects = semantic_objects_from_source(document)
    for obj in objects:
        cartridge.upsert_object(obj)
    enrichment_report = enrich_relations(objects)
    persist_relation_enrichments(cartridge, enrichment_report)
    seed = _seed_object_id(objects, block_index=1)
    return run_traversal_mcp_adapter(
        cartridge,
        seed,
        max_depth=2,
        max_steps=64,
        include_incoming=True,
    )


def _capability_descriptor(
    seam_manifest: McpSeamManifest,
    capability_name: str,
) -> McpCapabilityDescriptor:
    for capability in seam_manifest.capabilities:
        if capability.name == capability_name:
            return capability
    raise ValueError(f"Capability not found in seam manifest: {capability_name}")


def _seed_object_id(objects: list[Any], block_index: int) -> str:
    for obj in objects:
        if int(obj.surfaces.structural.get("block_index", -1)) == block_index:
            return obj.semantic_id
    if not objects:
        raise ValueError("Inspection fixture produced no semantic objects")
    return objects[0].semantic_id


def _traversal_usefulness_signal(
    *,
    traversal_step_count: int,
    blocker_count: int,
) -> McpUsefulnessSignal:
    has_steps = traversal_step_count > 0
    no_blockers = blocker_count == 0
    evidence_score = min(1.0, traversal_step_count / 3.0)
    return McpUsefulnessSignal(
        capability_name=TRAVERSAL_CAPABILITY_NAME,
        task_fit=1.0 if no_blockers else 0.25,
        evidence_quality=evidence_score,
        actionability=0.85 if has_steps and no_blockers else 0.2,
        friction_reduction=0.8 if has_steps and no_blockers else 0.2,
        repeatability=1.0,
        notes=f"walked {traversal_step_count} traversal steps with {blocker_count} blockers",
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
