# MCP Usefulness Seam

_Status: Thin contract plus local host bridge complete_

This document records the Phase 8 MCP seam. It is subordinate to
`builder_constraint_contract.md` and does not declare a full MCP server.

## Purpose

The seam exists so the prototype can be evaluated by how useful it is for a
builder or agent to use, not only by whether internal layers are present.

The first usefulness question is:

```text
Does this capability reduce the effort required to inspect, reason about, and
act on semantic project state?
```

## Current Form

Runtime owner:

- `src/core/coordination/mcp_seam.py`
- `src/core/coordination/local_mcp_adapter.py`
- `src/core/coordination/mcp_tool_registry.py`
- `src/core/coordination/mcp_inspection_history.py`
- `src/core/coordination/interaction_spine.py`
- `src/core/coordination/project_documents.py`
- `src/core/coordination/builder_task_scoring.py`
- `src/core/coordination/history_inspector.py`
- `src/core/coordination/seed_search.py`
- `src/core/coordination/host_workspace.py`
- `src/core/coordination/host_bridge.py`
- `src/ui/mcp_inspector.py`
- `src/ui/gui_main.py`

The seam provides:

- capability descriptors for the prototype spine
- declared input and output shapes for future wrapping
- usefulness scoring signals
- aggregate usefulness reports
- an acceptance threshold for tuning

## Capability Surface

Current capability descriptors cover:

- source text to semantic objects
- relation enrichment
- cartridge traversal
- bounded execution
- semantic cartridge persistence/querying
- project context query projection

These descriptors are not network endpoints. They are stable local contracts a
future MCP wrapper can map onto.

## Local Adapter Pilot

Current pilot:

- `analysis.traverse_cartridge`

The local adapter captures:

- capability descriptor
- seam manifest
- request payload
- traversal response
- usefulness report
- builder-facing notes

This capture is visible through:

```bat
python -m src.app mcp-inspect
```

For headless inspection:

```bat
python -m src.app mcp-inspect --dump-json
```

Current local adapter score:

- `analysis.traverse_cartridge`: `0.93`, accepted

## Tool Registration Candidate

Registered candidate:

- `ngraph.analysis.traverse_cartridge`
- `ngraph.project.query`

The registered tool accepts a JSON-like request:

For `ngraph.analysis.traverse_cartridge`:

- `db_path`
- `seed_semantic_id`
- optional `cartridge_id`
- optional `max_depth`
- optional `max_steps`
- optional `include_incoming`

For `ngraph.project.query`:

- `query`
- optional `limit`
- optional `context_stack`

The result envelope includes:

- `call_id`
- `tool`
- `status`
- `capture`

List registered candidates with:

```bat
python -m src.app mcp-tools --dump-json
```

The inspector now routes through the registered tool candidate before rendering
or dumping the raw capture.

## Shared Command Spine

`project-query` is the first shared command-spine pilot. A CLI call now creates
a `CommandEnvelope`, executes the project query handler, creates a
`ToolResultEnvelope`, and stores the combined `InteractionCapture` in MCP
inspection history.

The capture preserves:

- actor and source surface
- tool name and command payload
- correlation id and command id
- result status and evidence summary
- selected projection layer and candidate evidence
- raw projection frame
- usefulness report

SemanticObject projection adapters exist for command and result envelopes, but
this tranche does not persist interaction events into semantic cartridges.

## Shared Host State Spine

The desktop host now has a coordination-owned live state model:

- recent command/result objects
- active projection and `selected_flow`
- active seed flow
- latest builder score summary
- latest projection score summary
- active interaction object
- raw payload cache for current panes

The durable ledger is still:

- `data/mcp_inspection/history.sqlite3`
- `data/mcp_inspection/builder_task_scores.json`
- `data/mcp_inspection/context_projection_scores.json`

The host snapshot is an in-process working set for the UI, not a new truth
store.

Shared dispatcher ownership:

- `project-query`
- `mcp-search-seeds`
- `mcp-history-view`
- `mcp-stream`
- `mcp-cockpit`

All of these now normalize through one coordination-owned dispatcher before
their payloads are shown in the host workspace.

## Local Host Bridge

The seam now includes a bounded local host bridge for separate-process session
control without introducing a network server.

Bridge state is project-owned:

```text
data/host_bridge/session.json
data/host_bridge/requests/
data/host_bridge/responses/
```

The UI host publishes a live bridge session while `python -m src.app ui` is
open and heartbeats that session through the normal Tk event loop.

The first bridge-enabled commands are:

- `project-query`
- `mcp-search-seeds`

Opt-in CLI usage:

```bat
python -m src.app project-query --query "class object function" --use-host-bridge
python -m src.app mcp-search-seeds --query "Current Park Point" --use-host-bridge
```

These calls reuse the existing canonical `CommandEnvelope` shape. They do not
invent a second command language for cross-process control.

The bridge is intentionally:

- local
- file-backed
- inspectable
- stdlib-only
- bounded to approved commands

It is not:

- a network service
- a websocket layer
- a real MCP server
- a new truth store

The next seam pressure is not "more transport." It is how the current bridge
stays bounded and inspectable as the project enters post-prototype hardening.

## Persistent Inspection History

Registered tool calls are now persisted in a project-owned SQLite history store:

```text
data/mcp_inspection/history.sqlite3
```

The history stores:

- call id
- tool name
- capability name
- captured timestamp
- status
- aggregate score
- raw call/capture JSON

This history is now important enough that the project has an explicit
retention/pruning policy. The current rolling-trace model is:

- Active Reasoning:
  - recent unpinned interaction captures kept for live inspection and current
    session legibility
- Durable Evidence:
  - score-referenced call ids pinned in history, plus accepted score artifacts
    and journaled decisions outside the history store

Implemented behavior now includes:

- automatic pruning of old unpinned rows beyond the rolling-trace limit
- automatic pinning of call ids referenced by current score artifacts
- retention summary visible in history, stream, cockpit, and host payloads

For `ngraph.project.query`, history summaries also include selected projection
layer and candidate count when available.

Show recent history:

```bat
python -m src.app mcp-history
```

Headless history view:

```bat
python -m src.app mcp-history --dump-json
```

## Surface Ownership In The Hardening Phase

The seam now has enough visibility surfaces that ownership needs to be stated
plainly:

- host workspace:
  - the main live operator surface over the shared in-process host snapshot
- stream:
  - the sliding recent interaction window
- cockpit:
  - the compact shared registry for latest scores, latest projection, latest
    seed flow, and recent stream state
- history view:
  - the deeper provenance access surface over persisted inspection records

The next hardening work should preserve these roles rather than letting
multiple surfaces drift into saying the same thing differently.

The first bounded filtering refinement now exists:

- `mcp-stream` accepts optional exact `tool_filter`
- `mcp-stream` accepts optional exact `layer_filter`
- `mcp-cockpit` accepts the same filters
- filtered views report their active filters in raw payloads

These filters narrow the read surface only. They do not mutate persisted
history, scoring artifacts, or cartridge truth.

The next bounded operator control is now in place as well:

- `mcp-promote-call` promotes the latest or named history record
- the host workspace exposes `Promote Active` and `Demote Active`
- promotion updates durable-evidence state in the history ledger only
- score-linked records remain locked against casual demotion

This keeps the active reasoning / durable evidence split visible and controllable
without turning MCP interaction captures into cartridge truth.

The presentation rule is now clarified too:

- the host workspace is the default visible operator surface
- host-owned stream, cockpit, history, and promotion commands can route through
  the local bridge to that existing workspace
- host-owned visible commands now wait briefly for a live session to appear
  before falling back, which keeps startup races from spraying detached windows
- detached windows are still available, but only through explicit
  `--detached-window` usage

That keeps the shared visible workflow centered on one main surface instead of
letting useful but fragmented windows become the default operator experience.

## Usefulness Scoring

Scoring dimensions:

- task fit
- evidence quality
- actionability
- friction reduction
- repeatability

The current acceptance threshold is `0.7`.

## Explicit Non-Goals

- no network server
- no full MCP protocol implementation
- no external runtime dependency
- no autonomous agent loop
- no hidden coupling to quarantined reference or tool bins
- no socket transport requirement

## Prototype Scoring Harness

Repeatable builder-task fixtures now exist in:

- `src/core/coordination/prototype_scoring.py`

Current default fixture scores:

- `relation_evidence_trace`: `0.91`
- `execution_report_trace`: `0.91`
- `persistence_round_trip`: `0.91`

All pass the `0.7` acceptance threshold. The recommended first real adapter
candidate is:

- `analysis.traverse_cartridge`

The next seam pressure is no longer "can the live host be targeted?" The next
seam pressure is whether retention/pruning, broader bridge coverage, or a
different local transport are worth the added complexity.

## Project Document Ingestion

Selected project documents can now be ingested into a project-owned cartridge
and traversed through the registered tool path:

```bat
python -m src.app mcp-ingest-docs --dump-json
```

Current bounded document set:

- `README.md`
- `_docs/PROJECT_STATUS.md`
- `_docs/MCP_SEAM.md`
- `_docs/STRANGLER_PLAN.md`

The command creates or updates:

```text
data/cartridges/project_documents.sqlite3
```

It records the registered traversal call into the same MCP inspection history.

Next work should score whether this helps answer real builder continuation
questions.

## Real Builder-Task Scoring

Real builder continuation tasks now score against ingested project documents:

```bat
python -m src.app mcp-score-tasks --dump-json
```

Current task set:

- current tranche lookup
- MCP surface lookup
- strangler next-work lookup
- operator command lookup

The latest real-project run produced aggregate score `0.93` and passed
acceptance. Builder-task scoring now uses the same seed-fitness scorer as
`mcp-search-seeds`, with a narrow builder-task policy for document role,
heading/section affinity, continuation markers, operator-command proximity, and
expected source fit. The score artifact is written to:

```text
data/mcp_inspection/builder_task_scores.json
```

Next work should make seed-fitness details easier to inspect without hiding the
raw JSON.

## History-Aware Inspector

Recent MCP calls can now be viewed through a summarized inspector payload:

```bat
python -m src.app mcp-history-view
```

Headless form:

```bat
python -m src.app mcp-history-view --dump-json
```

The payload includes:

- compact recent call summaries
- tool name
- capability
- status
- aggregate score
- traversal step and blocker counts
- mapped builder task ids when the latest score artifact contains them
- raw history snapshot

The inspector UI preserves the raw JSON view and adds a Summary tab for this
payload.

## Interaction Stream

Recent command/result records can also be viewed as a basic chronological
query/response stream:

```bat
python -m src.app mcp-stream
```

Headless form:

```bat
python -m src.app mcp-stream --dump-json
```

The stream projects existing MCP inspection history into compact query/response
objects. For `ngraph.project.query`, it renders each record as a labeled
object block with query, result, selected layer, selected candidate kind, score,
preview, source, and call id. The UI polls the history database and preserves a
Raw JSON tab for the same payload.

Current stream behavior:

- initial render reads the recent history snapshot
- later polls append only newly seen call ids
- the formatted Stream tab keeps object blocks readable without making them
  semantic cartridge truth
- autoscroll pauses while the vertical scrollbar is held so inspection is not
  interrupted by refreshes
- the Raw JSON tab remains the complete payload

`project-query` records now also carry `selected_flow`, so recent stream items
can show the selected projection candidate plus nearby alternatives in rank
order.

## Visibility Cockpit

The prototype now has a unified read-only visibility surface:

```bat
python -m src.app mcp-cockpit
python -m src.app mcp-cockpit --dump-json
```

The cockpit combines:

- latest builder-task score artifact
- latest projection score artifact
- latest `ngraph.project.query` capture
- latest builder-seed flow snapshot
- recent interaction stream records
- Raw JSON tab for the full payload

The cockpit is intentionally history-first. It does not introduce a new truth
store, a message spine, cartridge persistence for interaction events, or a
polished dashboard framework.

## UI Command Spine Pilot

`python -m src.app ui` is now the primary desktop host workspace rather than a
thin command pilot.

The host workspace submits the same canonical command shape and renders:

- command stream
- active projection
- active seed flow
- latest score summaries
- Raw JSON for the current host snapshot

The rule for this tranche is explicit:

- same process: shared live host state
- separate process: shared durable state only

That means headless commands do not auto-attach to an already-open window yet.
`--dump-json` remains the official non-UI path.

## Layer Arbitration Scoring

`project-query-score` runs the first bounded context-projection arbitration
fixtures:

```bat
python -m src.app project-query-score --dump-json
```

The command drives plain English, Python/code, and project-local doctrine
queries through `run_project_query_interaction`. Each fixture therefore emits
the same `ngraph.project.query` capture shape as CLI and UI calls while marking
the command envelope with `actor="builder"` and `source_surface="scoring"`.

The score artifact is written to:

`data/mcp_inspection/context_projection_scores.json`

The current purpose is measurement and tuning evidence. It is not a new MCP
server, not a merged semantic cartridge, and not learned disambiguation.

Next work should improve seed discovery and search over ingested project
documents.

## Traversal Seed Search

Persisted project-document semantic objects can now be searched and ranked as
candidate traversal seeds:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point"
```

Headless form:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json
```

The command:

- re-ingests the bounded project-document set into the project cartridge
- removes stale semantic objects for each re-ingested source before replacement
- ranks seed candidates with a deterministic owned seed-fitness scorer
- includes score-breakdown dimensions in the raw selected-seed payload
- includes a `selected_flow` window with previous / selected / next semantic
  objects from the same source document
- calls `ngraph.analysis.traverse_cartridge` on the selected seed
- records the selected traversal in MCP inspection history
- preserves ranked candidates and raw traversal evidence in the inspector
- opens the existing inspector with a Summary tab showing the selected seed,
  score breakdown, breadcrumb, source flow, and traversal summary beside the
  full Raw JSON tab

This is not embeddings, FTS, repo-wide scan, or a second tool candidate.

Continue scoring whether the seam helps with:

- finding relevant semantic objects
- understanding relation evidence
- generating a traceable report
- deciding the next implementation action
- reducing repeated manual inspection steps
