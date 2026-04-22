# TODO

_Status: Active continuation checklist_

This file is a human-readable checkpoint. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Current Park Point

Completed tranche:

- Projection Scoring And MCP Inspection: Shared Command Spine

Current status:

- parked complete in bounded prototype form

Before continuing:

- read `_docs/THOUGHTS_FOR_NEXT_SESSION.md`
- start with UI Command Spine Pilot

## Completed Recently

- project document ingestion over the bounded doc set
- real builder-task scoring over ingested docs
- history-aware inspector payload with summarized recent calls
- tabbed inspector display with Summary and Raw JSON views
- deterministic seed search over persisted project-document semantic objects
- selected traversal calls recorded in MCP inspection history
- stale semantic-object replacement during bounded project-doc re-ingestion
- dedicated English lexical baseline cartridge
- headword lookup over `data/cartridges/base_english_lexicon.sqlite3`
- cautious parser notes for alpha-array dictionary fields
- project-owned Python docs text extractor
- AST summaries over isolated parseable Python documentation snippets
- dedicated Python docs projection cartridge
- layered probe across English lexicon, Python docs, and project-doc cartridges
- next-session conceptual handoff in `_docs/THOUGHTS_FOR_NEXT_SESSION.md`
- sanitized English lexical baseline naming:
  `ingest-lexicon`, `lookup-lexicon`,
  `data/cartridges/base_english_lexicon.sqlite3`
- first deterministic `project-query` command
- query projection frame with English lexical, Python docs, and project-local
  evidence layers
- shared command spine for `project-query`
- `CommandEnvelope`, `ToolResultEnvelope`, and `InteractionCapture`
- `ngraph.project.query` registered as an MCP-shaped candidate
- project-query calls recorded in MCP inspection history
- SemanticObject projection adapters for command/result envelopes

## Next Tranche

Active tranche:

- UI Command Spine Pilot

Goal:

- prove that a human-facing UI control and CLI/MCP-shaped calls can share the
  same `CommandEnvelope` source of truth and produce comparable inspection
  history records

In scope:

- add one minimal UI control for project query
- route the UI action through the existing shared command spine
- display the resulting `InteractionCapture` in the existing inspector
- verify UI, CLI, and MCP-shaped calls use the same envelope structure

Done when:

- focused UI command-spine tests pass
- full unit discovery passes
- the UI control produces a history record with `ngraph.project.query`
- docs and journal record the UI/MCP alignment behavior

Explicit non-goals:

- no embeddings
- no repo-wide scan
- no real network MCP server
- no polished dashboard
- no full-text search engine
- no conversation corpus ingestion
- no merge between cartridges
- no `.dev-tools` runtime dependency
- no interaction-event cartridge persistence yet

## Backlog

- Add search-scored traversal tuning after lexical layering has a baseline.
- Decide whether the bounded document set should expand beyond the current four
  docs.
- Define retention/pruning rules for MCP inspection history.
- Add a formatted inspector view only after the summary view proves useful.
- Decide if and when to wrap the local registry in a real MCP protocol server.
- Decide whether the raw dictionary text should be compared against the alpha-array
  JSON for richer example extraction.
- Decide whether the next user-facing display should expose layered projection
  candidates or wait until scoring/arbitration is implemented.
- Decide when command/result SemanticObject projections should become persisted
  cartridge truth instead of inspection-only adapters.
- Decide which UI actions beyond `project-query` should join the shared command
  spine after the first button/control pilot.

