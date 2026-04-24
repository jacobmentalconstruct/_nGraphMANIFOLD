"""Semantic cartridge persistence store."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Iterable, Iterator
from typing import Any

from src.core.representation import SemanticObject, SemanticRelation
from src.core.representation.canonical import canonical_json, versioned_digest

from .schema import SCHEMA_SQL, SCHEMA_VERSION, SCHEMA_VERSION_TEXT

DEFAULT_CARTRIDGE_ID = "default"


@dataclass(frozen=True)
class CartridgeManifest:
    """Manifest and readiness counters for a semantic cartridge."""

    cartridge_id: str
    schema_version: int
    schema_version_text: str
    created_at: str
    updated_at: str
    object_count: int
    occurrence_count: int
    relation_count: int
    provenance_count: int
    is_ready: bool
    notes: str = ""


@dataclass(frozen=True)
class CartridgeReadiness:
    """Small readiness report for persistence-layer consumers."""

    is_ready: bool
    object_count: int
    occurrence_count: int
    relation_count: int
    provenance_count: int
    blockers: tuple[str, ...] = ()


class SemanticCartridge:
    """SQLite-backed persistence boundary for semantic objects."""

    def __init__(self, db_path: Path | str, cartridge_id: str = DEFAULT_CARTRIDGE_ID) -> None:
        self.db_path = Path(db_path)
        self.cartridge_id = cartridge_id

    def initialize(self) -> None:
        """Create or migrate the cartridge schema for the current version."""
        if self.db_path != Path(":memory:"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self._ensure_manifest(conn)
            self._refresh_manifest(conn)

    def connect(self) -> sqlite3.Connection:
        """Open a configured SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Open a connection and always close it after use."""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def upsert_object(self, obj: SemanticObject) -> None:
        """Persist one semantic object and its projections."""
        self.upsert_objects((obj,))

    def upsert_objects(self, objects: Iterable[SemanticObject]) -> int:
        """Persist semantic objects and refresh manifest once at the end."""
        now = utc_now()
        self.initialize()
        count = 0
        with self.connection() as conn:
            with conn:
                for obj in objects:
                    self._upsert_object_projection(conn, obj, now)
                    count += 1
                self._refresh_manifest(conn)
        return count

    def _upsert_object_projection(
        self,
        conn: sqlite3.Connection,
        obj: SemanticObject,
        now: str,
    ) -> None:
        """Persist one semantic object using an existing transaction."""
        conn.execute(
            """
            INSERT INTO semantic_objects(
                semantic_id, kind, content, identity_version, object_json,
                metadata_json, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(semantic_id) DO UPDATE SET
                kind = excluded.kind,
                content = excluded.content,
                identity_version = excluded.identity_version,
                object_json = excluded.object_json,
                metadata_json = excluded.metadata_json,
                updated_at = excluded.updated_at
            """,
            (
                obj.semantic_id,
                obj.kind,
                obj.content,
                obj.identity.version,
                obj.to_json(),
                canonical_json(obj.metadata),
                now,
                now,
            ),
        )
        if obj.occurrence:
            occurrence = obj.occurrence
            conn.execute(
                """
                INSERT OR REPLACE INTO semantic_occurrences(
                    occurrence_id, semantic_id, source_ref, source_span_json,
                    local_context_json, occurrence_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    occurrence.occurrence_id,
                    obj.semantic_id,
                    occurrence.source_ref,
                    canonical_json(occurrence.source_span.to_dict()),
                    canonical_json(occurrence.local_context),
                    canonical_json(occurrence.to_dict()),
                    now,
                ),
            )

        self._replace_relation_projection(conn, obj.semantic_id, obj.relations, now)

        conn.execute("DELETE FROM provenance_records WHERE semantic_id = ?", (obj.semantic_id,))
        for index, record in enumerate(obj.provenance):
            provenance_id = provenance_record_id(obj.semantic_id, record.to_dict(), index)
            conn.execute(
                """
                INSERT INTO provenance_records(
                    provenance_id, semantic_id, source_ref, transform_status,
                    method, confidence, provenance_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provenance_id,
                    obj.semantic_id,
                    record.source_ref,
                    record.transform_status.value,
                    record.method,
                    record.confidence,
                    canonical_json(record.to_dict()),
                    now,
                ),
            )

    def upsert_relations(
        self,
        semantic_id: str,
        relations: Iterable[SemanticRelation],
        relation_scope: str = "phase5_relation_enrichment",
    ) -> None:
        """Persist relation projections for an existing semantic object."""
        now = utc_now()
        self.initialize()
        with self.connection() as conn:
            with conn:
                exists = conn.execute(
                    "SELECT 1 FROM semantic_objects WHERE semantic_id = ?",
                    (semantic_id,),
                ).fetchone()
                if exists is None:
                    raise ValueError(f"Cannot attach relations to unknown semantic_id: {semantic_id}")

                rows = conn.execute(
                    """
                    SELECT relation_json
                    FROM semantic_relations
                    WHERE semantic_id = ?
                    ORDER BY relation_id
                    """,
                    (semantic_id,),
                ).fetchall()
                preserved: list[SemanticRelation] = []
                for row in rows:
                    relation_data = json.loads(row["relation_json"])
                    if relation_data.get("metadata", {}).get("enrichment_pass") != relation_scope:
                        preserved.append(SemanticRelation.from_dict(relation_data))
                self._replace_relation_projection(
                    conn,
                    semantic_id,
                    tuple(preserved) + tuple(relations),
                    now,
                )
                self._refresh_manifest(conn)

    def get_object(self, semantic_id: str) -> SemanticObject | None:
        """Load a semantic object by semantic identity."""
        self.initialize()
        with self.connection() as conn:
            row = conn.execute(
                "SELECT object_json FROM semantic_objects WHERE semantic_id = ?",
                (semantic_id,),
            ).fetchone()
        if row is None:
            return None
        return SemanticObject.from_dict(json.loads(row["object_json"]))

    def all_objects(self) -> list[SemanticObject]:
        """Load every stored semantic object in deterministic source order."""
        self.initialize()
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT object_json
                FROM semantic_objects
                ORDER BY semantic_id
                """
            ).fetchall()
        return [SemanticObject.from_dict(json.loads(row["object_json"])) for row in rows]

    def delete_objects_for_source(self, source_ref: str) -> int:
        """Delete objects whose occurrence belongs to a source reference."""
        self.initialize()
        with self.connection() as conn:
            with conn:
                rows = conn.execute(
                    """
                    SELECT semantic_id
                    FROM semantic_occurrences
                    WHERE source_ref = ?
                    """,
                    (source_ref,),
                ).fetchall()
                semantic_ids = [row["semantic_id"] for row in rows]
                for semantic_id in semantic_ids:
                    conn.execute("DELETE FROM semantic_objects WHERE semantic_id = ?", (semantic_id,))
                self._refresh_manifest(conn)
        return len(semantic_ids)

    def source_refs(self) -> list[str]:
        """Return distinct source references currently stored in the cartridge."""
        self.initialize()
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT source_ref
                FROM semantic_occurrences
                ORDER BY source_ref
                """
            ).fetchall()
        return [str(row["source_ref"]) for row in rows]

    def get_occurrence(self, occurrence_id: str) -> dict[str, Any] | None:
        """Return a stored occurrence projection."""
        self.initialize()
        with self.connection() as conn:
            row = conn.execute(
                "SELECT occurrence_json FROM semantic_occurrences WHERE occurrence_id = ?",
                (occurrence_id,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row["occurrence_json"])

    def relations_for(self, semantic_id: str) -> list[dict[str, Any]]:
        """Return stored relation projections for a semantic object."""
        self.initialize()
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT relation_json
                FROM semantic_relations
                WHERE semantic_id = ?
                ORDER BY relation_id
                """,
                (semantic_id,),
            ).fetchall()
        return [json.loads(row["relation_json"]) for row in rows]

    def relations_targeting(self, target_ref: str) -> list[dict[str, Any]]:
        """Return relation projections that point at a target reference."""
        self.initialize()
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT semantic_id, relation_json
                FROM semantic_relations
                WHERE target_ref = ?
                ORDER BY relation_id
                """,
                (target_ref,),
            ).fetchall()
        return [
            {
                "semantic_id": row["semantic_id"],
                "relation": json.loads(row["relation_json"]),
            }
            for row in rows
        ]

    def provenance_for(self, semantic_id: str) -> list[dict[str, Any]]:
        """Return stored provenance projections for a semantic object."""
        self.initialize()
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT provenance_json
                FROM provenance_records
                WHERE semantic_id = ?
                ORDER BY provenance_id
                """,
                (semantic_id,),
            ).fetchall()
        return [json.loads(row["provenance_json"]) for row in rows]

    def manifest(self) -> CartridgeManifest:
        """Return the cartridge manifest."""
        self.initialize()
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM cartridge_manifest WHERE cartridge_id = ?",
                (self.cartridge_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("Cartridge manifest missing after initialization")
        return CartridgeManifest(
            cartridge_id=row["cartridge_id"],
            schema_version=row["schema_version"],
            schema_version_text=row["schema_version_text"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            object_count=row["object_count"],
            occurrence_count=row["occurrence_count"],
            relation_count=row["relation_count"],
            provenance_count=row["provenance_count"],
            is_ready=bool(row["is_ready"]),
            notes=row["notes"],
        )

    def readiness(self) -> CartridgeReadiness:
        """Return a minimal readiness report."""
        manifest = self.manifest()
        blockers: list[str] = []
        if manifest.object_count < 1:
            blockers.append("no semantic objects stored")
        return CartridgeReadiness(
            is_ready=not blockers,
            object_count=manifest.object_count,
            occurrence_count=manifest.occurrence_count,
            relation_count=manifest.relation_count,
            provenance_count=manifest.provenance_count,
            blockers=tuple(blockers),
        )

    def _ensure_manifest(self, conn: sqlite3.Connection) -> None:
        now = utc_now()
        conn.execute(
            """
            INSERT OR IGNORE INTO cartridge_manifest(
                cartridge_id, schema_version, schema_version_text,
                created_at, updated_at, notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                self.cartridge_id,
                SCHEMA_VERSION,
                SCHEMA_VERSION_TEXT,
                now,
                now,
                "nGraphMANIFOLD semantic cartridge",
            ),
        )

    def _refresh_manifest(self, conn: sqlite3.Connection) -> None:
        counts = {
            "object_count": count_rows(conn, "semantic_objects"),
            "occurrence_count": count_rows(conn, "semantic_occurrences"),
            "relation_count": count_rows(conn, "semantic_relations"),
            "provenance_count": count_rows(conn, "provenance_records"),
        }
        conn.execute(
            """
            UPDATE cartridge_manifest
            SET schema_version = ?,
                schema_version_text = ?,
                updated_at = ?,
                object_count = ?,
                occurrence_count = ?,
                relation_count = ?,
                provenance_count = ?,
                is_ready = ?
            WHERE cartridge_id = ?
            """,
            (
                SCHEMA_VERSION,
                SCHEMA_VERSION_TEXT,
                utc_now(),
                counts["object_count"],
                counts["occurrence_count"],
                counts["relation_count"],
                counts["provenance_count"],
                1 if counts["object_count"] > 0 else 0,
                self.cartridge_id,
            ),
        )

    def _replace_relation_projection(
        self,
        conn: sqlite3.Connection,
        semantic_id: str,
        relations: Iterable[SemanticRelation],
        now: str,
    ) -> None:
        conn.execute("DELETE FROM semantic_relations WHERE semantic_id = ?", (semantic_id,))
        for index, relation in enumerate(relations):
            relation_id = relation_record_id(semantic_id, relation.to_dict(), index)
            conn.execute(
                """
                INSERT INTO semantic_relations(
                    relation_id, semantic_id, predicate, source_ref, target_ref,
                    weight, confidence, metadata_json, relation_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relation_id,
                    semantic_id,
                    relation.predicate.value,
                    relation.source_ref,
                    relation.target_ref,
                    relation.weight,
                    relation.confidence,
                    canonical_json(relation.metadata),
                    canonical_json(relation.to_dict()),
                    now,
                ),
            )


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    """Count rows in a known schema table."""
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def relation_record_id(semantic_id: str, relation: dict[str, Any], index: int) -> str:
    """Return a deterministic relation row id."""
    return versioned_digest("rel", "v1", {"semantic_id": semantic_id, "relation": relation, "index": index})


def provenance_record_id(semantic_id: str, record: dict[str, Any], index: int) -> str:
    """Return a deterministic provenance row id."""
    return versioned_digest("prov", "v1", {"semantic_id": semantic_id, "record": record, "index": index})


def new_cartridge_path(root: Path, name: str | None = None) -> Path:
    """Return a project-local cartridge path under the data folder."""
    cartridge_name = name or f"cartridge-{uuid.uuid4().hex}.sqlite3"
    return root / "data" / "cartridges" / cartridge_name


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
