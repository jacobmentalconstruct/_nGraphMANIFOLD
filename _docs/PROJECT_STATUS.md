# Project Status

_Status: Active parking surface, visible host lifecycle hardening parked_

This file is the quick continuation marker between tranches. The app journal
remains the authoritative phase ledger.

## Current Park Point

Just-completed tranche:

- Visible Host Lifecycle Hardening

Status:

- opened after live monitor lifecycle checks showed two host-visible gaps:
  bridged seed search could outgrow the flat bridge timeout, and the Tool
  Registry panel text was not rendering the current registry payload shape
- bridged `mcp-search-seeds` now uses a medium command-aware timeout policy
- Status panel text now exposes `seed_search_bridge_timeout_ms`
- Tool Registry panel text now reads both `tools` and legacy `registrations`
  payloads
- bridge session reads no longer delete stale manifests passively; cleanup is
  still handled by explicit maintenance/retention policy
- bridge request processing refreshes the owner heartbeat before and after
  dispatch so long-running visible commands can be followed immediately by
  another bridged command
- visible monitor smoke passed for seed search, immediate tool registry
  follow-up, seed panel readback, tools panel readback, and status panel
  readback
- full test suite is green at `138` tests
- no embeddings, vector views, cartridge rewrite, global event bus, or hidden
  app-state ingestion were introduced

Started:

- 2026-04-30

Parked:

- 2026-04-30

Recently parked tranche:

- Lens-Guided Companion Evidence Evaluation (2026-04-30)
- Scored Human-Facing Inspection Usefulness Fixture (2026-04-30)
- Protected Baseline And Semantic Docking Doctrine (2026-04-30)
- Visibility / Introspection Boundary Realignment (2026-04-28)
- Disambiguation Bias Repair (2026-04-25)
- Bridge Transport And Profile Discipline (2026-04-23 / 2026-04-24)

## What Shifted

The important shift is phase-level, not architectural panic:

```text
before:
  prove the bounded prototype can exist coherently
  prove visibility can keep up with the build
  prove the live host can be targeted without turning transport into the app

now:
  harden the working prototype so success does not become clutter
  define how much history should remain active
  define how the bridge stays bounded
  define what each visibility surface owns
```

The next danger is no longer "nothing works yet." The next danger is
structural drift caused by accumulating meaningful but unmanaged history,
bridge state, and overlapping visibility surfaces.

Recent hardening slices now address that directly:

- human-facing inspection usefulness now has a scored fixture with accepted
  projection, seed, promotion, status/tool, and score-surface visibility
- visible host lifecycle hardening now makes bridged seed search a medium
  timeout command and makes Tool Registry panel text match the current payload
  shape
- a project-owned retrieval/evidence side harness family now lives under
  `src/core/coordination/` and is callable from `src.app`
- outside retrieval evaluation now exists without changing the canonical
  deterministic scorer
- lens-guided bag evaluation now exists without changing cartridge truth or
  current runtime doctrine
- adaptive deterministic weight rotation was tested and did not beat the
  current baseline scorer
- baseline seed plus auto-lens companion bag did improve supporting evidence
  coverage without degrading baseline top choice
- the retrieval conclusion is now bounded:
  keep the deterministic baseline as primary chooser
  and treat the lens bag as companion context rather than replacement search
- protected deterministic baseline doctrine now makes the three current
  cartridges canonical local evidence before any embedding work begins
- semantic docking is now explicitly subordinate to baseline preservation and
  must use `derived_vector_views` rather than redefining identity or graph truth
- MCP inspection history uses a rolling-trace policy
- old unpinned interaction rows are pruned automatically
- score-referenced call ids are pinned as durable evidence
- stale bridge request/response/session files are cleaned conservatively
- stale-looking bridge sessions are no longer deleted by passive readers, so
  the visible host owner can recover its own manifest after a long command
- the host, stream, cockpit, and history surfaces now expose retention state
- stream and cockpit surfaces now support bounded tool/layer filtering
- operator-facing promotion controls can now pin or unpin the active or named
  interaction record without changing semantic cartridge truth
- host workspace now acts as the default visible operator surface for stream,
  cockpit, and history views, with detached popup windows becoming explicit
  opt-ins
- visible host-owned commands now use a short attach grace period so a freshly
  opened workspace is given time to publish its live session before any popup
  fallback is considered
- the host now exposes active/named/all panel readback through
  `mcp-read-panels`
- host workspace now includes Status and Tool Registry tabs as first-class
  surfaces
- `status`, `mcp-tools`, `mcp-score-tasks`, and `project-query-score` now
  route through the shared host dispatcher
- a bounded tuning pass over the current corpus remains stable at builder-task
  score `0.93` and projection arbitration score `0.96`
- bridged commands now use command-aware timeout defaults instead of one flat
  five-second wait for every tool
- builder-task scoring now defaults to a heavy bridge timeout policy and
  projection and seed-search commands now default to a medium bridge timeout
  policy
- `--bridge-timeout-ms` remains a caller-owned override rather than being
  removed from the CLI surface
- bridged JSON payloads now expose additive `_bridge` metadata so timeout
  behavior is inspectable instead of implicit
- status surfaces now expose a machine-readable `bridge_timeout_policy`
  manifest for the current host bridge defaults
- operator-promoted durable evidence now supports bounded history-side metadata:
  label, reason, and note
- promotion metadata is visible in history summaries, stream summaries, cockpit
  stream excerpts, host workspace panels, and raw inspection payloads
- `mcp-promote-call` now accepts `--label`, `--reason`, and `--note`
- the host workspace now exposes compact label/reason/note fields for active
  promotion without turning the operator surface into a new truth store
- status surfaces now expose bridge transport kind, live bridge runtime state,
  and the bounded project-doc profile manifest
- builder-task and projection scoring now emit explicit `elapsed_ms`
- builder-task scoring now emits `corpus_object_count` and
  `corpus_relation_count`
- switching between `expanded` and `core` project-doc profiles now purges
  out-of-profile docs from the project-doc cartridge instead of quietly
  carrying them forward
- current measured profile comparison is now inspectable:
  - `core`: `605` objects / `2251` relations / `0.93` accepted / `60093 ms`
  - `expanded`: `879` objects / `3288` relations / `0.93` accepted / `84682 ms`
- journal continuity now has a clearer forward rule:
  phase parks should preserve compact lessons learned, key decisions, evidence
  used, and rejected alternatives when a tranche teaches something important
- disambiguation falsifier panel now exists at `tests/test_disambiguation_panel.py`
  with ten pre-committed (query, expected_layer) assertions, passing 10/10
- projection scoring rebalanced inside `src/core/coordination/context_projection.py`
  to suppress headword-match dominance for project/python frame hints, weaken
  english single-term bias when the term is a frame hint, weaken python boost
  for ambiguous (project+python) terms, and climb project boost for short
  queries when at least one project hint is present
- the working assumption that the substrate's foundation is sound and the
  observed bend is localized to projection scoring has been confirmed by repair
- "stable" now means falsifier-backed for the disambiguation claim, not only
  acceptable on the prior 0.93 / 0.96 score floor
- a contract amendment motion was drafted to distinguish architectural locks
  from substantive non-goals; the motion is awaiting user approval and has
  no active case after the disambiguation repair landed within existing locks
- the visibility/introspection boundary is now explicit: runtime monitoring
  and logging records may be normalized later for app introspection, but only as
  gated inspection evidence, never as hidden substrate memory or semantic
  cartridge truth

## Stable Prototype State

The current stable prototype is now defined as:

```text
a bounded, inspectable, score-accepted semantic substrate prototype
with:
  - canonical semantic objects
  - explicit relations and provenance
  - SQLite cartridge persistence
  - traversal and seed selection
  - separated English / Python / project-local priors
  - deterministic context projection
  - shared command/result envelopes
  - persistent inspection history
  - readable stream / cockpit / host workspace visibility
  - scored human-facing inspection usefulness
  - local same-instance host targeting through a bounded file-backed bridge
```

This is a real prototype substrate, not yet the full semantic operating system.

## What We Just Completed

Completed and now parked:

- shared host state owner in
  `src/core/coordination/host_workspace.py`
- shared dispatcher for:
  `project-query`, `mcp-search-seeds`, `mcp-history-view`, `mcp-stream`,
  `mcp-cockpit`, `status`, `mcp-tools`, `mcp-score-tasks`,
  `project-query-score`
- primary desktop host workspace via `python -m src.app ui`
- local host bridge in `src/core/coordination/host_bridge.py`
- bridge session manifest and request/response roots under `data/host_bridge/`
- opt-in bridge routing for:
  - `python -m src.app project-query --use-host-bridge`
  - `python -m src.app mcp-search-seeds --use-host-bridge`
- host panel readback via:
  - `python -m src.app mcp-read-panels --dump-json --use-host-bridge`
- bounded same-instance cross-process control through canonical
  `CommandEnvelope` payloads

## What This Prototype Currently Proves

It currently proves that we can:

- ingest bounded corpora into project-owned cartridges
- preserve semantic objects, occurrences, relations, and provenance
- traverse and inspect those persisted objects
- score builder-facing usefulness over repeatable fixtures and real project docs
- project queries through separated priors instead of collapsing them together
- make query/result life cycles visible enough for real inspection
- let separate processes target an already-open host without promoting network
  transport into the architecture

It does not yet prove:

- final semantic grounding
- learned disambiguation
- broad corpus ingestion at scale
- production-grade transport or distributed coordination
- final execution-layer maturity

## Proposed Next Tranche

Current active tranche family:

- Post-Prototype Hardening And Expansion

Immediate focus inside that family:

- choose the next bounded slice after the accepted visibility fixture
- preserve the now-explicit answer on bridge/profile discipline:
  - keep the bridge file-backed for the next band
  - keep `core` and `expanded`
  - do not add thinner IPC or another profile without new measured need
- preserve the now-explicit answer on the disambiguation claim:
  - the falsifier panel is the acceptance gate for the central claim
  - localized scoring rebalance is the first move when bias re-emerges
  - architectural locks remain in force; the gate-lift motion has no active case
- keep the interaction truth boundary inspection-only unless a future tranche
  explicitly reopens it
- carry the visibility/introspection boundary into the next slice:
  - compare what the operator and builder agent can both inspect
  - use existing shared surfaces first
  - do not implement a global runtime event/logging spine inside this tranche
  - keep monitoring/app-state evidence gated, explicit, and outside cartridges
- preserve the app-owned side retrieval/evidence harnesses as reusable
  inspection surfaces only:
  - do not merge them into main scoring doctrine casually
  - do not reopen semantic-first or weight-rotation replacement paths first
  - if retrieval work resumes later, start from baseline plus companion bag

Recommended next tranche candidates:

- Traversal Seed Selection Falsifier Panel
- Baseline Manifest Helper before any persisted vector-view pilot

What that means:

- if continuing claim discipline, add a second pre-committed falsifier panel
  for a different substrate claim, with traversal seed selection still the
  probable candidate
- if opening the semantic-docking/vector path, implement the baseline manifest
  first so cartridge counts and hashes are protected before vector views

Queued behind that slice:

- consider a gated runtime event/logging spine as future app-monitoring work,
  rooted in structured inspection evidence and not in semantic cartridge truth

Already-completed tranche slices in this family:

- Visibility / Introspection Boundary Realignment (parked)
- Loop Safeguards And Controlled Expansion Review (parked)
- Scored Human-Facing Inspection Usefulness Fixture (parked)
- Visible Host Lifecycle Hardening (parked)
- Bridge Transport Maintenance Surface (parked)
- Bridge Transport And Profile Discipline (parked)
- Disambiguation Bias Repair (parked)

## Visible Horizon

From the current vantage point, we can see roughly four clear tranche bands
ahead without pretending to know every detail yet.

### Band 1: Hardening

- inspection-history retention/pruning
- bridge hardening and transport discipline
- filtering decisions for stream/cockpit
- clearer continuation docs and lifecycle discipline
- scored human-facing inspection usefulness

### Band 2: Controlled Expansion

- selective addition of more UI actions to the shared command spine
- carefully chosen expansion of bounded project-document scope
- targeted seed/projection tuning based on observed failure modes
- possible gated runtime event/logging spine after human visibility evidence is scored

### Band 3: Truth-Surface Decisions

- decide whether interaction envelopes remain inspection-only
- decide if and when command/result projections become persisted semantic truth
- decide what belongs in runtime truth vs builder memory vs logs
- decide whether app-monitoring events remain transient, durably inspectable,
  or queryable, while keeping them out of semantic cartridge truth by default

### Band 4: Post-Prototype Platform Decisions

- decide whether a real MCP protocol wrapper is worth it
- decide whether the bridge remains file-backed or moves to thinner IPC
- decide when broader execution / coordination capabilities are justified

## Current Desired End State

At this juncture, the desired end state is best understood in two layers.

### Desired end state for the current prototype line

```text
a robust, locally vendorable, inspectable semantic prototype
that is useful to a builder, visibly coherent to a human operator,
and disciplined enough to expand without architectural drift
```

### Longer northstar beyond the prototype line

```text
a semantic-native operating substrate in which meaning has explicit
representational form, survives transformation and persistence, remains
addressable and inspectable, and can eventually coordinate execution and
distributed alignment without collapsing back into brittle syntax-only systems
```

The prototype line is about proving the substrate can live locally and
coherently. The longer northstar is about what that substrate can eventually
become.

## Current Scoring Snapshot

Default fixture scores:

- `relation_evidence_trace`: `0.91`, accepted
- `execution_report_trace`: `0.91`, accepted
- `persistence_round_trip`: `0.91`, accepted

Current real-project scores:

- builder-task score: `0.93`, accepted
- projection arbitration score: `0.96`, accepted

Current falsifier panel:

- `tests/test_disambiguation_panel.py`: `10/10` pre-committed queries select the
  expected layer; the panel skips when cartridges are absent so it never
  blocks a clean checkout

Important reading note: the 0.93 / 0.96 score floor measures tasks the
substrate already handles. The falsifier panel measures the substrate's
central context-conditioned disambiguation claim. Stability now means both
floors hold; the panel is the load-bearing one for the central claim.

Current bounded corpora and stores:

- project docs cartridge:
  `data/cartridges/project_documents.sqlite3`
- English lexical cartridge:
  `data/cartridges/base_english_lexicon.sqlite3`
- Python docs cartridge:
  `data/cartridges/python_docs.sqlite3`
- inspection history:
  `data/mcp_inspection/history.sqlite3`
- builder-task score artifact:
  `data/mcp_inspection/builder_task_scores.json`
- projection score artifact:
  `data/mcp_inspection/context_projection_scores.json`

## Active Non-Goals

Still explicitly out of scope unless a future tranche says otherwise:

- no network server
- no full MCP protocol implementation
- no external runtime dependency
- no autonomous agent loop
- no hidden reference/tool-bin coupling
- no host tool installation
- no protocol transport
- no network socket transport
- no polished dashboard
- no custom visualization widgets
- no raw JSON removal
- no embeddings
- no repo-wide scan
- no full-text search engine
- no conversation corpus ingestion
- no cartridge merge
- no hidden app-state ingestion
- no runtime monitoring/logging events promoted to semantic cartridge truth
- no `.dev-tools` runtime dependency
- no Docling runtime dependency
- no custom Python parser beyond docs-text segmentation
- no final semantic grounding claim
- no learned disambiguation

## Latest Verification

Latest tranche verification:

- `python -m unittest tests.test_host_bridge tests.test_host_workspace -v`
  passed with `20` tests after the seed-search bridge policy, Tool Registry
  panel readback, and heartbeat recovery hardening
- `python -m unittest discover -s tests -v` passed with `138` tests after the
  visible host lifecycle hardening
- visible monitor lifecycle smoke passed:
  - `mcp-search-seeds --use-host-bridge --dump-json` returned `status=ok`
    with `ngraph.host.search_seeds` using the medium `30000 ms` policy
  - immediate follow-up `mcp-tools --use-host-bridge --dump-json` returned
    `status=ok`
  - Tool Registry panel readback included `ngraph.analysis.traverse_cartridge`
    and `ngraph.project.query`
  - Seed panel readback showed `Current Park Point`, selected source
    `_docs/PROJECT_STATUS.md`, `steps: 17`, and `blockers: 0`
  - Status panel readback showed `seed_search_bridge_timeout_ms: 30000`
- `python -m unittest tests.test_history_inspector tests.test_host_workspace` passed with `25` tests
- `python -m unittest tests.test_host_bridge tests.test_host_workspace` passed with `16` tests
- `python -m unittest tests.test_project_documents tests.test_host_workspace tests.test_builder_task_scoring tests.test_context_projection_scoring tests.test_host_bridge`
  passed with `29` tests
- `python -m unittest discover -s tests` passed with `126` tests
- `python -m unittest discover -s tests` passed with `132` tests after
  bridge-maintenance implementation
- `python -m compileall src tests` passed
- `python -m src.app mcp-promote-call --dump-json --label keeper --reason checkpoint --note "Preserve this query result."`
  now records bounded operator metadata in inspection history
- `python -m src.app mcp-score-tasks --dump-json` remained at `0.93`, accepted
- `python -m src.app mcp-score-tasks --project-doc-profile expanded --dump-json`
  remained at `0.93`, accepted
- `python -m src.app project-query-score --dump-json` remained at `0.96`, accepted
- `python -m src.app project-query-bag-compare --project-doc-profile expanded --dump-json`
  preserved the app-owned fixed-lens vs baseline comparison surface
- `python -m src.app project-query-adaptive-compare --project-doc-profile expanded --dump-json`
  showed that rotating the current deterministic scorer weights alone did not
  beat the baseline
- `python -m src.app project-query-companion-compare --project-doc-profile expanded --dump-json`
  showed that baseline seed plus auto-lens companion evidence improved support
  coverage without degrading baseline top choice
- `python -m src.app status --dump-json` now emits the current `bridge_timeout_policy`
- `python -m src.app status --dump-json` now also emits `bridge_runtime` and
  `project_doc_profiles`
- `python -m src.app mcp-tools --dump-json` now emits through the shared host dispatcher
- `python -m src.app mcp-read-panels --dump-json --use-host-bridge` now reads
  the live active panel correctly
- `python -m src.app mcp-history --dump-json` now reports rolling-trace retention
- `python -m src.app mcp-cockpit --dump-json` now exposes the same retention split
- filtered stream and cockpit dumps now honor `--tool-filter` and `--layer-filter`
- `python -m src.app mcp-promote-call --dump-json` now promotes the latest
  interaction record and reports retention state
- host bridge support now includes host-owned cockpit/stream/history/promotion
  commands for default workspace-first presentation
- fresh visible smoke now routes `mcp-cockpit`, `mcp-history-view`, and
  `mcp-stream` into the live host workspace without opening extra windows
- bridged CLI smoke succeeded for
  `project-query --use-host-bridge --dump-json`
- forbidden runtime/source-name scan over Python files in `src/` and `tests/`
  found `0` violations for `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`,
  `NodeWALKER`, `docling`, and `Docling`
- `python -m src.app status` now reports:
  - `active_tranche=Post-Prototype Hardening And Expansion`
  - `next_tranche=Traversal Seed Selection Falsifier Panel Or Baseline Manifest Helper`
- `python -m src.app loop-review --dump-json` now emits the loop-safeguard
  review gate against the declared next tranche; current real-project status is
  `ready_for_controlled_expansion_review`, with the next-tranche anchor
  resolving through `_docs/PROJECT_STATUS.md`
- `python -m src.app mcp-bridge-maintenance --dump-json` removed `2` stale
  bridge request files and `1` stale bridge response file under the default
  `300` second retention policy
- `python -m unittest tests.test_disambiguation_panel` passes `10/10` after
  the projection scoring rebalance landed in
  `src/core/coordination/context_projection.py`
- `python -m unittest discover -s tests` passed with `133` tests after the
  disambiguation repair (was `132` plus the new falsifier panel)
- `python -m src.app project-query-score --dump-json` remained at `0.96`,
  accepted, after the rebalance
- `python -m src.app mcp-score-tasks --dump-json` remained at `0.93`,
  accepted, after the rebalance

Useful live commands:

- `python -m src.app ui`
- `python -m src.app mcp-cockpit`
- `python -m src.app mcp-stream`
- `python -m src.app project-query --query "class object function" --dump-json`
- `python -m src.app project-query --query "class object function" --use-host-bridge`
- `python -m src.app project-query-bag --query "Current Park Point" --lens-profile auto --dump-json`
- `python -m src.app project-query-bag-compare --project-doc-profile expanded --dump-json`
- `python -m src.app project-query-adaptive-compare --project-doc-profile expanded --dump-json`
- `python -m src.app project-query-companion-compare --project-doc-profile expanded --dump-json`
- `python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json`
- `python -m src.app mcp-search-seeds --query "Current Park Point" --use-host-bridge`
- `python -m src.app mcp-promote-call --dump-json`
- `python -m src.app mcp-bridge-maintenance --dump-json`
- `python -m src.app mcp-read-panels --dump-json --use-host-bridge`
- `python -m src.app status --dump-json`
- `python -m src.app mcp-tools --dump-json`
- `python -m src.app mcp-score-tasks --dump-json`
- `python -m src.app mcp-score-tasks --use-host-bridge --dump-json`
- `python -m src.app project-query-score --dump-json`
- `python -m src.app project-query-score --use-host-bridge --dump-json`
- `python -m src.app loop-review --dump-json`

## Next-Session Handoff

If re-entering fresh, read:

- `_docs/builder_constraint_contract.md`
- `_docs/PROJECT_STATUS.md`
- `_docs/TODO.md`
- `_docs/THOUGHTS_FOR_NEXT_SESSION.md`

The most important current sync point is simple:

```text
The stable prototype exists.
The bridge exists.
The next work is hardening, not reinvention.
```

## Steering Clarification - 2026-04-30

This is an append-only clarification, not a rewrite of the parked tranche
history above.

After reviewing the side retrieval/evidence harness and running a zero-semantic
ablation, the immediate next slice should be inserted before choosing between
the previously named traversal seed-selection falsifier panel and baseline
manifest helper:

- Retrieval Influence Ablation Fixture

Reason:

- the current companion-bag evidence gain is real, but it mixes deterministic
  surfaces with ML embedding influence
- a zero-semantic ablation showed deterministic bag structure preserves
  document-level coverage gains and some heading recovery, while the ML
  semantic signal appears to improve earlier heading placement
- before any retrieval harness graduates or any vector/docking work resumes,
  the project needs a committed fixture that separates:
  - baseline deterministic seed scoring
  - deterministic-only companion evidence
  - ML-backed companion evidence

Boundary:

- no new embedder
- no Ollama call
- no persisted vector views
- no schema migration
- no cartridge merge
- no promotion of embedding output into semantic cartridge truth
- no replacement of the baseline scorer

After this clarification tranche, the prior next-tranche choice remains valid:

- Baseline Manifest Helper before persisted vector-view work
- Traversal Seed Selection Falsifier Panel if continuing claim-discipline
  hardening

## Retrieval Influence Ablation Fixture - 2026-04-30

Status:

- implemented as a project-owned coordination fixture under
  `src/core/coordination/retrieval_influence_ablation.py`
- exposed through:
  `python -m src.app project-query-ablation-compare --project-doc-profile expanded --dump-json`
- writes:
  `data/mcp_inspection/retrieval_influence_ablation.json`
- compares:
  - baseline deterministic seed scoring
  - deterministic-only companion evidence with semantic-vector influence zeroed
  - ML-backed companion evidence using the existing side-harness semantic model

Boundary preserved:

- no new embedder
- no Ollama call
- no persisted vector views
- no schema migration
- no cartridge merge
- no promotion of embedding output into semantic cartridge truth
- no replacement of the baseline scorer

Next after this fixture:

- Baseline Manifest Helper before persisted vector-view work, or
- Traversal Seed Selection Falsifier Panel if continuing broader
  falsifier-backed claim discipline

## Baseline Manifest Helper - 2026-05-01

Status:

- implemented as a project-owned coordination helper under
  `src/core/coordination/baseline_manifest.py`
- exposed through:
  `python -m src.app baseline-manifest --dump-json`
- writes:
  `data/cartridges/baseline_manifest.json`
- records the protected deterministic cartridges:
  - `base_english_lexicon.sqlite3`
  - `python_docs.sqlite3`
  - `project_documents.sqlite3`

Manifest contract:

- cartridge name
- role
- object, occurrence, relation, and provenance counts
- source refs
- build command
- generator/parser version
- SHA-256 file hash
- cartridge created time
- lock policy

Boundary preserved:

- read-only cartridge inspection
- no schema migration
- no vector generation
- no Ollama call
- no cartridge merge
- no promotion of derived views into cartridge truth
- no in-place deformation of protected baseline cartridges

Next after this helper:

- Traversal Seed Selection Falsifier Panel
