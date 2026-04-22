# Strangler Plan

_Status: Active migration doctrine, shared command spine pilot parked complete_

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

Status: next tranche.

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

- Score whether traversal search improves real builder-task usefulness.
- Score whether the English lexical baseline helps layered retrieval.
- Score the context projection layer and decide whether it should become the
  next MCP-shaped registered tool candidate.
- Keep history-aware inspector attached to show selected seeds and traversal
  outcomes.
- Decide whether search tuning is enough or whether a second registered tool is
  justified.

## Backlog Seeds

- Decide exact `semantic_id` hash envelope.
- Decide minimal relation predicate registry for prototype one.
- Decide how semantic evolution creates versions.
- Decide first execution artifact shape.
- Decide which `.dev-tools` checks become mandatory phase gates.
- Define the first search-scored traversal tuning controls.

