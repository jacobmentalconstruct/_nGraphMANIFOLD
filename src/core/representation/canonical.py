"""Canonical JSON and hashing helpers for semantic identity."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any


def normalize_for_identity(value: Any) -> Any:
    """Return a deterministic JSON-compatible representation."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {
            str(key): normalize_for_identity(value[key])
            for key in sorted(value.keys(), key=str)
        }
    if isinstance(value, tuple):
        return [normalize_for_identity(item) for item in value]
    if isinstance(value, list):
        return [normalize_for_identity(item) for item in value]
    if isinstance(value, set | frozenset):
        return [normalize_for_identity(item) for item in sorted(value, key=repr)]
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [normalize_for_identity(item) for item in value]
    if isinstance(value, bytes):
        return value.hex()
    return value


def canonical_json(value: Any) -> str:
    """Serialize a value as canonical compact JSON."""
    normalized = normalize_for_identity(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_digest(value: Any) -> str:
    """Return a SHA-256 hex digest for canonical JSON of value."""
    payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def versioned_digest(prefix: str, version: str, value: Any) -> str:
    """Return a versioned project identity string."""
    return f"{prefix}:{version}:{sha256_digest(value)}"
