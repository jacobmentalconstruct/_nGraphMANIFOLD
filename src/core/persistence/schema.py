"""SQLite schema for semantic cartridges."""

from __future__ import annotations

SCHEMA_VERSION = 1
SCHEMA_VERSION_TEXT = "1.0.0"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cartridge_manifest (
    cartridge_id TEXT PRIMARY KEY,
    schema_version INTEGER NOT NULL,
    schema_version_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    object_count INTEGER NOT NULL DEFAULT 0,
    occurrence_count INTEGER NOT NULL DEFAULT 0,
    relation_count INTEGER NOT NULL DEFAULT 0,
    provenance_count INTEGER NOT NULL DEFAULT 0,
    is_ready INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS semantic_objects (
    semantic_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    identity_version TEXT NOT NULL,
    object_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS semantic_occurrences (
    occurrence_id TEXT PRIMARY KEY,
    semantic_id TEXT NOT NULL REFERENCES semantic_objects(semantic_id) ON DELETE CASCADE,
    source_ref TEXT NOT NULL,
    source_span_json TEXT NOT NULL,
    local_context_json TEXT NOT NULL,
    occurrence_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_semantic_occurrences_semantic
ON semantic_occurrences(semantic_id);

CREATE INDEX IF NOT EXISTS idx_semantic_occurrences_source
ON semantic_occurrences(source_ref);

CREATE TABLE IF NOT EXISTS semantic_relations (
    relation_id TEXT PRIMARY KEY,
    semantic_id TEXT NOT NULL REFERENCES semantic_objects(semantic_id) ON DELETE CASCADE,
    predicate TEXT NOT NULL,
    source_ref TEXT,
    target_ref TEXT NOT NULL,
    weight REAL NOT NULL,
    confidence REAL NOT NULL,
    metadata_json TEXT NOT NULL,
    relation_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_semantic_relations_semantic
ON semantic_relations(semantic_id);

CREATE INDEX IF NOT EXISTS idx_semantic_relations_target
ON semantic_relations(target_ref);

CREATE INDEX IF NOT EXISTS idx_semantic_relations_predicate
ON semantic_relations(predicate);

CREATE TABLE IF NOT EXISTS provenance_records (
    provenance_id TEXT PRIMARY KEY,
    semantic_id TEXT NOT NULL REFERENCES semantic_objects(semantic_id) ON DELETE CASCADE,
    source_ref TEXT NOT NULL,
    transform_status TEXT NOT NULL,
    method TEXT NOT NULL,
    confidence REAL NOT NULL,
    provenance_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_provenance_semantic
ON provenance_records(semantic_id);

CREATE INDEX IF NOT EXISTS idx_provenance_source
ON provenance_records(source_ref);

CREATE TABLE IF NOT EXISTS derived_vector_views (
    semantic_id TEXT PRIMARY KEY REFERENCES semantic_objects(semantic_id) ON DELETE CASCADE,
    vector_model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    vector_blob BLOB NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS derived_graph_views (
    graph_view_id TEXT PRIMARY KEY,
    semantic_id TEXT NOT NULL REFERENCES semantic_objects(semantic_id) ON DELETE CASCADE,
    node_ref TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_derived_graph_views_semantic
ON derived_graph_views(semantic_id);
"""


def expected_tables() -> tuple[str, ...]:
    """Return the schema tables owned by the persistence layer."""
    return (
        "cartridge_manifest",
        "semantic_objects",
        "semantic_occurrences",
        "semantic_relations",
        "provenance_records",
        "derived_vector_views",
        "derived_graph_views",
    )
