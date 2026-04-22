"""Relation enrichment pass for canonical semantic objects."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from src.core.persistence import SemanticCartridge
from src.core.representation import RelationPredicate, SemanticObject, SemanticRelation
from src.core.representation.canonical import versioned_digest

ENRICHMENT_PASS = "phase5_relation_enrichment"
ENRICHMENT_VERSION = "v1"
MARKDOWN_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")


@dataclass(frozen=True)
class RelationEnrichment:
    """One projected relation produced for an existing semantic object."""

    semantic_id: str
    relation: SemanticRelation


@dataclass(frozen=True)
class RelationEnrichmentReport:
    """Traceable result for one enrichment run."""

    enrichments: tuple[RelationEnrichment, ...]
    object_count: int

    @property
    def relation_count(self) -> int:
        return len(self.enrichments)

    def relations_for(self, semantic_id: str) -> tuple[SemanticRelation, ...]:
        return tuple(
            enrichment.relation
            for enrichment in self.enrichments
            if enrichment.semantic_id == semantic_id
        )


def enrich_relations(objects: Iterable[SemanticObject]) -> RelationEnrichmentReport:
    """Produce structural, adjacency, and simple reference relations."""
    ordered_objects = list(objects)
    enrichments: list[RelationEnrichment] = []

    enrichments.extend(_structural_relations(ordered_objects))
    enrichments.extend(_adjacency_relations(ordered_objects))
    enrichments.extend(_reference_relations(ordered_objects))

    return RelationEnrichmentReport(
        enrichments=tuple(_dedupe_enrichments(enrichments)),
        object_count=len(ordered_objects),
    )


def persist_relation_enrichments(
    cartridge: SemanticCartridge,
    report: RelationEnrichmentReport,
) -> None:
    """Persist projected enrichment relations without changing object identity."""
    grouped: dict[str, list[SemanticRelation]] = defaultdict(list)
    for enrichment in report.enrichments:
        grouped[enrichment.semantic_id].append(enrichment.relation)
    for semantic_id, relations in grouped.items():
        cartridge.upsert_relations(semantic_id, relations)


def _structural_relations(objects: list[SemanticObject]) -> list[RelationEnrichment]:
    enrichments: list[RelationEnrichment] = []
    for obj in objects:
        source_ref = _source_ref(obj)
        if not source_ref:
            continue

        enrichments.append(
            RelationEnrichment(
                semantic_id=obj.semantic_id,
                relation=SemanticRelation(
                    predicate=RelationPredicate.MEMBER_OF,
                    target_ref=source_ref,
                    source_ref=source_ref,
                    weight=1.0,
                    confidence=1.0,
                    metadata=_metadata(
                        basis="source_membership",
                        target_kind="source_document",
                        score_components={"source_ref_present": 1.0},
                    ),
                ),
            )
        )

        heading_trail = _heading_trail(obj)
        if heading_trail and obj.kind != "heading":
            enrichments.append(
                RelationEnrichment(
                    semantic_id=obj.semantic_id,
                    relation=SemanticRelation(
                        predicate=RelationPredicate.MEMBER_OF,
                        target_ref=_heading_anchor(source_ref, heading_trail),
                        source_ref=source_ref,
                        weight=0.95,
                        confidence=0.95,
                        metadata=_metadata(
                            basis="heading_trail",
                            target_kind="heading_anchor",
                            heading_trail=list(heading_trail),
                            score_components={"heading_trail_present": 1.0},
                        ),
                    ),
                )
            )
    return enrichments


def _adjacency_relations(objects: list[SemanticObject]) -> list[RelationEnrichment]:
    enrichments: list[RelationEnrichment] = []
    for source_ref, group in _objects_by_source(objects).items():
        sorted_group = sorted(group, key=_block_index)
        for left, right in zip(sorted_group, sorted_group[1:]):
            left_index = _block_index(left)
            right_index = _block_index(right)
            if right_index - left_index != 1:
                continue

            forward_metadata = {
                "basis": "consecutive_block",
                "source_block_index": left_index,
                "target_block_index": right_index,
                "score_components": {"block_distance": 1.0},
            }
            backward_metadata = {
                "basis": "consecutive_block",
                "source_block_index": right_index,
                "target_block_index": left_index,
                "score_components": {"block_distance": 1.0},
            }
            enrichments.append(
                RelationEnrichment(
                    semantic_id=left.semantic_id,
                    relation=SemanticRelation(
                        predicate=RelationPredicate.PRECEDES,
                        target_ref=right.semantic_id,
                        source_ref=source_ref,
                        weight=0.85,
                        confidence=0.9,
                        metadata=_metadata(**forward_metadata),
                    ),
                )
            )
            enrichments.append(
                RelationEnrichment(
                    semantic_id=right.semantic_id,
                    relation=SemanticRelation(
                        predicate=RelationPredicate.FOLLOWS,
                        target_ref=left.semantic_id,
                        source_ref=source_ref,
                        weight=0.85,
                        confidence=0.9,
                        metadata=_metadata(**backward_metadata),
                    ),
                )
            )
    return enrichments


def _reference_relations(objects: list[SemanticObject]) -> list[RelationEnrichment]:
    enrichments: list[RelationEnrichment] = []
    for obj in objects:
        source_ref = _source_ref(obj)
        for match in MARKDOWN_LINK_RE.finditer(obj.content):
            label = match.group(1).strip()
            target = match.group(2).strip()
            if not target:
                continue
            enrichments.append(
                RelationEnrichment(
                    semantic_id=obj.semantic_id,
                    relation=SemanticRelation(
                        predicate=RelationPredicate.REFERENCES,
                        target_ref=target,
                        source_ref=source_ref,
                        weight=0.7,
                        confidence=0.75,
                        metadata=_metadata(
                            basis="markdown_link",
                            label=label,
                            score_components={"explicit_link": 1.0},
                        ),
                    ),
                )
            )
    return enrichments


def _dedupe_enrichments(enrichments: list[RelationEnrichment]) -> list[RelationEnrichment]:
    seen: set[str] = set()
    deduped: list[RelationEnrichment] = []
    for enrichment in enrichments:
        key = versioned_digest(
            "enrich",
            ENRICHMENT_VERSION,
            {
                "semantic_id": enrichment.semantic_id,
                "relation": enrichment.relation.to_dict(),
            },
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(enrichment)
    return deduped


def _objects_by_source(objects: list[SemanticObject]) -> dict[str, list[SemanticObject]]:
    grouped: dict[str, list[SemanticObject]] = defaultdict(list)
    for obj in objects:
        source_ref = _source_ref(obj)
        if source_ref:
            grouped[source_ref].append(obj)
    return grouped


def _source_ref(obj: SemanticObject) -> str | None:
    if obj.occurrence:
        return obj.occurrence.source_ref
    if obj.provenance:
        return obj.provenance[0].source_ref
    return None


def _block_index(obj: SemanticObject) -> int:
    structural = obj.surfaces.structural
    if "block_index" in structural:
        return int(structural["block_index"])
    if obj.occurrence and "block_index" in obj.occurrence.local_context:
        return int(obj.occurrence.local_context["block_index"])
    return 0


def _heading_trail(obj: SemanticObject) -> tuple[str, ...]:
    value = obj.surfaces.structural.get("heading_trail", ())
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _heading_anchor(source_ref: str, heading_trail: tuple[str, ...]) -> str:
    digest = versioned_digest(
        "heading",
        ENRICHMENT_VERSION,
        {"source_ref": source_ref, "heading_trail": list(heading_trail)},
    )
    return f"anchor:{digest}"


def _metadata(**items: object) -> dict[str, object]:
    return {
        "enrichment_pass": ENRICHMENT_PASS,
        "enrichment_version": ENRICHMENT_VERSION,
        **items,
    }
