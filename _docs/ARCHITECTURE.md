# nGraphMANIFOLD Architecture Doctrine

_Status: Active doctrine, local host bridge parked complete_

This document normalizes the conceptual build plan into an implementation-facing
architecture doctrine. It is subordinate to `builder_constraint_contract.md` and
inherits `semantic_os_conceptual_build_plan.md` as the conceptual northstar.

## Authority Stack

1. `builder_constraint_contract.md` - project constitution and build discipline.
2. `semantic_os_conceptual_build_plan.md` - conceptual architecture contract.
3. `ARCHITECTURE.md` - active normalized architecture doctrine.
4. `STRANGLER_PLAN.md` - phased migration and prototype route.
5. `SOURCE_PROVENANCE.md` - reference-source and borrowing ledger.
6. `TOOLS.md` - development tool surface and usage policy.
7. App journal - append-only continuity, decisions, backlog, and phase history.

When documents conflict, the contract wins. When the concept plan and this file
appear to conflict, preserve the concept plan and revise this file.

Companion handoff note:

- `THOUGHTS_FOR_NEXT_SESSION.md` is a non-authoritative research and reasoning
  surface for the next work session. It captures the current interpretation of
  English lexical, Python docs, project-local priors, the layered probe, and the
  expected context projection tranche.

## Northstar

nGraphMANIFOLD is a semantic operating substrate under construction. Its job is
to represent, transform, persist, analyze, coordinate, and eventually execute
meaning as a first-class computational substrate.

The system shall not collapse into a conventional retrieval stack, embedding
pipeline, graph database, compiler framework, or app-shell bundle. Those may be
mechanisms, but none of them owns the architecture.

## Canonical Semantic Object Model

The primary object model is a hybrid semantic object:

`SemanticObject = content-grounded unit + explicit surfaces + typed relations + provenance + derived views`

This is the declared primary substrate for prototype work. Vectors, graph rows,
database chunks, traversal artifacts, and execution plans are derived views or
operational projections unless a later doctrine explicitly revises this.

### Semantic Identity

Semantic identity is content-grounded and structure-aware, not path-grounded.

A semantic object has at least two identities:

- `semantic_id`: stable content/structure identity for the normalized unit.
- `occurrence_id`: source occurrence identity for one appearance of that unit in
  a source, context, document, corpus, or execution trace.

Human labels, file paths, UI names, and local variable names are presentation or
source context. They may aid provenance and display, but they do not define
canonical semantic identity.

Phase 2 identity envelope:

- `semantic_id` is `sem:v1:<sha256>` over canonical JSON containing object kind,
  normalized content, surface data, and relation summaries, excluding occurrence
  and provenance.
- `occurrence_id` is `occ:v1:<sha256>` over canonical JSON containing
  `semantic_id`, source reference, source span, and local context.
- Canonical JSON uses sorted keys, compact separators, and recursive
  normalization of mappings, sequences, scalar values, and path-like strings.
- This policy is intentionally local and versioned. Later persistence or
  coordination tranches may add stronger Merkle envelopes without changing the
  rule that identity is not a file path.

### Required Object Surfaces

Prototype semantic objects should preserve these surfaces when available:

- `verbatim`: source text or original content evidence.
- `structural`: containment, position, hierarchy, and source shape.
- `grammatical`: syntax, language, node kind, scope, declarations, and grammar.
- `statistical`: token counts, locality windows, frequencies, and numeric cues.
- `semantic`: embedding, symbolic, relation, or meaning-bearing features.
- `provenance`: source, derivation lineage, transform status, and confidence.

The surface list is intentionally close to the HyperHunk idea from the parts
bin, but it belongs here as nGraphMANIFOLD doctrine, not as an imported app
boundary.

### Relations

Relations are explicit typed objects. Important relationships must not exist
only as opaque vector proximity.

Prototype relation classes include:

- `contains` / `member_of`
- `precedes` / `follows`
- `references`
- `derives_from`
- `transforms_to`
- `similar_to`
- `supports`
- `contradicts`
- `executes_as`

Every relation should preserve source and confidence metadata when practical.

### Derived Views

Derived views must remain honest about derivation:

- vector embeddings annotate semantic objects, but do not replace identity.
- graph nodes and edges project semantic objects and relations.
- persistence rows store and index semantic objects.
- traversal artifacts gather and rank evidence over persisted objects.
- execution plans are traceable transformations from semantic intent.

## Canonical Layers

The implementation shall preserve the six conceptual layers from the build
plan. These are architectural ownership layers, not necessarily top-level
folders.

### Representation Layer

Owns `SemanticObject`, identity, surfaces, relation contracts, and object-level
serialization. No upper layer may redefine what a semantic object is.

Prototype owner: `src/core/representation/` after scaffold creation.

### Transformation Layer

Owns conversion into, out of, and across semantic object forms. Every
transformation must declare one status:

- identity-preserving
- reversibly mappable
- bounded-loss
- interpretive / heuristic

Prototype owner: `src/core/transformation/`.

Phase 4 intake adapter:

- Reads UTF-8 local text sources into `SourceDocument`.
- Splits small text/Markdown-like documents into blank-line-delimited
  `SourceBlock` units with line spans.
- Emits canonical `SemanticObject` instances with verbatim, structural,
  grammatical, statistical, and empty semantic surfaces.
- Records `IDENTITY_PRESERVING` provenance through `ProvenanceRecord`.
- Can persist emitted objects directly into a `SemanticCartridge`.

This is a minimal source-to-object adapter, not a full Splitter migration,
TreeSitter parser, broad corpus ingestor, or embedding pipeline.

### Persistence Layer

Owns durable storage, schema, cartridge boundaries, content addressing,
lineage, indexes, and migration/version behavior.

Prototype owner: `src/core/persistence/`.

Phase 3 persistence cartridge:

- SQLite-backed local cartridge under persistence ownership.
- `cartridge_manifest` stores schema version, readiness flag, notes, and counts.
- `semantic_objects` stores canonical object JSON by `semantic_id`.
- `semantic_occurrences` stores occurrence projections by `occurrence_id`.
- `semantic_relations` stores queryable relation projections by predicate,
  source, and target.
- `provenance_records` stores derivation and transform-status projections.
- `derived_vector_views` and `derived_graph_views` reserve explicit derived-view
  surfaces without claiming mature embedding or graph behavior yet.
- Schema version is `1` / `1.0.0`.

This is a persistence spine, not full event sourcing, search, graph analytics,
or a TripartiteDataSTORE copy.

### Analysis Layer

Owns traversal, scoring, pattern detection, search, graph walks, spectral or
topological lenses, and evidence assembly.

Prototype owner: `src/core/analysis/`.

Phase 5 relation enrichment:

- Produces first-pass explicit relations over existing semantic objects.
- Emits source-membership and heading-membership structural relations.
- Emits `precedes` / `follows` adjacency relations between consecutive source
  blocks.
- Emits `references` relations from simple Markdown link syntax.
- Adds traceable metadata containing enrichment pass, version, basis, and score
  components.
- Persists enriched relations as cartridge projections attached to existing
  `semantic_id` values rather than mutating canonical object identity.

This is a bounded enrichment pass, not a learned scorer, graph traversal engine,
advanced spectral/TDA lens, or imported Emitter nucleus.

Phase 6 traversal artifact:

- Traverses persisted cartridge relation projections from a seed
  `semantic_id`.
- Performs readiness and seed checks before walking.
- Records outgoing and incoming relation steps with direction, depth, source,
  target reference, reached semantic object, relation score, cumulative score,
  and relation metadata.
- Preserves non-semantic targets, such as document anchors or external links,
  in the trace without pretending they are semantic objects.
- Produces a deterministic `TraversalReport` artifact ID from the walk inputs
  and trace.

This is a traceable analysis artifact, not a full NodeWALKER transplant,
mutation agent, patch approval flow, advanced graph algorithm, or UI surface.

### Coordination Layer

Owns canonical anchors, divergence checks, registry surfaces, replay/attestation
concepts, and multi-agent alignment mechanics.

Prototype owner: `src/core/coordination/`, initially light and mostly doctrinal.

Phase 8 thin MCP usefulness seam:

- Defines builder-facing capability descriptors for the prototype spine.
- Declares input and output shapes that a future MCP wrapper can expose.
- Defines usefulness scoring dimensions: task fit, evidence quality,
  actionability, friction reduction, and repeatability.
- Provides aggregate scoring and an acceptance threshold for tuning.
- Remains a local coordination contract only.

This is not a network server, full MCP protocol implementation, external
runtime dependency, autonomous agent loop, or hidden reference-bin coupling.

Prototype tuning and scoring:

- Defines repeatable builder-task fixtures under `src/core/coordination/`.
- Runs the completed spine from source intake through relation enrichment,
  persistence, traversal, semantic intent, execution plan, execution result,
  and feedback persistence.
- Scores every current MCP seam capability descriptor against task fit,
  evidence quality, actionability, friction reduction, and repeatability.
- Recommends `analysis.traverse_cartridge` as the first local MCP adapter pilot
  when all default fixtures pass acceptance.

This is a scoring harness for builder usefulness, not a protocol transport,
server runtime, broad benchmark suite, or agent autonomy layer.

Local MCP adapter and raw inspector:

- Wraps `analysis.traverse_cartridge` in a local MCP-shaped adapter.
- Captures the raw capability descriptor, seam manifest, request, traversal
  response, usefulness report, and notes as a single inspection payload.
- Exposes that payload through a minimal raw JSON panel and a headless JSON
  command.

This is a visibility and adapter-shape pilot, not a full MCP server, protocol
transport, persistent history store, polished UI, or host-app integration.

MCP tool registration candidate:

- Defines a project-owned registry for MCP-facing tool candidates.
- Registers `ngraph.analysis.traverse_cartridge` as the first serializable tool
  candidate over the traversal adapter.
- Declares JSON-like input and output schemas for the registered call.
- Returns a call envelope containing tool metadata, call status, and the raw
  inspection capture.

This is still not a protocol server, host tool installation, external MCP SDK
dependency, or network transport.

Persistent MCP inspection history:

- Stores registered local MCP tool calls in a coordination-owned SQLite history
  database under `data/mcp_inspection/`.
- Preserves raw call/capture JSON while indexing tool name, capability, capture
  time, status, and aggregate score.
- Allows the raw inspector to show recent persisted history rather than only a
  single ephemeral payload.

This is a builder-facing observability surface, not semantic cartridge truth,
not a broad telemetry platform, and not a polished analytics UI.

Project document ingestion candidate:

- Ingests a bounded curated set of project documents into a project-owned
  semantic cartridge.
- Uses the existing transformation, relation enrichment, persistence,
  registered traversal, and inspection-history path.
- Selects a project-status seed so builder continuation context becomes visible
  through the MCP-shaped surface.

This is not a repo-wide scanner, arbitrary file ingestor, search engine,
embedding pipeline, or document-retention policy.

Real builder-task scoring:

- Defines continuation-oriented builder tasks against ingested project docs.
- Runs each task through the project-document ingestion and registered traversal
  path with task-specific seed hints.
- Records each tool call into inspection history.
- Produces a score artifact under `data/mcp_inspection/`.

This is a usefulness harness, not a complete benchmark suite, learned evaluator,
or substitute for review.

History-aware MCP inspector:

- Builds compact summaries from persisted MCP inspection history.
- Maps scored builder tasks back to recent call ids when the score artifact is
  available.
- Adds a tabbed Summary / Raw JSON inspector view.
- Provides an interaction stream projection over the same history, showing
  recent command/result pairs as formatted labeled object blocks with raw JSON
  preserved.
- Keeps the stream as an inspection projection: it appends newly seen call ids,
  pauses autoscroll while the scrollbar is held, and does not become a message
  broker, event store, or semantic cartridge.

This is still a minimal builder observability surface, not a dashboard,
visual analytics system, or replacement for raw evidence.

Projection candidate flow visibility:

- Extends `project-query` frames with `selected_flow`.
- Preserves the selected candidate plus nearby alternatives from the same layer.
- Carries rank, source reference, matched terms, evidence, breadcrumb, heading
  trail, and compact preview.
- Feeds the same selected-flow evidence into the inspector Summary tab, the
  interaction stream payload, and the unified cockpit payload.

This is ordered inspection evidence for projection choice, not a graph view,
not a merged cartridge, and not semantic truth on its own.

Unified visibility cockpit:

- Adds a read-only `mcp-cockpit` projection over existing history and score
  artifacts.
- Combines the latest builder-task score, latest projection score, latest
  project-query projection, latest builder-seed flow, and recent interaction
  stream.
- Preserves Raw JSON beside the formatted cockpit surface.
- Keeps history and score artifacts as the sources of truth; the cockpit is a
  projection only.

This is an immersion surface for human inspection, not a new state owner,
message broker, event store, or polished dashboard platform.

Shared host state spine:

- Adds `src/core/coordination/host_workspace.py` as the coordination-owned live
  host-state owner for the desktop workspace.
- Builds one current host snapshot from durable history, score artifacts, and a
  bounded raw-payload cache.
- Normalizes `project-query`, `mcp-search-seeds`, `mcp-history-view`,
  `mcp-stream`, and `mcp-cockpit` through one in-process dispatcher.
- Promotes `src/ui/gui_main.py` from a thin query launcher into the primary
  desktop host workspace.
- Preserves `--dump-json` as the headless path.
- Provides the stable command/state center a later bridge can safely target.

This is the right-order unification step for the current stage: shared
command/state, not shared widget ownership and not transport-heavy
architecture.

Local host bridge:

- Adds `src/core/coordination/host_bridge.py` as a project-owned local bridge
  over the shared host dispatcher.
- Publishes a live host session under `data/host_bridge/session.json` while the
  Tk host is open.
- Uses project-owned request/response folders under `data/host_bridge/`.
- Allows approved separate-process commands to target the already-open host
  without introducing a network server.
- Reuses canonical `CommandEnvelope` payloads instead of inventing a second
  command language.
- Keeps the bridge subordinate to the command/state spine rather than making
  transport the architecture.

Traversal seed search and selection:

- Reuses the bounded project-document cartridge.
- Searches persisted semantic objects with deterministic text ranking.
- Selects the top seed for the registered traversal tool.
- Records the selected traversal call in MCP inspection history.
- Replaces stale objects for re-ingested project-document sources.

This is a project-owned analysis/coordination helper, not embeddings, a
full-text engine, a repo-wide scan, or a second registered tool candidate.

English lexical baseline:

- Streams `assets/_corpus_examples/dictionary_alpha_arrays.json`.
- Preserves headword and raw definition as the authoritative lexical record.
- Conservatively infers numbered senses, domain labels, cross references,
  derived forms, and usage-example candidates.
- Writes a dedicated `data/cartridges/base_english_lexicon.sqlite3` cartridge.
- Keeps lexical truth separate from project-document truth.

The alpha-array source is treated as reliable for `headword -> definition_raw`.
All inferred fields are parser candidates for prototype use, not authoritative
dictionary schema.

Python docs projection corpus:

- Reads `assets/_corpus_examples/python-3.11.15-docs-text` as a project-owned
  official Python documentation text corpus.
- Defaults to a bounded projection set: `library/functions.txt`,
  `reference/compound_stmts.txt`, `reference/simple_stmts.txt`, and
  `tutorial/controlflow.txt`.
- Extracts typed documentation units: sections, API signatures, prose
  descriptions, doctest examples, parseable code examples, and grammar rules.
- Defaults to projection anchors, signatures, examples, doctests, and grammar;
  full-tree and broad prose descriptions are available only through explicit
  build options.
- Uses Python's standard-library `ast` only after candidate Python snippets have
  been isolated from the docs text.
- Writes a dedicated `data/cartridges/python_docs.sqlite3` cartridge.
- Keeps Python documentation/code structure separate from project-document and
  English lexical truth.

This is a projection lens for query rebinding, not dictionary search, corpus
search, a generic docs search engine, a custom Python parser, an embedding
pipeline, a Docling runtime dependency, or a `.dev-tools` runtime dependency.

Layered probe note:

- The same raw term can now be inspected through separate English, Python, and
  project-local cartridges without merging their truth layers.
- A probe over `object` produced distinct anchors: English lexical entry,
  Python docs code/API usage, and project-local `SemanticObject` doctrine.
- A probe over `for element in iterable return False` resolved strongly to
  Python docs examples while producing only broad lexical/project noise.
- This supported the context-stack theory and led to the first explicit
  projection frame. Layer arbitration remains deterministic and provisional.

Context projection / rebinding layer:

- Adds `src/core/coordination/context_projection.py` as the first explicit
  context projection frame.
- Projects one raw query through separated layers:
  `english_lexical_prior`, `python_docs_projection`, and `project_local_docs`.
- Preserves each layer's candidate evidence, matched terms, source reference,
  heading context, score, and caution notes.
- Selects a provisional layer/candidate by deterministic scoring while stating
  that this is not final semantic grounding or learned disambiguation.
- Exposes the frame through `python -m src.app project-query --query "..."`
  with optional `--dump-json`.

This is the first implementation of the "dipping" idea. It remains a
coordination-layer prototype, not embeddings, full-text search, a merged
cartridge, a polished UI, or a registered external MCP server.

The next coordination target is projection scoring and MCP inspection: record
projection calls in inspection history, expose the frame through the inspector,
and decide whether `project-query` should become the next MCP-shaped registered
tool candidate.

Shared command spine:

- Adds `src/core/coordination/interaction_spine.py` as the first common
  command/result envelope path for CLI, future UI buttons, and future MCP
  protocol wrappers.
- Defines `CommandEnvelope`, `ToolResultEnvelope`, and `InteractionCapture`.
- Routes `project-query` through this shared path and records
  `ngraph.project.query` in MCP inspection history.
- Registers `ngraph.project.query` as an MCP-shaped local tool candidate beside
  `ngraph.analysis.traverse_cartridge`.
- Provides adapters that project command/result envelopes into `SemanticObject`
  instances with verbatim, structural, grammatical, statistical, semantic, and
  provenance surfaces.

This is history-first interaction persistence. It is not a message broker,
event-sourcing platform, polished UI button layer, real MCP server, or semantic
cartridge persistence for every interaction.

UI command spine pilot:

- Replaces the scaffold UI placeholder with a minimal `python -m src.app ui`
  surface.
- Adds one project-query control that submits the same command envelope shape as
  CLI and MCP-shaped calls.
- Records UI-originated `ngraph.project.query` captures in the existing MCP
  inspection history with `actor="human"` and `source_surface="ui"`.
- Shows a current history summary and the latest raw `InteractionCapture`
  payload through the same Summary / Raw JSON pattern as the inspector.

This is a human-facing command surface, not a new source of truth, dashboard,
semantic persistence path, or broad UI layer.

Layer arbitration scoring:

- Adds `project-query-score` as a coordination-owned scoring command.
- Runs bounded fixtures for English lexical anchoring, Python/context rebinding,
  and project-local doctrine lookup.
- Routes each fixture through the same `ngraph.project.query`
  `CommandEnvelope` / `ToolResultEnvelope` / `InteractionCapture` path.
- Records fixture calls in MCP inspection history with
  `source_surface="scoring"`.
- Writes the latest scoring artifact to
  `data/mcp_inspection/context_projection_scores.json`.

This makes selected-layer behavior measurable before adding broader UI display,
embeddings, merged cartridges, or learned disambiguation.

Seed-fitness scoring:

- Owns traversal start-point fitness in `src/core/coordination/seed_fitness.py`.
- Provides the shared deterministic scorer used by both `mcp-search-seeds` and
  `mcp-score-tasks`.
- Scores lexical match, heading/section affinity, document-role fit,
  continuation-marker proximity, operator-command proximity, expected source
  fit, kind, brevity, and stable fallback fields.
- Keeps source-path ordering as a final deterministic fallback rather than a
  meaningful authority signal.
- Does not use embeddings, vector similarity, context projection state,
  persistent cross-cartridge links, or merged priors.

Seed flow inspector visibility:

- Extends seed-search results with a `selected_flow` window containing the
  previous, selected, and next source objects around the chosen seed when that
  source order is available.
- Renders seed-search payloads through the existing Summary / Raw JSON
  inspector pattern.
- Shows selected-seed source, kind, score, matched terms, score breakdown,
  breadcrumb, source-flow previews, and traversal counts.
- Treats flow visibility as inspection evidence only, not graph visualization,
  semantic truth, or a replacement for raw payloads.

Formatted interaction stream visibility:

- Projects persisted MCP inspection records into readable command/result
  objects.
- Displays query, result, selected layer, selected kind, score, preview,
  source, call id, and aggregate score in a user-facing scroll surface.
- Preserves Raw JSON as the source of complete evidence.
- Uses incremental append and scrollbar-hold autoscroll pause to keep human
  inspection stable while new records arrive.
- Does not persist interaction events into semantic cartridges yet.

### Execution Layer

Owns conversion from semantic structures into inspectable actions and feedback.
This layer may be skeletal in early prototypes, but it must remain visible.

Prototype owner: `src/core/execution/`, initially a traceable execution-intent
interface rather than broad automation.

Phase 7 minimal execution pathway:

- Defines `SemanticIntent`, `ExecutionPlan`, and `ExecutionResult` records.
- Supports bounded `report_generation` and `no_op` actions only.
- Produces an `execution_result` semantic object when execution completes.
- Records `executes_as` and `derives_from` feedback relations from the result
  object back to its plan and originating semantic objects.
- Persists the result through the existing semantic cartridge rather than
  introducing a new execution database.

This closes the first prototype spine. It is not an autonomous action system,
trusted execution implementation, distributed consensus mechanism, or broad
automation layer.

## Runtime Composition

When the application scaffold exists, `src/app.py` is the composition root and
canonical app-state authority. It shall bootstrap configuration, logging,
runtime graph or service boundaries, and lifecycle monitoring.

Core implementation belongs under `src/core/`. UI behavior belongs under
`src/ui/`. UI may inspect and trigger core services, but it must not own
semantic identity, persistence, analysis, or transformation truth.

Current desktop-host rule:

- the UI owns presentation
- coordination owns the host snapshot and command dispatcher
- durable truth remains the history store and score artifacts
- separate CLI invocations are not yet routed into a running UI instance

## Prototype Spine

The first useful prototype should establish this minimal flow:

1. Source content enters the system.
2. Transformation produces canonical semantic objects.
3. Existing semantic objects receive explicit relation projections and
   provenance without hidden relation inference.
4. Persistence stores objects, relations, derived views, and lineage.
5. Analysis traverses persisted objects with traceable scoring.
6. Execution layer records at least one inspectable semantic intent path, even
   if the executed action is initially a no-op or report generation.

This keeps all six layers alive without pretending each is mature.

## Core Versus Extension

### Irreducible Core

- canonical semantic object model
- semantic identity separate from occurrence and presentation
- explicit relation structure
- transformation-status discipline
- durable persistence model
- provenance and lineage
- traversal/analysis over persisted objects
- visible execution pathway

### Deferred Extensions

- learned FFN nucleus or equivalent learned relation scorer
- full distributed coordination
- trusted execution and attestation
- topological data analysis
- advanced spectral graph workflows beyond basic relation scoring
- information bottleneck optimization
- rich UI and visualization
- broad multi-language production ingestion

Deferral is not deletion. Deferred extensions remain part of the long-range
doctrine when they serve the northstar.

## Parts-Bin Fit

Existing parts are reference foundations only:

- `_BDNeuralTranslationSUITE/_BDHyperNodeSPLITTER` informs semantic-object
  intake and surface population.
- `_BDNeuralTranslationSUITE/_BDHyperNeuronEMITTER` informs relation scoring,
  enrichment, graph assembly, and training/inference boundaries.
- `_TripartiteDataSTORE` informs durable cartridge persistence.
- `_NodeWALKER` informs traversal, scoring, decision memory, and analysis over
  cartridges.
- `.dev-tools/_project-authority` informs development workflow, scanning,
  patching, scaffolding, journal continuity, and contract-aware build support.

None of these may become runtime dependencies by path. Any borrowed logic must
be re-homed, owned, tested, and recorded in `SOURCE_PROVENANCE.md` and the app
journal.

## Explicit Non-Goals For The Next Tranche

- No wholesale copying from `.parts`.
- No runtime imports from `.parts` or `.dev-tools`.
- No UI-first development.
- No full MCP server before the local adapter shape and inspection payload prove
  useful.
- No host MCP tool installation before the project-owned registry shape is
  stable.
- No broad project ingestion before the history path can preserve what the tool
  saw.
- No repo-wide scan before selected-doc usefulness is scored.
- No second tool candidate before traversal/history usefulness is readable by
  the builder.
- No broader tool expansion before seed discovery is scored for usefulness.
- No lexical baseline merge into project-document truth before layered retrieval
  is scored.
- No Python docs projection merge into project-document or lexical truth before
  the rebinding layer is scored.
- No learned FFN or advanced math layer before the object/persistence spine is
  stable.
- No claim of full event sourcing, decentralized consensus, or semantic OS
  completeness before the required mechanics exist.
- No app shell that hides an undefined object model underneath.

## Open Doctrine Questions

These questions are intentionally preserved rather than hand-waved:

- What exact canonical serialization defines `semantic_id`?
- Which relation predicates are core in prototype one?
- How should mutable semantic evolution version identity and occurrence?
- What is the first minimal execution action that preserves traceability?
- Which `.dev-tools` audits should become mandatory phase gates?
- What exact local adapter payload should expose `analysis.traverse_cartridge`
  most usefully through the MCP seam?
- Should raw MCP inspection history persist across runs, or remain ephemeral
  until true tool registration exists?
- What minimum persistent inspection history is needed for registered tool
  calls without turning the inspector into a UI-first project?
- Which real project documents should become the first safe ingestion target
  for MCP-facing traversal?
- Which real builder tasks should be scored first against ingested docs?
- What minimum history-aware inspector features make the real-task evidence
  faster to use?
- What simple search/seed-selection path best improves traversal usefulness
  without introducing embeddings yet?
- How much does deterministic seed search improve real builder-task scores?
- Does English lexical grounding improve retrieval, or does it distract from
  current project truth?

