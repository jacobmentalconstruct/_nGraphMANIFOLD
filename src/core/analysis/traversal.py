"""Traceable traversal over persisted semantic cartridge relations."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from src.core.persistence import CartridgeReadiness, SemanticCartridge
from src.core.representation.canonical import versioned_digest

TRAVERSAL_VERSION = "v1"
TRAVERSAL_METHOD = "phase6_cartridge_relation_walk"
DEFAULT_MAX_DEPTH = 2
DEFAULT_MAX_STEPS = 64


@dataclass(frozen=True)
class TraversalStep:
    """One relation considered during a cartridge traversal."""

    step_index: int
    direction: str
    depth: int
    source_semantic_id: str
    target_ref: str
    reached_semantic_id: str | None
    predicate: str
    score: float
    cumulative_score: float
    relation_weight: float
    relation_confidence: float
    relation_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "direction": self.direction,
            "depth": self.depth,
            "source_semantic_id": self.source_semantic_id,
            "target_ref": self.target_ref,
            "reached_semantic_id": self.reached_semantic_id,
            "predicate": self.predicate,
            "score": self.score,
            "cumulative_score": self.cumulative_score,
            "relation_weight": self.relation_weight,
            "relation_confidence": self.relation_confidence,
            "relation_metadata": self.relation_metadata,
        }


@dataclass(frozen=True)
class TraversalReport:
    """Inspectable traversal artifact for a seed semantic object."""

    artifact_id: str
    seed_semantic_id: str
    method: str
    max_depth: int
    max_steps: int
    readiness: CartridgeReadiness
    blockers: tuple[str, ...]
    visited_semantic_ids: tuple[str, ...]
    steps: tuple[TraversalStep, ...]

    @property
    def is_ready(self) -> bool:
        return not self.blockers

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "seed_semantic_id": self.seed_semantic_id,
            "method": self.method,
            "max_depth": self.max_depth,
            "max_steps": self.max_steps,
            "readiness": {
                "is_ready": self.readiness.is_ready,
                "object_count": self.readiness.object_count,
                "occurrence_count": self.readiness.occurrence_count,
                "relation_count": self.readiness.relation_count,
                "provenance_count": self.readiness.provenance_count,
                "blockers": list(self.readiness.blockers),
            },
            "blockers": list(self.blockers),
            "visited_semantic_ids": list(self.visited_semantic_ids),
            "steps": [step.to_dict() for step in self.steps],
        }


def traverse_cartridge(
    cartridge: SemanticCartridge,
    seed_semantic_id: str,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_steps: int = DEFAULT_MAX_STEPS,
    include_incoming: bool = True,
) -> TraversalReport:
    """Walk relation projections from a seed semantic object."""
    bounded_depth = max(0, max_depth)
    bounded_steps = max(0, max_steps)
    readiness = cartridge.readiness()
    blockers = list(readiness.blockers)

    if readiness.relation_count < 1:
        blockers.append("no semantic relations stored")
    if cartridge.get_object(seed_semantic_id) is None:
        blockers.append("seed semantic object not found")
    if bounded_steps < 1:
        blockers.append("max_steps must be at least 1")

    if blockers:
        return _report(
            seed_semantic_id=seed_semantic_id,
            max_depth=bounded_depth,
            max_steps=bounded_steps,
            readiness=readiness,
            blockers=tuple(blockers),
            visited_semantic_ids=(),
            steps=(),
        )

    visited: set[str] = {seed_semantic_id}
    visit_order: list[str] = [seed_semantic_id]
    steps: list[TraversalStep] = []
    queue: deque[tuple[str, int, float]] = deque([(seed_semantic_id, 0, 1.0)])

    while queue and len(steps) < bounded_steps:
        current_id, depth, cumulative = queue.popleft()
        if depth >= bounded_depth:
            continue

        for candidate in _relation_candidates(cartridge, current_id, include_incoming):
            if len(steps) >= bounded_steps:
                break

            relation = candidate["relation"]
            reached_id = candidate["reached_semantic_id"]
            score = _relation_score(relation, depth + 1)
            next_cumulative = round(cumulative * score, 6)
            step = TraversalStep(
                step_index=len(steps),
                direction=candidate["direction"],
                depth=depth + 1,
                source_semantic_id=candidate["source_semantic_id"],
                target_ref=relation["target_ref"],
                reached_semantic_id=reached_id,
                predicate=relation["predicate"],
                score=score,
                cumulative_score=next_cumulative,
                relation_weight=float(relation.get("weight", 1.0)),
                relation_confidence=float(relation.get("confidence", 1.0)),
                relation_metadata=dict(relation.get("metadata", {})),
            )
            steps.append(step)

            if reached_id and reached_id not in visited:
                visited.add(reached_id)
                visit_order.append(reached_id)
                queue.append((reached_id, depth + 1, next_cumulative))

    return _report(
        seed_semantic_id=seed_semantic_id,
        max_depth=bounded_depth,
        max_steps=bounded_steps,
        readiness=readiness,
        blockers=(),
        visited_semantic_ids=tuple(visit_order),
        steps=tuple(steps),
    )


def _relation_candidates(
    cartridge: SemanticCartridge,
    semantic_id: str,
    include_incoming: bool,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for relation in cartridge.relations_for(semantic_id):
        target_id = relation["target_ref"] if cartridge.get_object(relation["target_ref"]) else None
        candidates.append(
            {
                "direction": "outgoing",
                "source_semantic_id": semantic_id,
                "reached_semantic_id": target_id,
                "relation": relation,
            }
        )

    if include_incoming:
        for row in cartridge.relations_targeting(semantic_id):
            source_id = row["semantic_id"]
            relation = row["relation"]
            if source_id == semantic_id:
                continue
            candidates.append(
                {
                    "direction": "incoming",
                    "source_semantic_id": source_id,
                    "reached_semantic_id": source_id if cartridge.get_object(source_id) else None,
                    "relation": relation,
                }
            )

    return sorted(
        candidates,
        key=lambda item: (
            item["direction"],
            item["relation"]["predicate"],
            item["source_semantic_id"],
            item["relation"]["target_ref"],
        ),
    )


def _relation_score(relation: dict[str, Any], depth: int) -> float:
    depth_discount = 1.0 / max(1, depth)
    score = float(relation.get("weight", 1.0)) * float(relation.get("confidence", 1.0)) * depth_discount
    return round(score, 6)


def _report(
    *,
    seed_semantic_id: str,
    max_depth: int,
    max_steps: int,
    readiness: CartridgeReadiness,
    blockers: tuple[str, ...],
    visited_semantic_ids: tuple[str, ...],
    steps: tuple[TraversalStep, ...],
) -> TraversalReport:
    artifact_id = versioned_digest(
        "trav",
        TRAVERSAL_VERSION,
        {
            "seed_semantic_id": seed_semantic_id,
            "method": TRAVERSAL_METHOD,
            "max_depth": max_depth,
            "max_steps": max_steps,
            "blockers": blockers,
            "visited_semantic_ids": visited_semantic_ids,
            "steps": [step.to_dict() for step in steps],
        },
    )
    return TraversalReport(
        artifact_id=artifact_id,
        seed_semantic_id=seed_semantic_id,
        method=TRAVERSAL_METHOD,
        max_depth=max_depth,
        max_steps=max_steps,
        readiness=readiness,
        blockers=blockers,
        visited_semantic_ids=visited_semantic_ids,
        steps=steps,
    )
