# Source Provenance

_Status: Active reference ledger, no runtime borrowing yet_

This document records approved reference sources and sourcing intent for
nGraphMANIFOLD. It does not grant permission to copy whole apps or create hidden
runtime dependencies. The builder constraint contract remains authoritative.

## Sourcing Rule

Preferred order:

1. original implementation inside nGraphMANIFOLD
2. bounded rewrite informed by reference material
3. narrow structured extraction of the smallest viable hunk
4. larger transplant only under strict exception conditions

Any meaningful borrowed, extracted, or transplanted logic must be:

- re-homed into this project
- placed under a clear owner
- cleaned of old environment coupling
- tested or verified
- recorded in this file
- recorded in the app journal

## Current Provenance Status

No application runtime code has been borrowed into nGraphMANIFOLD.

Phase 2 implemented the canonical semantic object as original project-owned
code under `src/core/representation/`. The model is architecturally informed by
the documented HyperHunk/surface idea, but no parts-bin code was copied,
extracted, transplanted, or imported.

Phase 3 implemented the semantic cartridge as original project-owned code under
`src/core/persistence/`. It is architecturally informed by TripartiteDataSTORE's
structural/semantic/graph cartridge concept, but no Tripartite code, schema
text, functions, classes, or runtime imports were copied into the project.

Phase 4 implemented the source intake adapter as original project-owned code
under `src/core/transformation/`. It is architecturally informed by the idea of
source splitting into surface-bearing semantic units, but no Splitter engine,
TreeSitter logic, token-budget code, or parts-bin runtime module was copied,
extracted, transplanted, or imported.

Phase 5 implemented the relation enrichment pass as original project-owned code
under `src/core/analysis/`. It is architecturally informed by the Emitter idea
of explicit relation enrichment and graph-ready edges, but no Emitter nucleus,
training logic, relation DSL implementation, graph assembler code, or
parts-bin runtime module was copied, extracted, transplanted, or imported.

Phase 6 implemented the traversal artifact as original project-owned code under
`src/core/analysis/`. It is architecturally informed by NodeWALKER readiness,
trace, and scoring concepts, but no NodeWALKER UI, mutation agent, patch
approval workflow, traversal implementation, or parts-bin runtime module was
copied, extracted, transplanted, or imported.

Phase 7 implemented the minimal execution pathway as original project-owned
code under `src/core/execution/`. It is architecturally informed by the project
doctrine that semantic structures must produce inspectable execution intent,
but no external execution engine, automation framework, trusted-execution code,
or parts-bin runtime module was copied, extracted, transplanted, or imported.

Phase 8 implemented the thin MCP usefulness seam as original project-owned code
under `src/core/coordination/`. It is architecturally informed by the need for a
future builder-facing MCP wrapper, but no MCP server, MCP SDK, external protocol
runtime, `.dev-tools` package, or parts-bin runtime module was copied,
extracted, transplanted, imported, or made a dependency.

Prototype tuning and scoring implemented the scoring harness as original
project-owned code under `src/core/coordination/`. It is architecturally
informed by the completed prototype spine and the MCP seam usefulness dimensions,
but no benchmark package, MCP runtime, `.dev-tools` package, or parts-bin
runtime module was copied, extracted, transplanted, imported, or made a
dependency.

The local MCP adapter and raw inspector were implemented as original
project-owned code under `src/core/coordination/` and `src/ui/`. They are
architecturally informed by the existing seam manifest and traversal artifact,
but no MCP SDK, host-panel code, UI toolkit wrapper, `.dev-tools` package, or
parts-bin runtime module was copied, extracted, transplanted, imported, or made
a dependency. The UI uses Python's standard Tkinter surface only.

The MCP tool registration candidate was implemented as original project-owned
code under `src/core/coordination/`. It is architecturally informed by the
local traversal adapter and seam manifest, but no MCP SDK, protocol server,
host tool configuration, `.dev-tools` package, or parts-bin runtime module was
copied, extracted, transplanted, imported, or made a dependency.

Persistent MCP inspection history was implemented as original project-owned
code under `src/core/coordination/`. It uses the standard library SQLite module
and stores registered call/capture JSON. No telemetry package, MCP SDK,
`.dev-tools` package, or parts-bin runtime module was copied, extracted,
transplanted, imported, or made a dependency.

Project document ingestion was implemented as original project-owned code under
`src/core/coordination/` using the existing project-owned transformation,
analysis, persistence, registry, and history surfaces. No repo scanner, external
indexer, `.dev-tools` package, or parts-bin runtime module was copied,
extracted, transplanted, imported, or made a dependency.

Real builder-task scoring was implemented as original project-owned code under
`src/core/coordination/`. It uses the existing seam scoring dimensions,
document-ingestion path, registered traversal tool, and inspection history. No
external evaluation package, benchmark framework, `.dev-tools` package, or
parts-bin runtime module was copied, extracted, transplanted, imported, or made
a dependency.

The history-aware MCP inspector was implemented as original project-owned code
under `src/core/coordination/` and `src/ui/`. It summarizes existing persisted
history and preserves raw JSON. No dashboard framework, visualization package,
`.dev-tools` package, or parts-bin runtime module was copied, extracted,
transplanted, imported, or made a dependency.

Traversal seed search and selection was implemented as original project-owned
code under `src/core/coordination/`, with a small persistence query extension
under `src/core/persistence/`. It searches already-ingested project-document
semantic objects with deterministic text ranking, selects a registered
traversal seed, and records the selected call in inspection history. No search
engine, embedding package, `.dev-tools` package, or parts-bin runtime module
was copied, extracted, transplanted, imported, or made a dependency.

The English lexical baseline was implemented as original project-owned code
under `src/core/transformation/` and `src/core/coordination/`. It uses the
project-owned source file `assets/_corpus_examples/dictionary_alpha_arrays.json`
to build `data/cartridges/base_english_lexicon.sqlite3`. The source is treated as a
derived dictionary alpha-array corpus reliable for headword and raw definition
text; inferred senses, labels, examples, and cross references are parser
candidates only. No `.parts` runtime path, external parser package, or
dictionary service was imported or made a dependency.

The Python docs projection corpus was implemented as original project-owned
code under `src/core/transformation/` and `src/core/coordination/`. It uses the
project-owned source directory
`assets/_corpus_examples/python-3.11.15-docs-text` to build
`data/cartridges/python_docs.sqlite3`. The adapter performs bounded
documentation-text segmentation and uses Python's standard-library `ast` only
on isolated candidate snippets. No Docling runtime dependency, `.dev-tools`
package, host MCP tool, external parser package, search engine, embedding
package, or parts-bin runtime module was copied, extracted, transplanted,
imported, or made a dependency.

The context projection / rebinding layer was implemented as original
project-owned code under `src/core/coordination/context_projection.py`. It reads
existing project-owned cartridges as separated priors, scores candidates with
deterministic local heuristics, and emits a query projection frame. No external
search engine, embedding package, MCP SDK, `.dev-tools` package, or parts-bin
runtime module was copied, extracted, transplanted, imported, or made a
dependency.

The shared command spine was implemented as original project-owned code under
`src/core/coordination/interaction_spine.py`. It defines command/result
envelopes, records `ngraph.project.query` calls through the existing MCP
inspection history path, and provides SemanticObject projection adapters for
future persistence. No event-sourcing package, message broker, MCP SDK,
`.dev-tools` package, or parts-bin runtime module was copied, extracted,
transplanted, imported, or made a dependency.

The UI command spine pilot was implemented as original project-owned code under
`src/ui/gui_main.py`. It uses the standard-library Tk surface to expose one
minimal project-query control, calls `run_project_query_interaction`, and
records `ngraph.project.query` captures with `source_surface="ui"`. No external
UI toolkit, network MCP server, `.dev-tools` runtime package, or parts-bin UI
module was copied, imported, or made a dependency.

The context projection arbitration scorer was implemented as original
project-owned code under
`src/core/coordination/context_projection_scoring.py`. It runs bounded
project-query fixtures through the existing shared command spine, records
normal `ngraph.project.query` captures in MCP inspection history, and writes a
score artifact for tuning. No benchmark package, embedding package, MCP SDK,
`.dev-tools` package, or parts-bin runtime module was copied, imported, or made
a dependency.

The task-aware seed-fitness scorer was implemented as original project-owned
code under `src/core/coordination/seed_fitness.py`. It unifies project-document
seed selection for `mcp-search-seeds` and `mcp-score-tasks`, emits inspectable
score breakdowns, and applies builder-task policy only in the coordination
layer. No embedding package, vector index, search engine, MCP SDK,
`.dev-tools` package, or parts-bin runtime module was copied, imported, or made
a dependency.

Seed fitness inspector visibility was implemented as original project-owned
code under `src/core/coordination/seed_search.py` and `src/ui/mcp_inspector.py`.
It adds source-flow inspection objects around selected traversal seeds and
renders them through the existing standard-library Tk inspector Summary / Raw
JSON pattern. No graph visualization package, external UI framework, MCP SDK,
`.dev-tools` package, or parts-bin runtime module was copied, imported, or made
a dependency.

The formatted interaction stream was implemented as original project-owned code
under `src/core/coordination/history_inspector.py`, `src/ui/mcp_inspector.py`,
and `src/app.py`. It projects existing MCP inspection history records into
chronological query/response objects and renders them as labeled object blocks
with standard-library Tk. The stream appends newly seen call ids and pauses
autoscroll while the vertical scrollbar is held, but it remains only an
inspection projection over history. No message broker, event-sourcing package,
external UI framework, MCP SDK, `.dev-tools` package, or parts-bin runtime
module was copied, imported, or made a dependency.

Projection candidate flow visibility and the unified cockpit were implemented
as original project-owned code under
`src/core/coordination/context_projection.py`,
`src/core/coordination/history_inspector.py`, `src/ui/mcp_inspector.py`, and
`src/app.py`. They project additional ordered evidence and score-state summaries
from existing cartridges, history, and score artifacts without creating a new
truth store. No dashboard framework, graph-visualization package, event broker,
MCP SDK, `.dev-tools` runtime package, or parts-bin runtime module was copied,
imported, or made a dependency.

The shared host state spine was implemented as original project-owned code
under `src/core/coordination/host_workspace.py`, `src/ui/gui_main.py`,
`src/ui/mcp_inspector.py`, and `src/app.py`. It introduces a coordination-owned
live host snapshot and dispatcher over the existing durable history/score
ledger, but it does not add a network API, websocket layer, external event
bus, `.dev-tools` runtime package, or parts-bin runtime module.

The sources below are approved reference candidates only.

## Reference Source: `.parts/_BDNeuralTranslationSUITE`

### Role

Reference foundation for semantic-object intake, transformation, relation
formation, graph assembly, and training/inference boundaries.

### Useful Subsources

- `_BDHyperNodeSPLITTER`
  - informs source-to-HyperHunk splitting
  - informs multi-surface object population
  - informs token-budget negotiation and context windows
  - candidate influence for Representation and Transformation layers

- `_BDHyperNeuronEMITTER`
  - informs relation scoring via Bootstrap Nucleus
  - informs relation DSL and graph assembly
  - informs deterministic embedding and training/inference boundaries
  - candidate influence for Representation, Transformation, and Analysis
    layers

### Current Permission State

Reference allowed. Runtime dependency forbidden. No wholesale copy approved.
Possible future extraction must be narrow and re-homed into nGraphMANIFOLD
ownership.

### Likely First Candidate

A bounded rewrite of the HyperHunk-style contract into this project's own
`SemanticObject` model. This should preserve the idea of surfaces, identity,
occurrence, relations, context, and provenance without importing the older app
boundary wholesale.

## Reference Source: `.parts/_TripartiteDataSTORE`

### Role

Reference foundation for durable semantic persistence.

### Useful Subsources

- structural layer: files, tree nodes, and chunks
- semantic layer: embeddings, chunk manifest, search surfaces
- graph layer: graph nodes and graph edges
- cartridge manifest and ingest-run tracking
- schema migration patterns
- FTS and SQLite-backed local portability

### Current Permission State

Reference allowed. Runtime dependency forbidden. No wholesale copy approved.
Future work should design a persistence interface around nGraphMANIFOLD's
canonical semantic object model, then adapt useful Tripartite schema ideas into
that model.

### Likely First Candidate

A bounded schema rewrite for a semantic cartridge that can store:

- semantic objects
- object occurrences
- relation records
- provenance records
- derived vector and graph views
- manifest and readiness metadata

## Reference Source: `.parts/_NodeWALKER`

### Role

Reference foundation for analysis, traversal, scoring, decision memory, and
traceable evidence walks over persisted cartridges.

### Useful Subsources

- readiness assessment over cartridge completeness
- multi-gradient traversal: structural, adjacency, semantic, graph, source
- traversal artifact and deterministic trace concepts
- scoring formula and budget state
- anti-data and decision-memory concepts
- activation/event surfaces for UI inspection

### Current Permission State

Reference allowed. Runtime dependency forbidden. No wholesale copy approved.
NodeWALKER should sit above persistence as an analysis layer, not compete with
the datastore.

### Likely First Candidate

A bounded rewrite of traversal artifact and scoring contracts after the semantic
cartridge schema exists.

## Reference Source: `.dev-tools/_project-authority`

### Role

Development-tool and builder-governance surface. This is not an application
runtime dependency.

### Useful Capabilities

- app journal initialization, query, write, export, and snapshot tooling
- project scaffold support
- module decomposition planning
- token-aware patching
- domain-boundary auditing
- blocking-call scanning
- SQLite schema inspection
- import graph mapping
- file-tree snapshots
- smoke-test running
- Python complexity scoring
- dead-code finding
- test scaffold generation
- schema diffing
- BuilderSET packed authority query/hydration/export surfaces
- constraint-registry package for task-scoped rule injection
- manifold MCP package as a possible reference for reversible
  text-evidence-hypergraph workflows

### Current Permission State

Tool use allowed when it supports project-local analysis, planning, patching, or
verification. Runtime dependency forbidden unless a tool or package is
explicitly vendored into the project under the contract's tool rules.

### Likely First Candidate

Use `.dev-tools` for analysis and verification gates during future tranches:

- file-tree snapshot after scaffold creation
- domain-boundary audit after first core modules exist
- schema inspection after persistence prototype exists
- smoke-test runner once tests are scaffolded

## Provenance Record Template

Use this template when meaningful logic is incorporated:

```text
Date:
Tranche:
Source:
Borrowed unit:
Destination owner:
Sourcing mode: original | bounded rewrite | structured extraction | transplant
Reason:
Compliance cleanup:
Tests / verification:
Journal entry:
```

