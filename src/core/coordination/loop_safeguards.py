"""Loop-safeguard review for controlled post-prototype expansion."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.config import AppSettings
from src.core.engine import ApplicationEngine

from .context_projection import ContextProjectionResult, project_context_query
from .context_projection_scoring import default_context_projection_score_path
from .host_bridge import (
    build_host_bridge_runtime_snapshot,
    build_host_bridge_timeout_policy_manifest,
)
from .interaction_spine import interaction_truth_policy
from .mcp_inspection_history import default_mcp_inspection_history_path
from .project_documents import (
    ingest_project_documents,
    resolve_project_document_profile,
    summarize_project_document_profiles,
)
from .builder_task_scoring import default_builder_task_score_path

LOOP_SAFEGUARDS_VERSION = "v1"
LOOP_REVIEW_STATUS_READY = "ready_for_controlled_expansion_review"
LOOP_REVIEW_STATUS_CAUTION = "caution_review_required"
LOOP_REVIEW_STATUS_BLOCKED = "blocked"


@dataclass(frozen=True)
class LoopEvidence:
    """One semantic-substrate evidence anchor used by the loop review."""

    evidence_id: str
    query: str
    selected_layer: str | None
    selected_source_ref: str
    selected_heading_trail: tuple[str, ...]
    selected_preview: str
    matched_terms: tuple[str, ...]
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "query": self.query,
            "selected_layer": self.selected_layer,
            "selected_source_ref": self.selected_source_ref,
            "selected_heading_trail": list(self.selected_heading_trail),
            "selected_preview": self.selected_preview,
            "matched_terms": list(self.matched_terms),
            "score": self.score,
        }


@dataclass(frozen=True)
class LoopSafeguardCheck:
    """One review gate for keeping the collaboration loop bounded."""

    check_id: str
    title: str
    status: str
    owner_surface: str
    rationale: str
    evidence_ids: tuple[str, ...]
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "status": self.status,
            "owner_surface": self.owner_surface,
            "rationale": self.rationale,
            "evidence_ids": list(self.evidence_ids),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class LoopSafeguardsReview:
    """Inspectable review result for the next-tranche collaboration loop."""

    version: str
    project_root: str
    active_tranche: str
    next_tranche: str
    document_profile: str
    document_paths: tuple[str, ...]
    status: str
    checks: tuple[LoopSafeguardCheck, ...]
    evidence: tuple[LoopEvidence, ...]
    runtime_state: dict[str, Any]
    expansion_gate: dict[str, Any]
    non_goals: tuple[str, ...]
    recommendations: tuple[str, ...]

    @property
    def meets_review_gate(self) -> bool:
        return self.status != LOOP_REVIEW_STATUS_BLOCKED

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "active_tranche": self.active_tranche,
            "next_tranche": self.next_tranche,
            "document_profile": self.document_profile,
            "document_paths": list(self.document_paths),
            "status": self.status,
            "meets_review_gate": self.meets_review_gate,
            "checks": [check.to_dict() for check in self.checks],
            "evidence": [item.to_dict() for item in self.evidence],
            "runtime_state": self.runtime_state,
            "expansion_gate": self.expansion_gate,
            "non_goals": list(self.non_goals),
            "recommendations": list(self.recommendations),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def build_loop_safeguards_review(
    project_root: Path | str,
    *,
    document_profile: str = "core",
) -> LoopSafeguardsReview:
    """Build an inspectable loop-safeguards review from project docs and runtime policy."""

    root = Path(project_root).resolve()
    profile_name, document_paths = resolve_project_document_profile(document_profile)
    corpus = ingest_project_documents(root, document_profile=profile_name)
    settings = AppSettings(
        project_root=root,
        docs_root=root / "_docs",
        data_root=root / "data",
    )
    engine_status = ApplicationEngine(settings).status()
    evidence = tuple(_collect_evidence(root))
    evidence_by_id = {item.evidence_id: item for item in evidence}
    runtime_state = _runtime_state(root)
    checks = (
        _anchor_check(engine_status.next_tranche, evidence_by_id),
        _semantic_evidence_check(corpus.to_dict(), evidence_by_id),
        _bridge_profile_check(runtime_state),
        _truth_boundary_check(runtime_state),
        _score_clarity_check(runtime_state),
        _visibility_ownership_check(evidence_by_id),
    )
    status = _review_status(checks)
    return LoopSafeguardsReview(
        version=LOOP_SAFEGUARDS_VERSION,
        project_root=str(root),
        active_tranche=engine_status.active_tranche,
        next_tranche=engine_status.next_tranche,
        document_profile=profile_name,
        document_paths=tuple(document_paths),
        status=status,
        checks=checks,
        evidence=evidence,
        runtime_state=runtime_state,
        expansion_gate=_expansion_gate(status),
        non_goals=_non_goals(),
        recommendations=_recommendations(status),
    )


def _collect_evidence(root: Path) -> tuple[LoopEvidence, ...]:
    queries = (
        (
            "next_tranche_anchor",
            "loop safeguards controlled expansion bridge profile policy next tranche",
        ),
        (
            "surface_ownership_anchor",
            "host workspace stream cockpit history surface ownership visibility",
        ),
        (
            "truth_boundary_anchor",
            "interaction truth boundary inspection only semantic cartridge truth",
        ),
    )
    evidence: list[LoopEvidence] = []
    for evidence_id, query in queries:
        try:
            projection = project_context_query(root, query, limit=3)
        except ValueError:
            continue
        evidence.append(_evidence_from_projection(evidence_id, projection))
    return tuple(evidence)


def _evidence_from_projection(
    evidence_id: str,
    projection: ContextProjectionResult,
) -> LoopEvidence:
    frame = projection.frame
    selected = frame.selected_candidate
    if selected is None:
        return LoopEvidence(
            evidence_id=evidence_id,
            query=frame.raw_query,
            selected_layer=frame.selected_layer,
            selected_source_ref="",
            selected_heading_trail=(),
            selected_preview="",
            matched_terms=(),
            score=0.0,
        )
    return LoopEvidence(
        evidence_id=evidence_id,
        query=frame.raw_query,
        selected_layer=frame.selected_layer,
        selected_source_ref=selected.source_ref,
        selected_heading_trail=selected.heading_trail,
        selected_preview=selected.content_preview,
        matched_terms=selected.matched_terms,
        score=selected.score,
    )


def _runtime_state(root: Path) -> dict[str, Any]:
    builder_score = _read_json(default_builder_task_score_path(root))
    projection_score = _read_json(default_context_projection_score_path(root))
    return {
        "history_path": str(default_mcp_inspection_history_path(root)),
        "bridge_timeout_policy": build_host_bridge_timeout_policy_manifest(),
        "bridge_runtime": build_host_bridge_runtime_snapshot(root),
        "interaction_truth_policy": interaction_truth_policy(),
        "project_doc_profiles": summarize_project_document_profiles(),
        "score_artifacts": {
            "builder": _score_artifact_summary(builder_score),
            "projection": _score_artifact_summary(projection_score),
        },
    }


def _anchor_check(
    next_tranche: str,
    evidence: dict[str, LoopEvidence],
) -> LoopSafeguardCheck:
    anchor = evidence.get("next_tranche_anchor")
    blockers: list[str] = []
    warnings: list[str] = []
    if anchor is None:
        blockers.append("No semantic evidence was collected for the next-tranche anchor.")
    elif anchor.selected_layer != "project_local_docs":
        blockers.append("Next-tranche query did not resolve through project-local docs.")
    elif "PROJECT_STATUS.md" not in anchor.selected_source_ref and "TODO.md" not in anchor.selected_source_ref:
        warnings.append("Next-tranche evidence did not come from PROJECT_STATUS.md or TODO.md.")
    if "Loop Safeguards" not in next_tranche:
        blockers.append("Runtime next_tranche does not name Loop Safeguards.")
    return LoopSafeguardCheck(
        check_id="current_anchor_resolution",
        title="Current Anchor Resolution",
        status=_check_status(blockers, warnings),
        owner_surface="PROJECT_STATUS.md + project_local_docs cartridge",
        rationale="The next tranche must resolve from declared project memory before expansion work starts.",
        evidence_ids=("next_tranche_anchor",),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _semantic_evidence_check(
    corpus: dict[str, Any],
    evidence: dict[str, LoopEvidence],
) -> LoopSafeguardCheck:
    blockers: list[str] = []
    warnings: list[str] = []
    if int(corpus.get("object_count", 0)) <= 0:
        blockers.append("Project-document cartridge has no semantic objects.")
    if int(corpus.get("relation_count", 0)) <= 0:
        warnings.append("Project-document cartridge has no relation evidence.")
    anchor = evidence.get("next_tranche_anchor")
    if anchor and len(anchor.matched_terms) < 3:
        warnings.append("Next-tranche anchor matched too few query terms.")
    return LoopSafeguardCheck(
        check_id="semantic_evidence_before_action",
        title="Semantic Evidence Before Action",
        status=_check_status(blockers, warnings),
        owner_surface="project_documents.sqlite3 + project-query",
        rationale="The app may assist tranche mapping, but only through visible evidence anchors.",
        evidence_ids=("next_tranche_anchor",),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _bridge_profile_check(runtime_state: dict[str, Any]) -> LoopSafeguardCheck:
    policy = runtime_state.get("bridge_timeout_policy", {})
    profiles = runtime_state.get("project_doc_profiles", {})
    blockers: list[str] = []
    warnings: list[str] = []
    if policy.get("transport_kind") != "file_backed_local":
        blockers.append("Bridge transport is no longer file_backed_local.")
    if set(profiles.keys()) != {"core", "expanded"}:
        blockers.append("Project-doc profile set is no longer exactly core/expanded.")
    runtime = runtime_state.get("bridge_runtime", {})
    if runtime.get("pending_request_count", 0) or runtime.get("pending_response_count", 0):
        warnings.append(
            "Bridge transport has pending files; run mcp-bridge-maintenance or observe retention cleanup."
        )
    return LoopSafeguardCheck(
        check_id="bridge_and_profile_discipline",
        title="Bridge And Profile Discipline",
        status=_check_status(blockers, warnings),
        owner_surface="status bridge/profile manifest",
        rationale="The prior tranche parked file-backed bridge transport and the core/expanded profile split.",
        evidence_ids=(),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _truth_boundary_check(runtime_state: dict[str, Any]) -> LoopSafeguardCheck:
    policy = runtime_state.get("interaction_truth_policy", {})
    blockers: list[str] = []
    if policy.get("persist_to_semantic_cartridges") is not False:
        blockers.append("Interaction projections are allowed to persist into semantic cartridges.")
    if policy.get("persistence_policy") != "inspection_only":
        blockers.append("Interaction persistence policy is not inspection_only.")
    return LoopSafeguardCheck(
        check_id="truth_surface_boundary",
        title="Truth Surface Boundary",
        status=_check_status(blockers, []),
        owner_surface="interaction_truth_policy",
        rationale="Loop review must not turn operational evidence into cartridge truth by accident.",
        evidence_ids=("truth_boundary_anchor",),
        blockers=tuple(blockers),
    )


def _score_clarity_check(runtime_state: dict[str, Any]) -> LoopSafeguardCheck:
    artifacts = runtime_state.get("score_artifacts", {})
    blockers: list[str] = []
    warnings: list[str] = []
    for name in ("builder", "projection"):
        artifact = artifacts.get(name) or {}
        if not artifact.get("present"):
            warnings.append(f"{name} score artifact is not present yet.")
        elif not artifact.get("meets_acceptance"):
            blockers.append(f"{name} score artifact does not meet acceptance.")
    return LoopSafeguardCheck(
        check_id="score_clarity",
        title="Score Clarity",
        status=_check_status(blockers, warnings),
        owner_surface="builder/projection score artifacts",
        rationale="Expansion should preserve accepted score artifacts and expose runtime cost when available.",
        evidence_ids=(),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _visibility_ownership_check(evidence: dict[str, LoopEvidence]) -> LoopSafeguardCheck:
    anchor = evidence.get("surface_ownership_anchor")
    blockers: list[str] = []
    warnings: list[str] = []
    if anchor is None:
        warnings.append("No semantic evidence was collected for surface ownership.")
    elif anchor.selected_layer != "project_local_docs":
        warnings.append("Surface ownership evidence did not resolve through project-local docs.")
    elif "MCP_SEAM.md" not in anchor.selected_source_ref and "PROJECT_STATUS.md" not in anchor.selected_source_ref:
        warnings.append("Surface ownership evidence came from an unexpected document.")
    return LoopSafeguardCheck(
        check_id="visibility_surface_ownership",
        title="Visibility Surface Ownership",
        status=_check_status(blockers, warnings),
        owner_surface="MCP_SEAM.md + host workspace panels",
        rationale="Host, stream, cockpit, and history surfaces should keep distinct jobs as the loop expands.",
        evidence_ids=("surface_ownership_anchor",),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _review_status(checks: tuple[LoopSafeguardCheck, ...]) -> str:
    if any(check.status == "block" for check in checks):
        return LOOP_REVIEW_STATUS_BLOCKED
    if any(check.status == "warn" for check in checks):
        return LOOP_REVIEW_STATUS_CAUTION
    return LOOP_REVIEW_STATUS_READY


def _check_status(blockers: list[str], warnings: list[str]) -> str:
    if blockers:
        return "block"
    if warnings:
        return "warn"
    return "pass"


def _expansion_gate(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "required_before_expansion": [
            "next tranche anchor resolves through project-local evidence",
            "bridge transport remains file-backed unless new measured need appears",
            "project-doc profiles remain core/expanded only",
            "interaction projections remain inspection-only",
            "builder and projection scores remain accepted or warnings are explicit",
            "visibility surfaces keep distinct ownership",
        ],
        "allowed_next_action": (
            "choose one controlled expansion candidate with tests and score visibility"
            if status != LOOP_REVIEW_STATUS_BLOCKED
            else "resolve blocking loop-discipline failures before expansion"
        ),
    }


def _non_goals() -> tuple[str, ...]:
    return (
        "no embeddings",
        "no repo-wide ingestion by default",
        "no real network MCP server",
        "no FastAPI or websocket transport",
        "no cartridge merge",
        "no broad dashboard rewrite",
        "no hidden interaction persistence",
    )


def _recommendations(status: str) -> tuple[str, ...]:
    if status == LOOP_REVIEW_STATUS_BLOCKED:
        return (
            "Resolve blocked loop-safeguard checks before adding new runtime behavior.",
            "Re-run loop-review after status, truth, bridge, or score artifacts are corrected.",
        )
    return (
        "Use loop-review as the first gate before selecting any controlled expansion slice.",
        "Use mcp-bridge-maintenance when loop-review reports pending bridge transport files.",
        "Prefer one expansion candidate that can be observed through existing stream/cockpit/history surfaces.",
        "Keep the semantic substrate as evidence for tranche mapping, not as silent autonomous planning.",
    )


def _score_artifact_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {"present": False}
    report = payload.get("usefulness_report") if isinstance(payload.get("usefulness_report"), dict) else {}
    return {
        "present": True,
        "meets_acceptance": bool(payload.get("meets_acceptance")),
        "aggregate_score": report.get("aggregate_score"),
        "document_profile": payload.get("document_profile"),
        "elapsed_ms": payload.get("elapsed_ms"),
        "corpus_object_count": payload.get("corpus_object_count"),
        "corpus_relation_count": payload.get("corpus_relation_count"),
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
