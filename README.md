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
aggregate score of `0.93`. The traversal adapter pilot exposes a raw inspection
payload through a simple MCP inspector panel, and the local registry now has two
MCP-shaped candidates: `ngraph.analysis.traverse_cartridge` and
`ngraph.project.query`. Persistent inspection history and a bounded
project-document ingestion path are in place. The history-aware inspector now
summarizes recent calls while preserving raw JSON.
Traversal seed search now ranks persisted project-document semantic objects by
text query, selects a useful seed, runs the registered traversal tool, records
history, and displays the evidence payload through Summary and Raw JSON tabs.
The seed-search summary now shows the selected seed, score breakdown,
breadcrumb, and previous/selected/next source-flow objects so the chosen
starting point can be inspected in order. A dedicated English lexical baseline
cartridge now preserves headword and raw definition records from the
project-owned alpha-array dictionary source for cautious prototype grounding.
The `project-query` command now routes through a shared command/result spine,
records `ngraph.project.query` in MCP inspection history, and projects raw
queries through English lexical, Python documentation, and project-local
context layers while preserving their separate evidence. The `ui` command is
now the primary desktop host workspace rather than a thin query launcher. It
submits the same canonical `CommandEnvelope` shape as CLI-originated calls,
updates a shared in-process host snapshot, and renders command stream, active
projection, active seed flow, score summaries, and Raw JSON as bounded
read-only panes. `mcp-history-view`, `mcp-stream`, `mcp-cockpit`, and
`mcp-search-seeds` now normalize through the same coordination-owned host
dispatcher. A local file-backed host bridge now lets opt-in external
`project-query` and `mcp-search-seeds` commands target an already-open host
workspace without introducing a network server or changing the durable truth
model. The durable truth is still the existing SQLite MCP inspection history
and score artifacts; the host snapshot is a live in-process working set, not a
new truth store. This tranche is parked with builder-task score `0.93`,
projection arbitration score `0.96`, full tests green, and boundary audits
clean.

The project has now crossed from prototype proving into
post-prototype hardening. The next priority is not more transport or more
surface invention. It is making the now-working system stay legible and
vendorable as it accumulates real history, bridge state, and inspection
surfaces. That means retention/pruning policy, bridge discipline, and surface
ownership clarity before broader expansion.

That hardening pass has now begun in code. MCP inspection history uses a
rolling-trace policy with automatic pruning of old unpinned interaction rows,
score-referenced calls are pinned as durable evidence, and bridge transport
files are cleaned conservatively when sessions are activated or polled. The
history, stream, cockpit, and host workspace now expose the active-vs-durable
split so the operator can see what is live trace versus retained evidence.
The next visibility refinement is also in place: `mcp-stream` and
`mcp-cockpit` now accept optional `--tool-filter` and `--layer-filter`
arguments so the operator can narrow the current read surface without changing
the underlying history truth.
Operator-facing promotion controls are now in place as well. The host workspace
can promote or demote the active interaction record, and
`python -m src.app mcp-promote-call` can pin the latest or named call into
durable evidence without changing cartridge truth. Score-referenced calls
remain protected from casual demotion.
Operator promotion now also supports bounded metadata on the history side:
labels, reasons, and freeform notes can be attached to durable evidence so a
later session can tell why a record was kept without promoting that metadata
into semantic cartridge truth.
The presentation model is now more disciplined: the host workspace is the
default visible operator surface, and detached stream/cockpit/history windows
are now an explicit opt-in rather than the normal path.
Host-owned visible commands now wait briefly for a live workspace session
during startup churn before falling back, which prevents the "main window plus
extra popups" race seen in early consolidation testing.
The host now also exposes a panel-read seam so the currently active panel, a
named panel, or the full workspace surface can be inspected through the same
shared host path. Shared-command expansion has also moved `status`,
`mcp-tools`, `mcp-score-tasks`, and `project-query-score` onto the host-owned
dispatcher, and a bounded tuning pass on the current corpus remains stable at
builder-task score `0.93` and projection arbitration score `0.96`.
Interaction-derived semantic-object projections now also declare an explicit
truth policy: they are inspection-only operational evidence adapters, not
semantic cartridge truth. Controlled project-doc expansion is available through
named `core` and `expanded` profiles. The bridge now also exposes an explicit
timeout policy: caller overrides are still supported, but longer-running
bridged scoring commands use larger command-aware defaults and report that
policy back in bridged JSON payloads through an additive `_bridge` section.

Start with:

- `_docs/builder_constraint_contract.md`
- `_docs/EXPERIENTIAL_WORKFLOW.md`
- `_docs/ARCHITECTURE.md`
- `_docs/STRANGLER_PLAN.md`
- `_docs/PROJECT_STATUS.md`
- `_docs/TODO.md`

How we work now, in one breath:

- the contract defines the laws
- the app journal preserves completed phase history
- `PROJECT_STATUS.md` marks current truth
- `TODO.md` shows the operational transition and next step
- scoring and inspection surfaces decide whether an experiment is actually
  useful enough to keep

## Run

```bat
run.bat
```

Equivalent Python command:

```bat
python -m src.app status
```

Open the shared host workspace:

```bat
python -m src.app ui
```

The host workspace now shows command stream, history summary, cockpit summary,
status, tool registry, active projection, active seed flow, latest score
summaries, and Raw JSON from one in-process shared host snapshot. The host now
also publishes a local bridge session under
`data/host_bridge/` so opt-in external commands can target that already-open
window. This is a local file-backed bridge, not a network service.

Target the live host from another process:

```bat
python -m src.app project-query --query "class object function" --use-host-bridge
python -m src.app mcp-search-seeds --query "Current Park Point" --use-host-bridge
```

Headless bridged form:

```bat
python -m src.app project-query --query "class object function" --use-host-bridge --dump-json
```

Read the active host panel, a named panel, or all panels:

```bat
python -m src.app mcp-read-panels --dump-json --use-host-bridge
python -m src.app mcp-read-panels --dump-json --use-host-bridge --panel-mode panel --panel-name projection
python -m src.app mcp-read-panels --dump-json --use-host-bridge --panel-mode all
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

The same command now also routes through the shared host dispatcher and can be
delivered to a live workspace with `--use-host-bridge`.

Show recent persisted MCP inspection calls:

```bat
python -m src.app mcp-history --dump-json
```

Ingest selected project documents and traverse them through the registered tool:

```bat
python -m src.app mcp-ingest-docs --dump-json
python -m src.app mcp-ingest-docs --project-doc-profile expanded --dump-json
```

Score real builder continuation tasks over ingested project docs:

```bat
python -m src.app mcp-score-tasks --dump-json
python -m src.app mcp-score-tasks --project-doc-profile expanded --dump-json
```

This command now also routes through the shared host dispatcher. When targeting
the live host for a longer scoring run, the bridge now applies command-aware
defaults: builder-task scoring uses a heavy default and projection scoring uses
a medium default. `--bridge-timeout-ms` remains available as an explicit caller
override. The expanded profile is intentionally opt-in because it is more
informative but materially heavier than the core four-doc profile.

Show the history-aware inspector summary:

```bat
python -m src.app mcp-history-view
```

Headless summary/raw payload:

```bat
python -m src.app mcp-history-view --dump-json
```

Detached popup form:

```bat
python -m src.app mcp-history-view --detached-window
```

Open a basic polling stream of query/response objects from inspection history:

```bat
python -m src.app mcp-stream
```

The Stream tab renders each recent interaction as a compact labeled object with
query, result, selected layer/kind/score, preview, source, and call id. It polls
history incrementally, appends only newly seen calls, and pauses autoscroll
while the vertical scrollbar is held. The Raw JSON tab preserves the full
payload.

Headless stream payload:

```bat
python -m src.app mcp-stream --dump-json
```

Detached popup form:

```bat
python -m src.app mcp-stream --detached-window
```

Promote the latest or named interaction into durable evidence:

```bat
python -m src.app mcp-promote-call --dump-json
python -m src.app mcp-promote-call --call-id "<call-id>" --dump-json
python -m src.app mcp-promote-call --call-id "<call-id>" --label keeper --reason checkpoint --note "Why this matters" --dump-json
```

Demote an operator-pinned record:

```bat
python -m src.app mcp-promote-call --call-id "<call-id>" --demote --dump-json
```

Score-linked durable evidence remains locked against demotion through this
surface. Promotion metadata stays in the inspection-history ledger as operator
context, not cartridge truth.

Open the unified read-only visibility cockpit:

```bat
python -m src.app mcp-cockpit
```

Headless cockpit payload:

```bat
python -m src.app mcp-cockpit --dump-json
```

Detached popup form:

```bat
python -m src.app mcp-cockpit --detached-window
```

Search ingested project documents for traversal seeds and inspect the selected
traversal:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point"
python -m src.app mcp-search-seeds --project-doc-profile expanded --query "Current Park Point" --dump-json
```

The inspector opens with Summary and Raw JSON tabs. The Summary tab shows the
selected seed, score breakdown, breadcrumb, and source-flow objects around the
selection.

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
call is recorded in `data/mcp_inspection/history.sqlite3`. The projection frame
now includes `selected_flow`, which shows the selected candidate plus nearby
alternatives from the same layer with rank, evidence, breadcrumb, and preview.
When the same command shape is run inside the UI host, it updates the live host
snapshot instead of opening a separate path. With `--use-host-bridge`, an
external process can now send the same command to the already-open host
workspace and let that live window update in place.

Score context-layer arbitration fixtures:

```bat
python -m src.app project-query-score --dump-json
```

The scoring run records each underlying `ngraph.project.query` call in MCP
inspection history and writes
`data/mcp_inspection/context_projection_scores.json`.
This command now also routes through the shared host dispatcher and can update
the live host workspace when sent through the bridge.

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

