"""Build the project-owned Python documentation projection cartridge."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.analysis import enrich_relations, persist_relation_enrichments
from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation import (
    ProvenanceRecord,
    RelationPredicate,
    SemanticObject,
    SemanticRelation,
    SemanticSurfaceSet,
    SourceSpan,
    TransformStatus,
)
from src.core.representation.canonical import versioned_digest
from src.core.transformation import PythonDocsRecord, extract_python_docs_file, iter_python_docs_records

PYTHON_DOCS_CORPUS_VERSION = "v1"
DEFAULT_PYTHON_DOCS_SOURCE_RELPATH = "assets/_corpus_examples/python-3.11.15-docs-text"
DEFAULT_PYTHON_DOCS_CARTRIDGE_NAME = "python_docs.sqlite3"
DEFAULT_PYTHON_DOCS_DOCUMENTS = (
    "library/functions.txt",
    "reference/compound_stmts.txt",
    "reference/simple_stmts.txt",
    "tutorial/controlflow.txt",
)


@dataclass(frozen=True)
class PythonDocsCorpusBuildResult:
    """Summary of a Python documentation projection cartridge build."""

    version: str
    project_root: str
    source_path: str
    cartridge_path: str
    cartridge_id: str
    document_paths: tuple[str, ...]
    limit: int | None
    reset: bool
    include_prose: bool
    records_seen: int
    objects_written: int
    object_count: int
    relation_count: int
    provenance_count: int
    ast_parseable_count: int
    ast_failed_count: int
    signature_count: int
    code_example_count: int
    doctest_example_count: int
    grammar_rule_count: int
    sample_records: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_root": self.project_root,
            "source_path": self.source_path,
            "cartridge_path": self.cartridge_path,
            "cartridge_id": self.cartridge_id,
            "document_paths": list(self.document_paths),
            "limit": self.limit,
            "reset": self.reset,
            "include_prose": self.include_prose,
            "records_seen": self.records_seen,
            "objects_written": self.objects_written,
            "object_count": self.object_count,
            "relation_count": self.relation_count,
            "provenance_count": self.provenance_count,
            "ast_parseable_count": self.ast_parseable_count,
            "ast_failed_count": self.ast_failed_count,
            "signature_count": self.signature_count,
            "code_example_count": self.code_example_count,
            "doctest_example_count": self.doctest_example_count,
            "grammar_rule_count": self.grammar_rule_count,
            "sample_records": list(self.sample_records),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def default_python_docs_source_path(project_root: Path | str) -> Path:
    """Return the project-owned official Python docs text corpus path."""
    return Path(project_root) / DEFAULT_PYTHON_DOCS_SOURCE_RELPATH


def default_python_docs_cartridge_path(project_root: Path | str) -> Path:
    """Return the project-owned Python docs projection cartridge path."""
    return Path(project_root) / "data" / "cartridges" / DEFAULT_PYTHON_DOCS_CARTRIDGE_NAME


def build_python_docs_corpus(
    project_root: Path | str,
    *,
    source_path: Path | str | None = None,
    cartridge_path: Path | str | None = None,
    limit: int | None = None,
    reset: bool = False,
    include_prose: bool = False,
    document_relpaths: tuple[str, ...] | None = DEFAULT_PYTHON_DOCS_DOCUMENTS,
) -> PythonDocsCorpusBuildResult:
    """Extract official Python docs records into a dedicated projection cartridge."""
    root = Path(project_root).resolve()
    source = Path(source_path).resolve() if source_path else default_python_docs_source_path(root).resolve()
    db_path = Path(cartridge_path).resolve() if cartridge_path else default_python_docs_cartridge_path(root).resolve()
    _ensure_project_owned(root, source)
    _ensure_project_owned(root, db_path)
    if not source.exists():
        raise FileNotFoundError(f"Python docs source path does not exist: {source}")
    if reset and db_path.exists():
        db_path.unlink()

    records = _load_records(source, limit=limit, include_prose=include_prose, document_relpaths=document_relpaths)
    objects = [python_docs_record_to_semantic_object(record, index) for index, record in enumerate(records)]
    cartridge = SemanticCartridge(db_path, cartridge_id=DEFAULT_CARTRIDGE_ID)
    objects_written = cartridge.upsert_objects(objects)
    enrichment_report = enrich_relations(objects)
    persist_relation_enrichments(cartridge, enrichment_report)
    manifest = cartridge.manifest()

    ast_records = [record for record in records if record.ast_summary is not None]
    return PythonDocsCorpusBuildResult(
        version=PYTHON_DOCS_CORPUS_VERSION,
        project_root=str(root),
        source_path=str(source),
        cartridge_path=str(db_path),
        cartridge_id=DEFAULT_CARTRIDGE_ID,
        document_paths=tuple(document_relpaths or ("<all-python-docs>",)),
        limit=limit,
        reset=reset,
        include_prose=include_prose,
        records_seen=len(records),
        objects_written=objects_written,
        object_count=manifest.object_count,
        relation_count=manifest.relation_count,
        provenance_count=manifest.provenance_count,
        ast_parseable_count=sum(1 for record in ast_records if record.ast_summary and record.ast_summary.is_parseable),
        ast_failed_count=sum(1 for record in ast_records if record.ast_summary and not record.ast_summary.is_parseable),
        signature_count=sum(1 for record in records if record.kind == "python_api_signature"),
        code_example_count=sum(1 for record in records if record.kind == "python_code_example"),
        doctest_example_count=sum(1 for record in records if record.kind == "python_doctest_example"),
        grammar_rule_count=sum(1 for record in records if record.kind == "python_grammar_rule"),
        sample_records=tuple(_sample_record(record) for record in records[:8]),
    )


def _load_records(
    source: Path,
    *,
    limit: int | None,
    include_prose: bool,
    document_relpaths: tuple[str, ...] | None,
) -> list[PythonDocsRecord]:
    if document_relpaths is None:
        return list(iter_python_docs_records(source, limit=limit, include_prose=include_prose))
    records: list[PythonDocsRecord] = []
    for relpath in document_relpaths:
        path = (source / relpath).resolve()
        _ensure_project_owned(source, path)
        records.extend(extract_python_docs_file(path, source, include_prose=include_prose))
        if limit is not None and len(records) >= limit:
            return records[: max(0, limit)]
    return records


def python_docs_record_to_semantic_object(record: PythonDocsRecord, block_index: int = 0) -> SemanticObject:
    """Convert one extracted Python docs record into a canonical semantic object."""
    ast_data = record.ast_summary.to_dict() if record.ast_summary else None
    metadata = {
        "corpus": "official_python_docs_text",
        "python_docs_corpus_version": PYTHON_DOCS_CORPUS_VERSION,
        "source_relpath": record.source_relpath,
        "line_start": record.line_start,
        "line_end": record.line_end,
        **record.metadata,
    }
    surfaces = SemanticSurfaceSet(
        verbatim={"content": record.content},
        structural={
            "block_index": block_index,
            "heading_trail": list(record.heading_trail),
            "source_relpath": record.source_relpath,
            "line_start": record.line_start,
            "line_end": record.line_end,
        },
        grammatical={
            "format": "python_docs_text",
            "record_kind": record.kind,
            "symbol": record.metadata.get("symbol", ""),
            "ast": ast_data,
        },
        statistical={
            "line_count": max(1, record.line_end - record.line_start + 1),
            "token_count": len(record.content.split()),
            "char_count": len(record.content),
        },
        semantic={
            "projection_role": _projection_role(record.kind),
            "heading_context": list(record.heading_trail),
        },
    )
    provenance = ProvenanceRecord(
        source_ref=record.source_ref,
        transform_status=TransformStatus.REVERSIBLY_MAPPABLE,
        method="python_docs_projection_extraction",
        confidence=0.94,
        metadata={
            "source_relpath": record.source_relpath,
            "line_start": record.line_start,
            "line_end": record.line_end,
            "record_kind": record.kind,
        },
    )
    return SemanticObject.create(
        kind=record.kind,
        content=record.content,
        surfaces=surfaces,
        relations=_record_relations(record),
        provenance=(provenance,),
        source_ref=record.source_ref,
        source_span=SourceSpan(start=record.line_start, end=record.line_end, unit="line"),
        local_context={
            "block_index": block_index,
            "heading_trail": list(record.heading_trail),
            "source_relpath": record.source_relpath,
        },
        metadata=metadata,
    )


def _record_relations(record: PythonDocsRecord) -> tuple[SemanticRelation, ...]:
    relations: list[SemanticRelation] = []
    source_ref = record.source_ref
    symbol = str(record.metadata.get("symbol", "")).strip()
    if symbol:
        relations.append(
            _relation(
                RelationPredicate.REFERENCES,
                f"py:symbol:{symbol}",
                source_ref,
                "python_api_signature_symbol",
                {"symbol": symbol},
            )
        )
    if record.ast_summary:
        ast_summary = record.ast_summary
        ast_ref = versioned_digest("pyast", "v1", {"source": record.content, "summary": ast_summary.to_dict()})
        relations.append(
            _relation(
                RelationPredicate.TRANSFORMS_TO,
                f"py:ast:{ast_ref}",
                source_ref,
                "python_ast_projection",
                {"parse_status": ast_summary.parse_status},
            )
        )
        if ast_summary.is_parseable:
            for name in ast_summary.defined_names:
                relations.append(_relation(RelationPredicate.REFERENCES, f"py:symbol:{name}", source_ref, "ast_defined_name", {"name": name}))
            for name in ast_summary.call_names:
                relations.append(_relation(RelationPredicate.REFERENCES, f"py:call:{name}", source_ref, "ast_call_name", {"name": name}))
            for name in ast_summary.imported_modules:
                relations.append(_relation(RelationPredicate.REFERENCES, f"py:import:{name}", source_ref, "ast_import", {"name": name}))
    return tuple(relations)


def _relation(
    predicate: RelationPredicate,
    target_ref: str,
    source_ref: str,
    basis: str,
    metadata: dict[str, Any],
) -> SemanticRelation:
    return SemanticRelation(
        predicate=predicate,
        target_ref=target_ref,
        source_ref=source_ref,
        weight=0.82,
        confidence=0.88,
        metadata={
            "enrichment_pass": "python_docs_projection_relations",
            "enrichment_version": PYTHON_DOCS_CORPUS_VERSION,
            "basis": basis,
            **metadata,
        },
    )


def _projection_role(kind: str) -> str:
    return {
        "python_doc_section": "context_anchor",
        "python_api_signature": "symbol_binding",
        "python_code_example": "executable_structure",
        "python_doctest_example": "executable_structure",
        "python_grammar_rule": "syntax_structure",
        "python_prose_description": "english_description",
    }.get(kind, "python_docs_unit")


def _sample_record(record: PythonDocsRecord) -> dict[str, Any]:
    return {
        "kind": record.kind,
        "source_relpath": record.source_relpath,
        "line_start": record.line_start,
        "line_end": record.line_end,
        "heading_trail": list(record.heading_trail),
        "preview": _preview(record.content),
    }


def _preview(content: str, limit: int = 160) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def _ensure_project_owned(root: Path, path: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Python docs corpus path is outside project root: {path}") from exc
