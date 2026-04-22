# nGraphMANIFOLD

nGraphMANIFOLD is a semantic operating substrate under construction. Its
architecture is governed by the builder constraint contract and the semantic OS
conceptual build plan under `_docs/`.

## Current Status

The project has completed the scaffold foundation, canonical semantic object,
persistence cartridge, intake adapter, and first relation-enrichment tranches.
It now has a first traceable cartridge traversal artifact and a minimal
semantic execution pathway. Runtime implementation remains intentionally narrow
with a thin MCP usefulness seam and repeatable prototype tuning/scoring
fixtures. The default scoring fixtures pass acceptance, and real builder-task
scoring over the bounded project-document cartridge currently passes with an
aggregate score of `0.87`. The traversal adapter pilot exposes a raw inspection
payload through a simple MCP inspector panel, and the local registry now has two
MCP-shaped candidates: `ngraph.analysis.traverse_cartridge` and
`ngraph.project.query`. Persistent inspection history and a bounded
project-document ingestion path are in place. The history-aware inspector now
summarizes recent calls while preserving raw JSON.
Traversal seed search now ranks persisted project-document semantic objects by
text query, selects a useful seed, runs the registered traversal tool, records
history, and displays the raw evidence payload. A dedicated English lexical
baseline cartridge now preserves headword and raw definition records from the
project-owned alpha-array dictionary source for cautious prototype grounding.
The `project-query` command now routes through a shared command/result spine,
records `ngraph.project.query` in MCP inspection history, and projects raw
queries through English lexical, Python documentation, and project-local
context layers while preserving their separate evidence. The parked next
implementation target is the UI Command Spine Pilot.

Start with:

- `_docs/builder_constraint_contract.md`
- `_docs/ARCHITECTURE.md`
- `_docs/STRANGLER_PLAN.md`
- `_docs/PROJECT_STATUS.md`
- `_docs/TODO.md`

## Run

```bat
run.bat
```

Equivalent Python command:

```bat
python -m src.app status
```

Open the raw MCP inspection panel:

```bat
python -m src.app mcp-inspect
```

Headless/raw JSON form:

```bat
python -m src.app mcp-inspect --dump-json
```

List registered MCP tool candidates:

```bat
python -m src.app mcp-tools --dump-json
```

Show recent persisted MCP inspection calls:

```bat
python -m src.app mcp-history --dump-json
```

Ingest selected project documents and traverse them through the registered tool:

```bat
python -m src.app mcp-ingest-docs --dump-json
```

Score real builder continuation tasks over ingested project docs:

```bat
python -m src.app mcp-score-tasks --dump-json
```

Show the history-aware inspector summary:

```bat
python -m src.app mcp-history-view
```

Headless summary/raw payload:

```bat
python -m src.app mcp-history-view --dump-json
```

Search ingested project documents for traversal seeds and inspect the selected
traversal:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point"
```

Headless seed-search traversal payload:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json
```

Build the English lexical baseline:

```bat
python -m src.app ingest-lexicon --reset --dump-json
```

Look up an English lexical headword:

```bat
python -m src.app lookup-lexicon --query tortuous --dump-json
```

Project a query through the current context layers:

```bat
python -m src.app project-query --query "object" --dump-json
```

The output is an `InteractionCapture` containing a `CommandEnvelope`, a
`ToolResultEnvelope`, the projection frame, and a usefulness report. The same
call is recorded in `data/mcp_inspection/history.sqlite3`.

Build the Python documentation projection cartridge:

```bat
python -m src.app ingest-python-docs --reset --dump-json
```

Build the full Python docs tree or include broad prose descriptions explicitly:

```bat
python -m src.app ingest-python-docs --all-python-docs --reset --dump-json
python -m src.app ingest-python-docs --include-prose --reset --dump-json
```

## Test

```bat
python -m unittest discover -s tests
```

## Boundary

`.parts` and `.dev-tools` are reference/tool surfaces. Application runtime code
must not import from them or require them.

