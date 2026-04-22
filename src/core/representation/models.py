"""Canonical semantic object model for nGraphMANIFOLD."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .canonical import canonical_json, normalize_for_identity, versioned_digest

IDENTITY_VERSION = "v1"


class TransformStatus(str, Enum):
    """Declared semantic integrity status for a transformation."""

    IDENTITY_PRESERVING = "identity-preserving"
    REVERSIBLY_MAPPABLE = "reversibly-mappable"
    BOUNDED_LOSS = "bounded-loss"
    INTERPRETIVE = "interpretive"


class RelationPredicate(str, Enum):
    """Prototype relation predicates owned by the representation layer."""

    CONTAINS = "contains"
    MEMBER_OF = "member_of"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    REFERENCES = "references"
    DERIVES_FROM = "derives_from"
    TRANSFORMS_TO = "transforms_to"
    SIMILAR_TO = "similar_to"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXECUTES_AS = "executes_as"


@dataclass(frozen=True)
class SourceSpan:
    """Source-local span for one semantic occurrence."""

    start: int | None = None
    end: int | None = None
    unit: str = "char"

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "unit": self.unit}

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SourceSpan":
        if not data:
            return cls()
        return cls(start=data.get("start"), end=data.get("end"), unit=data.get("unit", "char"))


@dataclass(frozen=True)
class SemanticSurfaceSet:
    """Named semantic surfaces for a canonical object."""

    verbatim: dict[str, Any] = field(default_factory=dict)
    structural: dict[str, Any] = field(default_factory=dict)
    grammatical: dict[str, Any] = field(default_factory=dict)
    statistical: dict[str, Any] = field(default_factory=dict)
    semantic: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return {
            "verbatim": normalize_for_identity(self.verbatim),
            "structural": normalize_for_identity(self.structural),
            "grammatical": normalize_for_identity(self.grammatical),
            "statistical": normalize_for_identity(self.statistical),
            "semantic": normalize_for_identity(self.semantic),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SemanticSurfaceSet":
        data = data or {}
        return cls(
            verbatim=dict(data.get("verbatim", {})),
            structural=dict(data.get("structural", {})),
            grammatical=dict(data.get("grammatical", {})),
            statistical=dict(data.get("statistical", {})),
            semantic=dict(data.get("semantic", {})),
        )


@dataclass(frozen=True)
class SemanticIdentity:
    """Stable semantic identity separate from source occurrence."""

    semantic_id: str
    version: str = IDENTITY_VERSION

    @classmethod
    def from_envelope(cls, envelope: dict[str, Any]) -> "SemanticIdentity":
        return cls(
            semantic_id=versioned_digest("sem", IDENTITY_VERSION, envelope),
            version=IDENTITY_VERSION,
        )

    def to_dict(self) -> dict[str, str]:
        return {"semantic_id": self.semantic_id, "version": self.version}


@dataclass(frozen=True)
class SemanticOccurrence:
    """One source occurrence of a semantic object."""

    occurrence_id: str
    semantic_id: str
    source_ref: str
    source_span: SourceSpan = field(default_factory=SourceSpan)
    local_context: dict[str, Any] = field(default_factory=dict)
    version: str = IDENTITY_VERSION

    @classmethod
    def create(
        cls,
        *,
        semantic_id: str,
        source_ref: str,
        source_span: SourceSpan | None = None,
        local_context: dict[str, Any] | None = None,
    ) -> "SemanticOccurrence":
        span = source_span or SourceSpan()
        context = local_context or {}
        envelope = {
            "semantic_id": semantic_id,
            "source_ref": source_ref,
            "source_span": span.to_dict(),
            "local_context": context,
        }
        return cls(
            occurrence_id=versioned_digest("occ", IDENTITY_VERSION, envelope),
            semantic_id=semantic_id,
            source_ref=source_ref,
            source_span=span,
            local_context=context,
            version=IDENTITY_VERSION,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "occurrence_id": self.occurrence_id,
            "semantic_id": self.semantic_id,
            "source_ref": self.source_ref,
            "source_span": self.source_span.to_dict(),
            "local_context": normalize_for_identity(self.local_context),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticOccurrence":
        return cls(
            occurrence_id=data["occurrence_id"],
            semantic_id=data["semantic_id"],
            source_ref=data["source_ref"],
            source_span=SourceSpan.from_dict(data.get("source_span")),
            local_context=dict(data.get("local_context", {})),
            version=data.get("version", IDENTITY_VERSION),
        )


@dataclass(frozen=True)
class SemanticRelation:
    """Explicit typed relation between semantic references."""

    predicate: RelationPredicate
    target_ref: str
    source_ref: str | None = None
    weight: float = 1.0
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "predicate": self.predicate.value,
            "target_ref": self.target_ref,
            "source_ref": self.source_ref,
            "weight": self.weight,
            "confidence": self.confidence,
        }

    def to_dict(self) -> dict[str, Any]:
        data = self.summary()
        data["metadata"] = normalize_for_identity(self.metadata)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticRelation":
        return cls(
            predicate=RelationPredicate(data["predicate"]),
            target_ref=data["target_ref"],
            source_ref=data.get("source_ref"),
            weight=float(data.get("weight", 1.0)),
            confidence=float(data.get("confidence", 1.0)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class ProvenanceRecord:
    """Derivation and source lineage for a semantic object."""

    source_ref: str
    transform_status: TransformStatus
    agent: str = "nGraphMANIFOLD"
    method: str = "original"
    derived_from: tuple[str, ...] = ()
    confidence: float = 1.0
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_ref": self.source_ref,
            "transform_status": self.transform_status.value,
            "agent": self.agent,
            "method": self.method,
            "derived_from": list(self.derived_from),
            "confidence": self.confidence,
            "notes": self.notes,
            "metadata": normalize_for_identity(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProvenanceRecord":
        return cls(
            source_ref=data["source_ref"],
            transform_status=TransformStatus(data["transform_status"]),
            agent=data.get("agent", "nGraphMANIFOLD"),
            method=data.get("method", "original"),
            derived_from=tuple(data.get("derived_from", ())),
            confidence=float(data.get("confidence", 1.0)),
            notes=data.get("notes", ""),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class SemanticObject:
    """Project-owned canonical semantic object."""

    identity: SemanticIdentity
    kind: str
    content: str
    surfaces: SemanticSurfaceSet = field(default_factory=SemanticSurfaceSet)
    relations: tuple[SemanticRelation, ...] = ()
    provenance: tuple[ProvenanceRecord, ...] = ()
    occurrence: SemanticOccurrence | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        kind: str,
        content: str,
        surfaces: SemanticSurfaceSet | None = None,
        relations: tuple[SemanticRelation, ...] | list[SemanticRelation] = (),
        provenance: tuple[ProvenanceRecord, ...] | list[ProvenanceRecord] = (),
        source_ref: str | None = None,
        source_span: SourceSpan | None = None,
        local_context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "SemanticObject":
        surface_set = surfaces or SemanticSurfaceSet(verbatim={"content": content})
        relation_tuple = tuple(relations)
        provenance_tuple = tuple(provenance)
        object_metadata = metadata or {}
        envelope = cls.identity_envelope(
            kind=kind,
            content=content,
            surfaces=surface_set,
            relations=relation_tuple,
            metadata=object_metadata,
        )
        identity = SemanticIdentity.from_envelope(envelope)
        occurrence = None
        if source_ref is not None:
            occurrence = SemanticOccurrence.create(
                semantic_id=identity.semantic_id,
                source_ref=source_ref,
                source_span=source_span,
                local_context=local_context,
            )
        return cls(
            identity=identity,
            kind=kind,
            content=content,
            surfaces=surface_set,
            relations=relation_tuple,
            provenance=provenance_tuple,
            occurrence=occurrence,
            metadata=object_metadata,
        )

    @staticmethod
    def identity_envelope(
        *,
        kind: str,
        content: str,
        surfaces: SemanticSurfaceSet,
        relations: tuple[SemanticRelation, ...],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Return the fields that define semantic identity."""
        return {
            "kind": kind,
            "content": content,
            "surfaces": surfaces.to_dict(),
            "relations": [relation.summary() for relation in relations],
            "metadata": normalize_for_identity(metadata),
        }

    @property
    def semantic_id(self) -> str:
        return self.identity.semantic_id

    @property
    def occurrence_id(self) -> str | None:
        return self.occurrence.occurrence_id if self.occurrence else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "kind": self.kind,
            "content": self.content,
            "surfaces": self.surfaces.to_dict(),
            "relations": [relation.to_dict() for relation in self.relations],
            "provenance": [record.to_dict() for record in self.provenance],
            "occurrence": self.occurrence.to_dict() if self.occurrence else None,
            "metadata": normalize_for_identity(self.metadata),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticObject":
        occurrence_data = data.get("occurrence")
        return cls(
            identity=SemanticIdentity(**data["identity"]),
            kind=data["kind"],
            content=data["content"],
            surfaces=SemanticSurfaceSet.from_dict(data.get("surfaces")),
            relations=tuple(SemanticRelation.from_dict(item) for item in data.get("relations", [])),
            provenance=tuple(ProvenanceRecord.from_dict(item) for item in data.get("provenance", [])),
            occurrence=SemanticOccurrence.from_dict(occurrence_data) if occurrence_data else None,
            metadata=dict(data.get("metadata", {})),
        )
