# Canonical Deterministic Baseline

_Status: Active doctrine, protected baseline recorded_

This document records the protected local evidence corpus that makes later
semantic-space docking safe. It is subordinate to
`builder_constraint_contract.md` and complements `ARCHITECTURE.md`,
`SOURCE_PROVENANCE.md`, and `semantic_os_conceptual_build_plan.md`.

## Purpose

nGraphMANIFOLD now has deterministic corpus surfaces that were generated,
measured, repaired, and scored before any machine-learning embedding layer was
introduced. Those surfaces are not temporary scaffolding. They are the local
evidence baseline against which future semantic-space projections must be
checked.

This baseline is canonical local evidence, not final universal truth. It is
valuable because it preserves project-owned structure, provenance, relations,
and disambiguation behavior without opaque model deformation.

## Protected Artifacts

The protected baseline currently consists of three generated cartridges:

| Artifact | Role | Protection Meaning |
| --- | --- | --- |
| `data/cartridges/base_english_lexicon.sqlite3` | English lexical prior | Preserves deterministic headword, definition, inferred lexical structure, provenance, and lexical relations. |
| `data/cartridges/python_docs.sqlite3` | Python documentation prior | Preserves deterministic Python-doc segmentation, source spans, AST-backed candidates, provenance, and relations. |
| `data/cartridges/project_documents.sqlite3` | Project-local doctrine prior | Preserves deterministic project-doc semantic objects, relations, provenance, scoring evidence, and profile boundaries. |

The files live under `/data/`, which is intentionally ignored by git. The
doctrine and future manifest contract therefore live in tracked documentation.

## Protection Rules

- Embedding output must not mutate, merge, rewrite, or replace these baseline
  cartridges in place.
- Regeneration is allowed only through project-owned ingest commands and must
  be explicitly versioned, manifest-recorded, and rechecked against the current
  acceptance gates.
- Baseline semantic object identity, deterministic relations, and provenance
  remain acceptance anchors after any embedding or vector-view pilot.
- ML vector neighborhoods are evidence candidates. They are not graph truth
  until promoted into explicit typed relations with provenance and confidence.
- `derived_vector_views` is the intended persistence surface for future vector
  projections. It is not a new identity layer.

## Semantic Docking Policy

Semantic docking means attaching protected local semantic objects to an
existing stable semantic substrate without surrendering local truth. The first
planned docking substrate is local Ollama embeddings.

Default future model:

```text
mxbai-embed-large:latest
```

Fallback model:

```text
all-minilm:latest
```

The fallback is reserved for speed or resource pressure. It is not the default
semantic surface.

Embedding transforms are interpretive / heuristic projections. They may reveal
neighborhoods, gradients, analogies, and search candidates around the baseline,
but they may not redefine canonical semantic identity or overwrite
deterministic relation/provenance truth.

## Future Baseline Manifest Contract

A later implementation tranche should generate a local manifest at:

```text
data/cartridges/baseline_manifest.json
```

The manifest is a generated local artifact and remains under ignored `/data/`.
Tracked docs own the contract for its shape.

Each protected artifact entry should include:

- cartridge name
- baseline role
- object count
- relation count
- provenance count
- source references or source profile
- build command
- generator or parser version
- file hash
- created time
- lock policy

The manifest should let an operator or builder answer whether a vector pilot
preserved baseline cartridge counts and hashes before and after projection.

## Non-Goals

- no schema migration in the doctrine tranche
- no vector generation before the baseline doctrine is recorded
- no API embedder or cloud semantic-space dependency
- no cartridge merge into a single undifferentiated truth store
- no replacement of deterministic scoring or falsifier panels with vector
  similarity

## Acceptance Rule

Any future vector pilot must preserve the baseline first and improve
inspection, query, or evidence gathering second. If those goals conflict, the
protected deterministic baseline wins.
