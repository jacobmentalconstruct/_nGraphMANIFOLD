# MCP Usefulness Seam

_Status: Thin contract plus shared command spine pilot complete_

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

Next work should route selected real project documents through the registered
tool path instead of only fixture content.

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
acceptance. The score artifact is written to:

```text
data/mcp_inspection/builder_task_scores.json
```

Next work should make the history inspector easier to use without hiding the
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
- ranks seed candidates with a deterministic owned text scorer
- calls `ngraph.analysis.traverse_cartridge` on the selected seed
- records the selected traversal in MCP inspection history
- preserves ranked candidates and raw traversal evidence in the inspector

This is not embeddings, FTS, repo-wide scan, or a second tool candidate.

Continue scoring whether the seam helps with:

- finding relevant semantic objects
- understanding relation evidence
- generating a traceable report
- deciding the next implementation action
- reducing repeated manual inspection steps
