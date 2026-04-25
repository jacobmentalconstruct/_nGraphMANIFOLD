"""Context projection over separated semantic-prior cartridges."""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation import SemanticObject

from .english_lexicon import default_english_lexicon_cartridge_path
from .project_documents import default_project_document_cartridge_path
from .python_docs_corpus import default_python_docs_cartridge_path

CONTEXT_PROJECTION_VERSION = "v1"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
COMMON_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "does",
    "from",
    "how",
    "is",
    "it",
    "of",
    "or",
    "should",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "why",
    "with",
}
PYTHON_HINTS = {
    "async",
    "await",
    "callable",
    "class",
    "def",
    "false",
    "for",
    "function",
    "generator",
    "import",
    "in",
    "iter",
    "iterable",
    "iterator",
    "lambda",
    "none",
    "object",
    "return",
    "true",
    "yield",
}
PROJECT_HINTS = {
    "bridge",
    "builder",
    "cartridge",
    "contract",
    "context",
    "journal",
    "mcp",
    "meaning",
    "object",
    "park",
    "projection",
    "provenance",
    "rebinding",
    "relation",
    "relations",
    "semantic",
    "tranche",
    "traversal",
}
DEFAULT_CONTEXT_STACK = (
    "english_lexical_prior",
    "python_docs_projection",
    "project_local_docs",
)


@dataclass(frozen=True)
class ContextLayer:
    """One layer available to project a query through."""

    name: str
    role: str
    cartridge_path: str
    object_count: int
    relation_count: int
    is_ready: bool
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "cartridge_path": self.cartridge_path,
            "object_count": self.object_count,
            "relation_count": self.relation_count,
            "is_ready": self.is_ready,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class LayerCandidate:
    """One scored candidate from one projection layer."""

    layer_name: str
    semantic_id: str
    kind: str
    score: float
    matched_terms: tuple[str, ...]
    evidence: tuple[str, ...]
    content_preview: str
    source_ref: str
    heading_trail: tuple[str, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_name": self.layer_name,
            "semantic_id": self.semantic_id,
            "kind": self.kind,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "evidence": list(self.evidence),
            "content_preview": self.content_preview,
            "source_ref": self.source_ref,
            "heading_trail": list(self.heading_trail),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class LayerProjection:
    """Projection result for one context layer."""

    layer: ContextLayer
    layer_score: float
    candidate_count: int
    candidates: tuple[LayerCandidate, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer.to_dict(),
            "layer_score": self.layer_score,
            "candidate_count": self.candidate_count,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class ProjectionFlowObject:
    """One ranked candidate around the selected projection result."""

    role: str
    rank: int
    semantic_id: str
    kind: str
    score: float
    matched_terms: tuple[str, ...]
    evidence: tuple[str, ...]
    content_preview: str
    source_ref: str
    heading_trail: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "rank": self.rank,
            "semantic_id": self.semantic_id,
            "kind": self.kind,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "evidence": list(self.evidence),
            "content_preview": self.content_preview,
            "source_ref": self.source_ref,
            "heading_trail": list(self.heading_trail),
        }


@dataclass(frozen=True)
class ProjectionFlowWindow:
    """Selected projection candidate plus nearby ranked alternatives."""

    layer_name: str
    breadcrumb: tuple[str, ...]
    objects: tuple[ProjectionFlowObject, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_name": self.layer_name,
            "breadcrumb": list(self.breadcrumb),
            "objects": [obj.to_dict() for obj in self.objects],
        }


@dataclass(frozen=True)
class QueryProjectionFrame:
    """Layer-conditioned interpretation frame for a raw query."""

    version: str
    raw_query: str
    terms: tuple[str, ...]
    context_stack: tuple[str, ...]
    selected_layer: str | None
    selected_candidate: LayerCandidate | None
    selected_flow: ProjectionFlowWindow | None
    projections: tuple[LayerProjection, ...]
    caution: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "raw_query": self.raw_query,
            "terms": list(self.terms),
            "context_stack": list(self.context_stack),
            "selected_layer": self.selected_layer,
            "selected_candidate": self.selected_candidate.to_dict() if self.selected_candidate else None,
            "selected_flow": self.selected_flow.to_dict() if self.selected_flow else None,
            "projections": [projection.to_dict() for projection in self.projections],
            "caution": self.caution,
        }


@dataclass(frozen=True)
class ContextProjectionResult:
    """Complete project-query result."""

    version: str
    project_root: str
    frame: QueryProjectionFrame

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "frame": self.frame.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def project_context_query(
    project_root: Path | str,
    query: str,
    *,
    limit: int = 3,
    context_stack: tuple[str, ...] = DEFAULT_CONTEXT_STACK,
) -> ContextProjectionResult:
    """Project a raw query through available context layers."""
    root = Path(project_root).resolve()
    terms = tokenize_query(query)
    if not terms:
        raise ValueError("Context projection query must contain at least one searchable term")

    projections = tuple(
        _project_layer(root, layer_name, query, terms, limit=max(1, limit))
        for layer_name in context_stack
    )
    selected_projection = _select_projection(projections)
    selected_candidate = selected_projection.candidates[0] if selected_projection and selected_projection.candidates else None
    frame = QueryProjectionFrame(
        version=CONTEXT_PROJECTION_VERSION,
        raw_query=query,
        terms=terms,
        context_stack=context_stack,
        selected_layer=selected_projection.layer.name if selected_projection else None,
        selected_candidate=selected_candidate,
        selected_flow=_selected_projection_flow(selected_projection),
        projections=projections,
        caution=(
            "Context projection is a deterministic prototype frame. It shows layer evidence "
            "and scoring, but it is not final semantic grounding or learned disambiguation."
        ),
    )
    return ContextProjectionResult(
        version=CONTEXT_PROJECTION_VERSION,
        project_root=str(root),
        frame=frame,
    )


def tokenize_query(query: str) -> tuple[str, ...]:
    """Return searchable query terms while preserving code-shaped keywords."""
    terms = []
    for token in TOKEN_PATTERN.findall(query):
        normalized = token.lower()
        if len(normalized) < 2:
            continue
        if normalized in COMMON_STOPWORDS and normalized not in PYTHON_HINTS:
            continue
        terms.append(normalized)
    return tuple(dict.fromkeys(terms))


def _project_layer(
    root: Path,
    layer_name: str,
    query: str,
    terms: tuple[str, ...],
    *,
    limit: int,
) -> LayerProjection:
    layer = _layer_for(root, layer_name)
    if not layer.is_ready:
        return LayerProjection(
            layer=layer,
            layer_score=0.0,
            candidate_count=0,
            candidates=(),
            notes=("layer cartridge is not ready",),
        )
    objects = _candidate_objects(Path(layer.cartridge_path), terms)
    candidates = tuple(
        candidate
        for candidate in (_score_object(layer.name, obj, query, terms) for obj in objects)
        if candidate.score > 0
    )
    ranked = tuple(sorted(candidates, key=_candidate_sort_key)[:limit])
    layer_score = _layer_score(layer.name, ranked, terms)
    notes = _layer_notes(layer.name, ranked, terms)
    return LayerProjection(
        layer=layer,
        layer_score=layer_score,
        candidate_count=len(candidates),
        candidates=ranked,
        notes=notes,
    )


def _layer_for(root: Path, layer_name: str) -> ContextLayer:
    if layer_name == "english_lexical_prior":
        path = default_english_lexicon_cartridge_path(root)
        role = "base English lexical anchor"
    elif layer_name == "python_docs_projection":
        path = default_python_docs_cartridge_path(root)
        role = "Python language and code-structure prior"
    elif layer_name == "project_local_docs":
        path = default_project_document_cartridge_path(root)
        role = "nGraphMANIFOLD local doctrine prior"
    else:
        path = root / "data" / "cartridges" / f"{layer_name}.sqlite3"
        role = "custom context layer"

    if not path.exists():
        return ContextLayer(
            name=layer_name,
            role=role,
            cartridge_path=str(path),
            object_count=0,
            relation_count=0,
            is_ready=False,
            notes=("missing cartridge",),
        )
    try:
        manifest = SemanticCartridge(path, cartridge_id=DEFAULT_CARTRIDGE_ID).manifest()
    except Exception as exc:
        return ContextLayer(
            name=layer_name,
            role=role,
            cartridge_path=str(path),
            object_count=0,
            relation_count=0,
            is_ready=False,
            notes=(f"manifest read failed: {exc}",),
        )
    return ContextLayer(
        name=layer_name,
        role=role,
        cartridge_path=str(path),
        object_count=manifest.object_count,
        relation_count=manifest.relation_count,
        is_ready=manifest.is_ready,
        notes=(),
    )


def _candidate_objects(db_path: Path, terms: tuple[str, ...], max_rows: int = 2500) -> tuple[SemanticObject, ...]:
    clauses = []
    params: list[str | int] = []
    for term in terms:
        escaped = _escape_like(term)
        clauses.append("LOWER(content) LIKE ? ESCAPE '\\'")
        params.append(f"%{escaped}%")
    if not clauses:
        return ()
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"""
            SELECT object_json
            FROM semantic_objects
            WHERE {" OR ".join(clauses)}
            LIMIT ?
            """,
            (*params, max_rows),
        ).fetchall()
    finally:
        conn.close()
    return tuple(SemanticObject.from_dict(json.loads(row["object_json"])) for row in rows)


def _score_object(layer_name: str, obj: SemanticObject, query: str, terms: tuple[str, ...]) -> LayerCandidate:
    content = obj.content
    normalized_content = content.lower()
    normalized_query = query.strip().lower()
    matched_terms = tuple(term for term in terms if term in normalized_content)
    evidence: list[str] = []
    score = 0.0

    if normalized_query and normalized_query in normalized_content:
        score += 8.0
        evidence.append("exact_phrase")
    if matched_terms:
        coverage = len(matched_terms) / max(1, len(terms))
        score += round(coverage * 5.0, 4)
        score += min(sum(normalized_content.count(term) for term in matched_terms), 6) * 0.35
        evidence.append(f"term_coverage:{len(matched_terms)}/{len(terms)}")
    if len(matched_terms) == len(terms):
        score += 4.0
        evidence.append("all_terms")
    ordered_score = _ordered_term_score(normalized_content, terms)
    if ordered_score:
        score += ordered_score
        evidence.append("ordered_terms")

    metadata = obj.metadata
    heading_trail = _heading_trail(obj)
    source_ref = obj.occurrence.source_ref if obj.occurrence else ""

    if layer_name == "english_lexical_prior":
        score += _english_score(obj, normalized_query, terms, matched_terms, evidence)
    elif layer_name == "python_docs_projection":
        score += _python_score(obj, terms, matched_terms, evidence)
    elif layer_name == "project_local_docs":
        score += _project_score(obj, terms, heading_trail, source_ref, evidence)

    return LayerCandidate(
        layer_name=layer_name,
        semantic_id=obj.semantic_id,
        kind=obj.kind,
        score=round(max(score, 0.0), 4),
        matched_terms=matched_terms,
        evidence=tuple(evidence),
        content_preview=_preview(content),
        source_ref=source_ref,
        heading_trail=heading_trail,
        metadata=_candidate_metadata(obj, metadata),
    )


def _english_score(
    obj: SemanticObject,
    normalized_query: str,
    terms: tuple[str, ...],
    matched_terms: tuple[str, ...],
    evidence: list[str],
) -> float:
    score = 0.0
    headword = str(obj.metadata.get("normalized_headword") or obj.metadata.get("headword") or "").lower()
    if headword and (headword == normalized_query or headword in terms):
        score += 10.0
        evidence.append("headword_match")
        if headword in PROJECT_HINTS or headword in PYTHON_HINTS:
            score -= 7.0
            evidence.append("headword_suppressed_by_frame_hint")
    if len(terms) > 1 and len(matched_terms) == 1 and headword in matched_terms:
        score -= 1.5
        evidence.append("single_headword_for_multi_term_query")
    if len(PYTHON_HINTS.intersection(terms)) >= 2:
        score -= 2.5
        evidence.append("python_hint_penalty")
    if len(PROJECT_HINTS.intersection(terms)) >= 2:
        score -= 1.5
        evidence.append("project_hint_penalty")
    token_count = int(obj.surfaces.statistical.get("definition_token_count", 0))
    if token_count > 80 and not headword:
        score -= 1.0
        evidence.append("broad_definition_penalty")
    return score


def _python_score(
    obj: SemanticObject,
    terms: tuple[str, ...],
    matched_terms: tuple[str, ...],
    evidence: list[str],
) -> float:
    score = 0.0
    symbol = str(obj.metadata.get("symbol") or obj.surfaces.grammatical.get("symbol") or "").lower()
    if symbol and any(term in symbol for term in terms):
        score += 7.0
        evidence.append("python_symbol_match")
    if obj.kind == "python_api_signature":
        score += 2.5
        evidence.append("api_signature")
    elif obj.kind in {"python_code_example", "python_doctest_example"}:
        score += 3.0
        evidence.append("python_example")
    elif obj.kind == "python_grammar_rule":
        score += 1.5
        evidence.append("python_grammar")

    ast_data = obj.surfaces.grammatical.get("ast")
    if isinstance(ast_data, dict):
        ast_terms = {
            str(item).lower()
            for key in ("defined_names", "referenced_names", "call_names", "control_flow", "top_level_forms")
            for item in ast_data.get(key, ())
        }
        if ast_terms.intersection(terms):
            score += 4.0
            evidence.append("ast_feature_match")
    python_hint_count = len(PYTHON_HINTS.intersection(terms))
    if python_hint_count >= 2:
        score += min(8.0, python_hint_count * 1.75)
        evidence.append("python_context_fit")
    if len(PROJECT_HINTS.intersection(terms)) >= 3 and len(matched_terms) <= 1:
        score -= 2.0
        evidence.append("project_query_penalty")
    return score


def _project_score(
    obj: SemanticObject,
    terms: tuple[str, ...],
    heading_trail: tuple[str, ...],
    source_ref: str,
    evidence: list[str],
) -> float:
    score = 0.0
    heading_text = " ".join(heading_trail).lower()
    source_text = source_ref.lower()
    if heading_text and any(term in heading_text for term in terms):
        score += 3.0
        evidence.append("heading_context_match")
    if source_text and any(term in source_text for term in terms):
        score += 0.75
        evidence.append("source_context_match")
    project_hint_count = len(PROJECT_HINTS.intersection(terms))
    if project_hint_count >= 2:
        score += min(8.0, project_hint_count * 1.75)
        evidence.append("project_context_fit")
    if len(PYTHON_HINTS.intersection(terms)) >= 3 and project_hint_count < 2:
        score -= 2.0
        evidence.append("python_query_penalty")
    return score


def _layer_score(layer_name: str, candidates: tuple[LayerCandidate, ...], terms: tuple[str, ...]) -> float:
    if not candidates:
        return 0.0
    matched = {term for candidate in candidates for term in candidate.matched_terms}
    coverage_score = (len(matched) / max(1, len(terms))) * 5.0
    score = candidates[0].score + coverage_score
    python_hints = len(PYTHON_HINTS.intersection(terms))
    project_hints = len(PROJECT_HINTS.intersection(terms))
    if layer_name == "english_lexical_prior":
        if python_hints >= 2:
            score -= 4.0
        if project_hints >= 2:
            score -= 3.0
        if len(terms) == 1 and not (python_hints or project_hints):
            score += 2.0
        elif len(terms) == 1:
            score += 0.5
    elif layer_name == "python_docs_projection":
        ambiguous_terms = PYTHON_HINTS & PROJECT_HINTS & set(terms)
        pure_python_hints = python_hints - len(ambiguous_terms)
        if pure_python_hints >= 2:
            score += 6.0
        elif pure_python_hints >= 1:
            score += 3.0
        elif python_hints >= 1:
            score += 1.0
        if project_hints >= 3:
            score -= 2.0
    elif layer_name == "project_local_docs":
        if project_hints >= 2:
            score += 6.0
        elif project_hints >= 1:
            score += 6.0 if len(terms) <= 2 else 3.0
        if python_hints >= 3 and project_hints < 2:
            score -= 2.0
    return round(max(score, 0.0), 4)


def _layer_notes(layer_name: str, candidates: tuple[LayerCandidate, ...], terms: tuple[str, ...]) -> tuple[str, ...]:
    notes: list[str] = []
    if not candidates:
        notes.append("no candidates matched this layer")
    if layer_name == "english_lexical_prior":
        notes.append("base lexical prior; useful for headword anchoring, not final truth")
    elif layer_name == "python_docs_projection":
        notes.append("Python/code prior; useful for API, syntax, doctest, and AST-shaped evidence")
    elif layer_name == "project_local_docs":
        notes.append("project-local prior; useful for nGraphMANIFOLD doctrine and current status")
    matched = sorted({term for candidate in candidates for term in candidate.matched_terms})
    if matched:
        notes.append(f"matched_terms:{','.join(matched)}")
    missing = [term for term in terms if term not in matched]
    if missing:
        notes.append(f"unmatched_terms:{','.join(missing)}")
    return tuple(notes)


def _select_projection(projections: tuple[LayerProjection, ...]) -> LayerProjection | None:
    ready = [projection for projection in projections if projection.layer_score > 0 and projection.candidates]
    if not ready:
        return None
    return sorted(ready, key=lambda projection: (-projection.layer_score, projection.layer.name))[0]


def _selected_projection_flow(projection: LayerProjection | None) -> ProjectionFlowWindow | None:
    if projection is None or not projection.candidates:
        return None
    objects: list[ProjectionFlowObject] = []
    for index, candidate in enumerate(projection.candidates[:3], start=1):
        role = "selected" if index == 1 else "alternative"
        objects.append(
            ProjectionFlowObject(
                role=role,
                rank=index,
                semantic_id=candidate.semantic_id,
                kind=candidate.kind,
                score=candidate.score,
                matched_terms=candidate.matched_terms,
                evidence=candidate.evidence,
                content_preview=candidate.content_preview,
                source_ref=candidate.source_ref,
                heading_trail=candidate.heading_trail,
            )
        )
    selected = projection.candidates[0]
    breadcrumb = tuple(
        item
        for item in (
            projection.layer.name,
            *selected.heading_trail,
            f"rank {1}",
        )
        if item
    )
    return ProjectionFlowWindow(
        layer_name=projection.layer.name,
        breadcrumb=breadcrumb,
        objects=tuple(objects),
    )


def _candidate_sort_key(candidate: LayerCandidate) -> tuple[float, str, str]:
    return (-candidate.score, candidate.source_ref, candidate.semantic_id)


def _ordered_term_score(content: str, terms: tuple[str, ...]) -> float:
    position = -1
    matched = 0
    for term in terms:
        found = content.find(term, position + 1)
        if found < 0:
            continue
        matched += 1
        position = found
    if matched < 2:
        return 0.0
    return min(3.0, matched * 0.75)


def _heading_trail(obj: SemanticObject) -> tuple[str, ...]:
    context = obj.occurrence.local_context if obj.occurrence else {}
    trail = context.get("heading_trail") or obj.surfaces.structural.get("heading_trail") or ()
    return tuple(str(item) for item in trail)


def _candidate_metadata(obj: SemanticObject, metadata: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "corpus",
        "headword",
        "normalized_headword",
        "symbol",
        "source_relpath",
        "line_start",
        "line_end",
    )
    compact = {key: metadata[key] for key in keys if key in metadata}
    compact["semantic_id_version"] = obj.identity.version
    return compact


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _preview(content: str, limit: int = 220) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."
