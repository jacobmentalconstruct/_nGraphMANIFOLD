# Project Status

_Status: Active parking surface, post-prototype hardening slice parked_

This file is the quick continuation marker between tranches. The app journal
remains the authoritative phase ledger.

## Current Park Point

Just-completed tranche:

- Bridge Timeout Policy And Explicit Reporting

Status:

- parked complete inside post-prototype hardening

Started:

- 2026-04-23

Parked:

- 2026-04-24

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

- MCP inspection history uses a rolling-trace policy
- old unpinned interaction rows are pruned automatically
- score-referenced call ids are pinned as durable evidence
- stale bridge request/response/session files are cleaned conservatively
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
  projection scoring now defaults to a medium bridge timeout policy
- `--bridge-timeout-ms` remains a caller-owned override rather than being
  removed from the CLI surface
- bridged JSON payloads now expose additive `_bridge` metadata so timeout
  behavior is inspectable instead of implicit
- status surfaces now expose a machine-readable `bridge_timeout_policy`
  manifest for the current host bridge defaults

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

Current active tranche:

- Post-Prototype Hardening And Expansion

Immediate focus inside that tranche:

- decide whether command/result SemanticObjects remain inspection-only or
  become persisted cartridge truth later
- decide whether to expand the bounded project-document set beyond the current
  four docs
- decide whether operator-promoted durable evidence needs labels, notes, or
  reason metadata beyond a simple pin

Recommended next tranche after this hardening slice:

- Operator Metadata Decisions

The first concrete hardening problem is:

```text
how do we preserve operator trust and project boundedness now that the
prototype produces real history, real bridge state, and multiple useful
inspection surfaces?
```

## Visible Horizon

From the current vantage point, we can see roughly four clear tranche bands
ahead without pretending to know every detail yet.

### Band 1: Hardening

- inspection-history retention/pruning
- bridge hardening and transport discipline
- filtering decisions for stream/cockpit
- clearer continuation docs and lifecycle discipline

### Band 2: Controlled Expansion

- selective addition of more UI actions to the shared command spine
- carefully chosen expansion of bounded project-document scope
- targeted seed/projection tuning based on observed failure modes

### Band 3: Truth-Surface Decisions

- decide whether interaction envelopes remain inspection-only
- decide if and when command/result projections become persisted semantic truth
- decide what belongs in runtime truth vs builder memory vs logs

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
- no `.dev-tools` runtime dependency
- no Docling runtime dependency
- no custom Python parser beyond docs-text segmentation
- no final semantic grounding claim
- no learned disambiguation

## Latest Verification

Latest tranche verification:

- `python -m unittest tests.test_history_inspector tests.test_host_workspace` passed with `21` tests
- `python -m unittest tests.test_host_bridge tests.test_host_workspace` passed with `16` tests
- `python -m unittest discover -s tests` passed with `123` tests
- `python -m compileall src tests` passed
- `python -m src.app mcp-score-tasks --dump-json` remained at `0.93`, accepted
- `python -m src.app project-query-score --dump-json` remained at `0.96`, accepted
- `python -m src.app status --dump-json` now emits the current `bridge_timeout_policy`
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
  - `next_tranche=Operator Metadata Decisions`

Useful live commands:

- `python -m src.app ui`
- `python -m src.app mcp-cockpit`
- `python -m src.app mcp-stream`
- `python -m src.app project-query --query "class object function" --dump-json`
- `python -m src.app project-query --query "class object function" --use-host-bridge`
- `python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json`
- `python -m src.app mcp-search-seeds --query "Current Park Point" --use-host-bridge`
- `python -m src.app mcp-promote-call --dump-json`
- `python -m src.app mcp-read-panels --dump-json --use-host-bridge`
- `python -m src.app status --dump-json`
- `python -m src.app mcp-tools --dump-json`
- `python -m src.app mcp-score-tasks --dump-json`
- `python -m src.app mcp-score-tasks --use-host-bridge --dump-json`
- `python -m src.app project-query-score --dump-json`
- `python -m src.app project-query-score --use-host-bridge --dump-json`

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
