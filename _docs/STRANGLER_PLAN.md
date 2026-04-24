# Strangler Plan

_Status: Active migration doctrine, shared host state spine parked complete_

This document defines how nGraphMANIFOLD will grow around useful prior parts
without becoming a copy of them. It is the active migration plan until a
dedicated implementation checklist supersedes it.

## Goal

Build a new semantic operating substrate by strangling useful behavior out of
the parts bin through clean contracts, clear ownership, and bounded tranches.

The goal is not to merge existing apps. The goal is to create a healthier new
application whose semantic-object model, persistence, analysis, coordination,
and execution layers remain coherent from the start.

## Governing Rules

- `builder_constraint_contract.md` is the constitution.
- `.parts` and `.dev-tools` are reference/tool surfaces, not runtime
  dependencies.
- No wholesale app copy is allowed by default.
- Borrowed logic requires the smallest viable extraction or bounded rewrite.
- Every meaningful borrowing requires provenance and journal recording.
- Each tranche must have explicit non-goals.
- Scaffold, implementation, integration, cleanup, and polish remain separate.

## Strangler Pattern

The new app will expose its own stable contracts first. Existing parts can then
be wrapped, rewritten, or replaced one boundary at a time.

The intended pattern:

1. Define the new canonical contract.
2. Add a narrow adapter from one old behavior into that contract.
3. Verify the new boundary.
4. Move the next behavior only after ownership remains clear.
5. Leave old apps in `.parts` as reference material until no longer needed.

## Target Prototype Flow

```text
source content
  -> transformation adapter
  -> SemanticObject
  -> relation/enrichment pass
  -> semantic cartridge persistence
  -> traversal / analysis
  -> traceable execution intent
```

## Phase 0: Doctrine Foundation

### In Scope

- `ARCHITECTURE.md`
- `SOURCE_PROVENANCE.md`
- `STRANGLER_PLAN.md`
- `TOOLS.md`
- app journal entry

### Non-Goals

- no code scaffold
- no copied runtime logic
- no database schema implementation
- no UI work

### Done When

- architecture declares the canonical semantic object model
- parts-bin roles are mapped
- `.dev-tools` governance/use is documented
- next tranche can start without ambiguity

## Phase 1: Scaffold Foundation

Status: parked complete as of 2026-04-21.

### In Scope

Create the application container:

- `src/app.py`
- `src/core/`
- `src/ui/`
- `tests/`
- `README.md`
- `LICENSE.md`
- `requirements.txt`
- `setup_env.bat`
- `run.bat`

Expected core subpackages:

- `src/core/representation/`
- `src/core/transformation/`
- `src/core/persistence/`
- `src/core/analysis/`
- `src/core/coordination/`
- `src/core/execution/`
- `src/core/config/`
- `src/core/logging/`

### Non-Goals

- no old app bodies copied in
- no full persistence schema yet
- no GUI beyond a placeholder if needed
- no advanced model training

### Tool Gates

- use file-tree snapshot after scaffold creation
- record scaffold in app journal

## Phase 2: Canonical Semantic Object

Status: parked complete as of 2026-04-21.

### In Scope

Implement the first project-owned object contract:

- `SemanticObject`
- `SemanticIdentity`
- `SemanticOccurrence`
- `SemanticSurfaceSet`
- `SemanticRelation`
- `ProvenanceRecord`
- serialization/deserialization
- unit tests

### Reference Sources

- HyperHunk contract from `_BDHyperNodeSPLITTER`
- Emitter relation DSL from `_BDHyperNeuronEMITTER`

### Non-Goals

- no full splitter migration
- no database write path
- no embedding provider

### Tool Gates

- domain-boundary audit once representation modules exist
- test scaffold generator if manual test structure starts to sprawl

## Phase 3: Persistence Cartridge

Status: parked complete as of 2026-04-21.

### In Scope

Create a project-owned SQLite persistence layer for semantic objects:

- schema ownership
- semantic objects table
- occurrences table
- relations table
- provenance table
- derived vector/graph view tables as needed
- cartridge manifest
- schema versioning
- readiness metadata

### Reference Sources

- TripartiteDataSTORE schema and manifest concepts
- SQLite schema inspector from `.dev-tools`

### Non-Goals

- no broad Tripartite app copy
- no viewer UI
- no full-text polish unless needed for verification

### Tool Gates

- SQLite schema inspection
- schema diff when migrations begin
- smoke tests for create/write/read round trip

## Phase 4: Intake Adapter

Status: parked complete as of 2026-04-21.

### In Scope

Build the first source-to-object path:

- source reader
- simple transformation adapter
- semantic object emitter
- provenance capture
- basic tests on small fixtures

### Reference Sources

- Splitter engines and token-budget/context-window concepts
- Tripartite chunker concepts only where they clarify fallback behavior

### Non-Goals

- no whole Splitter import
- no broad language support
- no TreeSitter dependency unless justified by the tranche

## Phase 5: Relation And Enrichment Pass

Status: complete in bounded prototype form.

### In Scope

Create a first explicit relation pass:

- structural relations
- adjacency relations
- reference relations where easily available
- traceable scoring metadata

### Reference Sources

- Emitter Bootstrap Nucleus
- Emitter graph assembler

### Non-Goals

- no FFN
- no training pipeline
- no advanced spectral/TDA work

## Phase 6: Traversal And Analysis

Status: complete in bounded prototype form.

### In Scope

Build traversal over semantic cartridges:

- readiness checks
- seed selection
- multi-gradient scoring
- traversal artifact
- trace/provenance output

### Reference Sources

- NodeWALKER manifest/readiness layer
- NodeWALKER scoring and traversal artifact concepts

### Non-Goals

- no full NodeWALKER UI
- no mutation agent
- no patch approval workflow

## Phase 7: Minimal Execution Pathway

Status: complete in bounded prototype form.

### In Scope

Make execution visible without overbuilding:

- semantic intent object
- execution plan record
- no-op or report-generation executor
- feedback relation from result to originating semantic objects

### Non-Goals

- no autonomous broad action system
- no trusted execution claims
- no distributed consensus implementation

## Phase 8: Thin MCP Usefulness Seam

Status: complete in bounded prototype form.

### In Scope

Expose the completed prototype spine through a minimal builder-facing seam:

- capability descriptors for the prototype actions
- usefulness scoring dimensions for builder/agent use
- evidence/output shapes suitable for future MCP wrapping
- tuning and evaluation hooks for repeated scoring
- documentation of what is and is not MCP yet

### Non-Goals

- no network server
- no full MCP protocol implementation
- no external tool runtime dependency
- no broad UI or automation layer
- no autonomous agent loop

## Phase 9: Prototype Tuning And Scoring

Status: complete in bounded prototype form.

### In Scope

Score whether the prototype spine is actually useful for builder work:

- repeatable builder-task fixtures
- end-to-end spine runs from source content to persisted execution result
- scoring across every MCP seam capability descriptor
- acceptance threshold checks
- first adapter-candidate recommendation

### Non-Goals

- no network server
- no full MCP protocol implementation
- no external runtime dependency
- no broad benchmark platform
- no autonomous agent loop

## Phase 10: Local MCP Adapter And Raw Inspector

Status: complete in bounded prototype form.

### In Scope

Make the first adapter visibly useful to the builder:

- local MCP-shaped adapter for `analysis.traverse_cartridge`
- raw capture envelope for capability, seam manifest, request, response, and score
- raw JSON panel for visible inspection
- headless JSON command for tests and non-UI environments

### Non-Goals

- no network server
- no full MCP protocol implementation
- no persistent inspection history
- no polished visual formatting
- no autonomous agent loop

## Phase 11: True MCP Tool Registration Candidate

Status: complete in bounded prototype form.

### In Scope

Make the first adapter callable through a project-owned registration surface:

- local MCP tool registry
- `ngraph.analysis.traverse_cartridge` registration
- serializable input/output schemas
- registered call envelope
- registry listing command
- inspector routed through the registered call path

### Non-Goals

- no network server
- no external MCP SDK dependency
- no host tool installation
- no protocol transport
- no persistent inspection history

## Phase 12: Persistent MCP Inspection History

Status: complete in bounded prototype form.

### In Scope

Persist what registered MCP-shaped tool calls see:

- SQLite inspection history store
- raw call/capture JSON
- indexed call metadata
- recent-history snapshot
- `mcp-history` command
- inspector display of recent history

### Non-Goals

- no protocol server
- no host tool installation
- no broad retention policy
- no polished visualization
- no semantic cartridge replacement

## Phase 13: Project Document Ingestion Candidate

Status: complete in bounded prototype form.

### In Scope

Move traversal from fixture content to selected project documents:

- curated project-document set
- project docs cartridge
- source-to-object ingestion
- relation enrichment
- registered traversal call
- inspection-history recording

### Non-Goals

- no repo-wide scan
- no arbitrary file ingestion
- no search engine
- no embedding pipeline
- no retention/pruning policy

## Phase 14: Real Builder Task Scoring

Status: complete in bounded prototype form.

### In Scope

Score actual builder continuation usefulness:

- real builder task fixtures
- task-specific doc traversal seeds
- inspection-history recording
- aggregate usefulness report
- project-local score artifact

### Non-Goals

- no broad benchmark suite
- no learned evaluator
- no second registered tool candidate
- no polished dashboard
- no replacement for human review

## Phase 15: History-Aware MCP Inspector

Status: complete in bounded prototype form.

### In Scope

Make persisted MCP calls easier to inspect without hiding evidence:

- summarized history-aware payload
- recent call summaries
- score artifact to call-id mapping
- Summary and Raw JSON inspector tabs
- `mcp-history-view` command

### Non-Goals

- no polished dashboard
- no custom visualization widgets
- no new document ingestion scope
- no second registered tool candidate
- no removal of raw JSON fallback

## Phase 16: Traversal Search And Seed Selection

Status: complete in bounded prototype form.

### In Scope

Make registered traversal easier to aim over project documents:

- deterministic text search over persisted semantic objects
- ranked traversal seed candidates
- selected call through `ngraph.analysis.traverse_cartridge`
- inspection-history recording for selected seed traversals
- inspector/headless command for selected seed evidence
- stale object replacement for re-ingested project-document sources

### Non-Goals

- no embeddings
- no full-text search engine
- no repo-wide scan
- no second registered tool candidate
- no polished dashboard
- no new document ingestion scope

## Phase 17: English Lexical Baseline

Status: complete in bounded prototype form.

### In Scope

Create a dedicated lexical baseline from the project-owned alpha-array
dictionary source:

- stream `assets/_corpus_examples/dictionary_alpha_arrays.json`
- preserve headword and raw definition text
- conservatively infer senses, labels, cross references, derived forms, and
  usage-example candidates
- build `data/cartridges/base_english_lexicon.sqlite3`
- add build and lookup commands
- document alpha-array caution and provenance

### Non-Goals

- no raw sliding-window dictionary ingestion
- no perfect English lexicon grammar parser claim
- no embeddings
- no Python docs ingestion
- no conversation corpus ingestion
- no merge into project-document cartridge

## Phase 18: Python Docs Projection Corpus

Status: complete in bounded prototype form.

### In Scope

Create a dedicated Python documentation/code projection layer from the
project-owned official Python docs text corpus:

- extract typed docs records from
  `assets/_corpus_examples/python-3.11.15-docs-text`
- keep the default build bounded to `library/functions.txt`,
  `reference/compound_stmts.txt`, `reference/simple_stmts.txt`, and
  `tutorial/controlflow.txt`
- classify sections, API signatures, parseable code examples, doctests, and
  grammar rules
- summarize isolated Python snippets with the standard-library `ast` module
- build `data/cartridges/python_docs.sqlite3`
- verify that the Python docs cartridge can act as a separate Python-context
  lens beside the English lexicon and project documents

### Non-Goals

- no Docling runtime dependency
- no `.dev-tools` runtime dependency
- no custom Python parser
- no embeddings
- no broad docs search product
- no merge into project-document or English lexical cartridges
- no full context rebinding layer yet

### Assessment

The tranche gives the prototype a useful Python prior: code phrases and
language terms can now resolve to API signatures, examples, doctests, grammar,
and AST-derived surfaces. It proves separable context lenses, not complete
semantic rebinding.

## Phase 19: Context Projection / Rebinding Layer

Status: complete in bounded prototype form.

### In Scope

Build the first query projection frame over existing cartridges:

- preserve sanitized English lexical naming and avoid source-branded component
  names
- read the English lexical baseline, Python docs projection corpus, and
  project-document cartridge as separate layers
- tokenize a raw query while preserving code-shaped terms such as `for`, `in`,
  `return`, and `False`
- produce per-layer candidates with scores, matched terms, evidence notes,
  source references, heading context, and compact metadata
- select a provisional layer/candidate while preserving every layer's evidence
- expose the frame through `python -m src.app project-query --query "..." --dump-json`

### Non-Goals

- no embeddings
- no full-text search engine
- no cartridge merge
- no new corpus ingestion
- no polished UI
- no external MCP server
- no claim of final semantic grounding
- no learned disambiguation

### Assessment

This phase turns the previous hand-built layered probe into a project-owned
coordination surface. It is the first actual implementation of contextual
"dipping": the query is inspected through English lexical, Python/code, and
project-local frames before the system chooses a provisional interpretation.
The scoring is deterministic and provisional; MCP inspection and usefulness
scoring are intentionally deferred to the next tranche.

## Phase 20: Projection Scoring And MCP Inspection

Status: complete in bounded prototype form.

### In Scope

- Add projection usefulness fixtures for English, Python/code, and project-local
  queries.
- Record `project-query` calls into MCP inspection history.
- Expose projection frames in the existing inspector Summary and Raw JSON views.
- Compare raw query matching against context-projected matching.
- Decide whether `project-query` should become the second registered
  MCP-shaped tool candidate.
- Add a shared command/result envelope spine for `project-query`.
- Preserve command/result captures in MCP inspection history.
- Add SemanticObject projection adapters for command/result envelopes without
  persisting them as cartridge truth yet.

### Non-Goals

- no embeddings
- no real network MCP server
- no cartridge merge
- no polished dashboard
- no broad corpus expansion
- no final semantic grounding claim

### Assessment

`project-query` now routes through the first shared command spine and is
registered as `ngraph.project.query`. The inspector can show the command/result
capture through existing history surfaces. This completes the history-first
UI/MCP alignment pilot, but not a real UI button layer or semantic cartridge
persistence for interaction events.

## Phase 21: UI Command Spine Pilot

Status: complete in bounded prototype form.

### In Scope

- Add the first user-facing UI control that emits the same `CommandEnvelope`
  shape used by CLI and MCP-shaped calls.
- Keep the command envelope as the invocation source of truth.
- Show the resulting `InteractionCapture` in the existing inspector views.
- Verify that human UI and CLI/MCP-shaped calls produce comparable history
  records.

### Non-Goals

- no broad dashboard
- no real network MCP server
- no interaction-event cartridge persistence
- no new corpus ingestion
- no hidden direct button-to-handler bypass

### Assessment

The UI is no longer a placeholder. `python -m src.app ui` opens a minimal
project-query control that records `ngraph.project.query` through the same
shared `CommandEnvelope` / `ToolResultEnvelope` / `InteractionCapture` path as
CLI and MCP-shaped calls. UI-originated records use `source_surface="ui"` and
remain history-first only. This proves the shared command spine can support a
human-facing control without making the UI a new source of truth.

## Phase 22: Layer Arbitration And Rebinding Scoring

Status: complete in bounded prototype form.

### In Scope

- Add focused scoring fixtures for English lexical, Python docs, and
  project-local query intent.
- Compare selected layers against expected context stacks.
- Tune deterministic arbitration where the current scoring chooses a weak layer.
- Keep tuning output visible through existing MCP inspection history.

### Non-Goals

- no embeddings
- no cartridge merge
- no broad UI expansion
- no real network MCP server
- no interaction-event cartridge persistence

### Assessment

`project-query-score` now runs bounded English, Python, and project-local
arbitration fixtures through the shared `ngraph.project.query` command spine.
Each fixture records a normal `InteractionCapture` in MCP inspection history
with `source_surface="scoring"`, and the aggregate context projection score is
accepted. The initial real-cartridge run scored `0.96` with all expected
selected layers passing, so no extra deterministic arbitration adjustment was
needed in this tranche.

## Phase 23: Builder Task Seed Selection Tuning

Status: complete in bounded prototype form.

### In Scope

- Inspect the weaker real-doc builder task fixtures currently scoring `0.69`.
- Compare seed hints, selected seed source documents, and expected source
  suffixes.
- Tune deterministic seed search or fixture routing over the existing bounded
  document set.
- Keep all tuning calls visible through existing MCP inspection history and
  score artifacts.

### Non-Goals

- no embeddings
- no repo-wide scan
- no broad document ingestion expansion as the first move
- no real network MCP server
- no polished UI expansion

### Assessment

Seed selection is now owned by a shared coordination-layer seed-fitness scorer.
`mcp-search-seeds` and `mcp-score-tasks` both use the same deterministic ranked
path, while builder-task scoring passes a narrow task policy for document-role
fit, heading/section affinity, continuation-marker proximity, operator-command
proximity, and expected source fit. Alphabetical source ordering is now only a
final stable fallback after score, structural score, and block order.

The real builder-task score improved to aggregate `0.93`, with all four
fixtures scoring `0.93`. This was done without embeddings, vector similarity,
projection-layer changes, cartridge merging, or persistent cross-cartridge
coupling.

## Phase 24: Seed Fitness Inspector Visibility

Status: complete in bounded prototype form.

### In Scope

- Surface selected-seed score breakdowns in inspector/history summaries where
  useful.
- Keep raw JSON as the complete inspection truth.
- Preserve the existing MCP inspection history path.
- Decide whether the minimal UI should show seed-fitness details before adding
  broader controls.

### Non-Goals

- no embeddings
- no broad UI dashboard
- no new protocol server
- no persistent cross-cartridge coupling

### Assessment

`mcp-search-seeds` now includes a `selected_flow` window around the selected
semantic object. The inspector renders seed-search payloads with Summary and
Raw JSON tabs, showing the selected seed, score breakdown, breadcrumb,
previous/selected/next source-flow objects, and traversal summary. This makes
seed-fitness evidence intentionally inspectable without replacing raw JSON or
turning the inspector into a polished dashboard.

This phase also added the first formatted interaction stream over MCP
inspection history. `mcp-stream` projects recent command/result captures into
labeled object blocks and preserves Raw JSON beside the formatted stream. The
stream is still history-first: it appends newly seen call ids, pauses autoscroll
while the scrollbar is held, and does not create a message broker, event store,
or interaction cartridge.

## Phase 25: Projection Candidate Flow Visibility

Status: complete in bounded prototype form.

### In Scope

- Apply the same flow-aware inspection pattern to `project-query` projection
  candidates and selected layers.
- Surface selected candidate order, layer breadcrumbs, matched terms, score
  evidence, and compact previews in the existing inspector.
- Preserve the shared `InteractionCapture` as the complete raw truth.

### Non-Goals

- no embeddings
- no graph visualization
- no cartridge merge
- no real MCP protocol server
- no interaction-event cartridge persistence

### Assessment

`project-query` frames now expose `selected_flow`, which shows the selected
candidate plus nearby alternatives from the same layer in ranked order. The
existing inspector Summary tab can now explain not just which layer won, but
which candidate won inside that layer, what nearly won, and what evidence each
visible candidate carries.

This keeps projection choice inspectable without introducing a graph view,
dashboard, merged cartridge, or hidden persistence path.

## Phase 26: Unified Visibility Cockpit

Status: complete in bounded prototype form.

### In Scope

- add one read-only cockpit surface over existing history and score artifacts
- combine latest projection, latest seed flow, latest builder score, latest
  projection score, recent stream, and Raw JSON
- keep the cockpit additive rather than replacing inspector or stream views

### Non-Goals

- no new truth store
- no broad dashboard framework
- no interaction-event cartridge persistence
- no graph visualization
- no real MCP protocol server

### Assessment

`mcp-cockpit` now assembles the current prototype state into one visibility
surface so the builder does not need to reconstruct it from separate tools.
The cockpit remains history-first and read-only.

## Phase 27: Prototype Completion Gate

Status: complete in bounded prototype form.

### In Scope

- re-run bounded ingestion after visibility updates
- refresh builder-task and projection score artifacts
- run full tests, compile checks, forbidden-reference scan, and domain audits
- park docs and journal with the new prototype-complete continuation point

### Non-Goals

- no new subsystem invention during the gate
- no broad UI rewrite
- no embeddings
- no real MCP protocol server
- no cartridge merge

### Assessment

The prototype completion gate is accepted. Current bounded verification is:

- builder-task score: `0.93`, accepted
- projection arbitration score: `0.96`, accepted
- full tests: `99`, passing
- compile check: passing
- forbidden-reference scan: `0` violations
- domain-boundary audits: `src=0`, `tests=0`

## Phase 28: Shared Host State Spine

Status: complete in bounded in-process form.

### In Scope

- add a coordination-owned live host snapshot for the desktop workspace
- normalize `project-query`, `mcp-search-seeds`, `mcp-history-view`,
  `mcp-stream`, and `mcp-cockpit` through one shared dispatcher
- promote `python -m src.app ui` into the primary host workspace
- preserve `--dump-json` as the official headless path
- document the explicit same-process vs separate-process rule

### Non-Goals

- no FastAPI
- no websocket transport
- no Docker / WASM architecture pivot
- no real MCP server
- no same-instance cross-process control yet

### Assessment

The app now has a real shared host-state spine. The durable truth remains the
existing SQLite history and score artifacts, but the UI no longer rebuilds its
world as an isolated launcher. It reads and updates one coordination-owned live
host snapshot containing recent interactions, active projection, active seed
flow, score summaries, and raw payload cache.

This is the right-order version of UI/MCP unification for the current stage:
same command model, same dispatcher, same live host state, multiple views.
Literal cross-process co-driving of an already-open window is intentionally
deferred to the next tranche.

## Deferred Advanced Work

- FFN relation scorer
- spectral graph methods
- TDA
- information bottleneck compression
- distributed canonical anchors
- deterministic replay
- attestation
- rich visualization
- multi-agent coordination runtime

## Immediate Post-Prototype Work

- Decide whether to add a local host bridge so separate commands can target an
  already-open UI host.
- Decide retention/pruning policy for MCP inspection history.
- Decide whether the cockpit and stream stay compact or gain filtering.
- Decide which additional UI actions should join the shared command spine.
- Decide when command/result SemanticObject projections should become persisted
  cartridge truth.
- Decide when the bounded project-document set should expand.

## Backlog Seeds

- Decide exact `semantic_id` hash envelope.
- Decide minimal relation predicate registry for prototype one.
- Decide how semantic evolution creates versions.
- Decide first execution artifact shape.
- Decide which `.dev-tools` checks become mandatory phase gates.
- Define the first search-scored traversal tuning controls.

