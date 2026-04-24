"""Real builder-task scoring over ingested project documents."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.persistence import SemanticCartridge

from .mcp_inspection_history import McpInspectionHistoryStore
from .mcp_seam import McpUsefulnessReport, McpUsefulnessSignal, evaluate_mcp_usefulness
from .project_documents import ingest_project_documents_for_traversal

REAL_BUILDER_TASK_SCORING_VERSION = "v1"
DEFAULT_BUILDER_TASK_DOCUMENT_PROFILE = "expanded"


@dataclass(frozen=True)
class RealBuilderTaskFixture:
    """One real builder continuation question to score against project docs."""

    task_id: str
    question: str
    seed_text_hint: str
    expected_source_suffix: str

    def to_dict(self) -> dict[str, str]:
        return {
            "task_id": self.task_id,
            "question": self.question,
            "seed_text_hint": self.seed_text_hint,
            "expected_source_suffix": self.expected_source_suffix,
        }


@dataclass(frozen=True)
class RealBuilderTaskScore:
    """Usefulness score for one real builder task."""

    fixture: RealBuilderTaskFixture
    signal: McpUsefulnessSignal
    seed_semantic_id: str
    seed_source_ref: str
    traversal_step_count: int
    blocker_count: int
    call_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture": self.fixture.to_dict(),
            "signal": self.signal.to_dict(),
            "seed_semantic_id": self.seed_semantic_id,
            "seed_source_ref": self.seed_source_ref,
            "traversal_step_count": self.traversal_step_count,
            "blocker_count": self.blocker_count,
            "call_id": self.call_id,
        }


@dataclass(frozen=True)
class RealBuilderTaskScoringRun:
    """Aggregate real-doc builder-task scoring run."""

    version: str
    project_root: str
    history_path: str
    document_profile: str
    document_paths: tuple[str, ...]
    scores: tuple[RealBuilderTaskScore, ...]
    usefulness_report: McpUsefulnessReport

    @property
    def meets_acceptance(self) -> bool:
        return self.usefulness_report.meets_acceptance

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "history_path": self.history_path,
            "document_profile": self.document_profile,
            "document_paths": list(self.document_paths),
            "scores": [score.to_dict() for score in self.scores],
            "usefulness_report": self.usefulness_report.to_dict(),
            "meets_acceptance": self.meets_acceptance,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_real_builder_tasks() -> tuple[RealBuilderTaskFixture, ...]:
    """Return real builder tasks for continuation and usefulness scoring."""
    return (
        RealBuilderTaskFixture(
            task_id="current_tranche_lookup",
            question="What is the current parked tranche and next implementation target?",
            seed_text_hint="Current Park Point",
            expected_source_suffix="PROJECT_STATUS.md",
        ),
        RealBuilderTaskFixture(
            task_id="mcp_surface_lookup",
            question="What MCP-facing surface exists now?",
            seed_text_hint="Tool Registration Candidate",
            expected_source_suffix="MCP_SEAM.md",
        ),
        RealBuilderTaskFixture(
            task_id="strangler_next_work_lookup",
            question="What does the plan say should happen next?",
            seed_text_hint="Immediate Post-Prototype Work",
            expected_source_suffix="STRANGLER_PLAN.md",
        ),
        RealBuilderTaskFixture(
            task_id="operator_command_lookup",
            question="Which command shows persisted MCP inspection history?",
            seed_text_hint="mcp-history",
            expected_source_suffix="README.md",
        ),
    )


def default_builder_task_score_path(project_root: Path | str) -> Path:
    """Return the project-owned score artifact path."""
    return Path(project_root) / "data" / "mcp_inspection" / "builder_task_scores.json"


def run_real_builder_task_scoring(
    project_root: Path | str,
    *,
    history_path: Path | str,
    score_path: Path | str | None = None,
    document_profile: str = DEFAULT_BUILDER_TASK_DOCUMENT_PROFILE,
    document_relpaths: tuple[str, ...] | None = None,
    fixtures: tuple[RealBuilderTaskFixture, ...] = default_real_builder_tasks(),
) -> RealBuilderTaskScoringRun:
    """Score registered traversal usefulness against real project-doc tasks."""
    root = Path(project_root).resolve()
    history = McpInspectionHistoryStore(history_path)
    scores: list[RealBuilderTaskScore] = []
    resolved_document_paths: tuple[str, ...] = ()

    for fixture in fixtures:
        ingestion = ingest_project_documents_for_traversal(
            root,
            document_profile=document_profile,
            document_relpaths=document_relpaths,
            seed_text_hint=fixture.seed_text_hint,
            seed_question=fixture.question,
            seed_task_id=fixture.task_id,
            expected_source_suffix=fixture.expected_source_suffix,
        )
        if not resolved_document_paths:
            resolved_document_paths = tuple(ingestion.document_paths)
        call = ingestion.tool_call.to_dict()
        history.record_call(call)
        traversal = call["capture"]["response"]["traversal_report"]
        seed_object = SemanticCartridge(ingestion.cartridge_path).get_object(ingestion.seed_semantic_id)
        seed_content = seed_object.content if seed_object else ""
        signal = _score_task(
            fixture=fixture,
            seed_source_ref=ingestion.seed_source_ref,
            seed_content=seed_content,
            traversal_step_count=len(traversal["steps"]),
            blocker_count=len(traversal["blockers"]),
        )
        scores.append(
            RealBuilderTaskScore(
                fixture=fixture,
                signal=signal,
                seed_semantic_id=ingestion.seed_semantic_id,
                seed_source_ref=ingestion.seed_source_ref,
                traversal_step_count=len(traversal["steps"]),
                blocker_count=len(traversal["blockers"]),
                call_id=call["call_id"],
            )
        )

    report = evaluate_mcp_usefulness(tuple(score.signal for score in scores))
    run = RealBuilderTaskScoringRun(
        version=REAL_BUILDER_TASK_SCORING_VERSION,
        project_root=str(root),
        history_path=str(history_path),
        document_profile=document_profile if document_relpaths is None else "custom",
        document_paths=resolved_document_paths,
        scores=tuple(scores),
        usefulness_report=report,
    )
    if score_path is not None:
        output_path = Path(score_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(run.to_json(), encoding="utf-8")
    return run


def _score_task(
    *,
    fixture: RealBuilderTaskFixture,
    seed_source_ref: str,
    seed_content: str,
    traversal_step_count: int,
    blocker_count: int,
) -> McpUsefulnessSignal:
    source_match = seed_source_ref.endswith(fixture.expected_source_suffix)
    content_match = fixture.seed_text_hint in seed_content
    no_blockers = blocker_count == 0
    has_steps = traversal_step_count > 0
    evidence = min(1.0, traversal_step_count / 3.0)
    task_fit = 1.0 if source_match and content_match else 0.5 if source_match else 0.25
    return McpUsefulnessSignal(
        capability_name=f"builder_task.{fixture.task_id}",
        task_fit=task_fit,
        evidence_quality=evidence,
        actionability=0.85 if no_blockers and source_match and content_match else 0.4,
        friction_reduction=0.8 if has_steps and no_blockers else 0.2,
        repeatability=1.0,
        notes=(
            f"seed_source={seed_source_ref}; steps={traversal_step_count}; "
            f"blockers={blocker_count}"
        ),
    )
