# Development Tools

_Status: Active tool-surface reference_

This document records the project-local development tool surface. It is not a
runtime architecture document. Application runtime code must not depend on
`.dev-tools` unless a tool or package is explicitly vendored into the project
under the builder constraint contract.

## Tool Boundary

`.dev-tools` may be used to work on nGraphMANIFOLD:

- inspect
- scan
- plan
- scaffold
- patch
- audit
- test
- snapshot
- maintain journal continuity

`.dev-tools` may not become a hidden app runtime dependency.

## Installed Tool Surface

Current tool root:

`/.dev-tools/_project-authority/`

This is a thin vendored shim for the DB-packed Project Authority Kit. Its
runtime tool entry points live under:

`/.dev-tools/_project-authority/runtime/src/tools/`

The tool surface includes builder tools, packed authorities, vendable packages,
and templates.

## Builder Tool Categories

Important available tool categories include:

- journal: `journal_init`, `journal_write`, `journal_query`,
  `journal_export`, `journal_snapshot`, `journal_actions`
- contract/governance: `journal_acknowledge`, constraint-oriented packages
- scaffold: `journal_scaffold`, `test_scaffold_generator`
- patching: `tokenizing_patcher`
- architecture analysis: `module_decomp_planner`, `domain_boundary_audit`
- runtime/UI inspection: `scan_blocking_calls`, `tkinter_widget_tree`
- codebase analysis: `import_graph_mapper`, `python_complexity_scorer`,
  `dead_code_finder`, `file_tree_snapshot`
- database analysis: `sqlite_schema_inspector`, `schema_diff_tool`
- verification: `smoke_test_runner`
- packed BuilderSET support: `builderset_authority_*`

Each tool follows the Project Authority Kit pattern:

```text
python src/tools/<tool>.py metadata
python src/tools/<tool>.py run --input-json "{...}"
python src/tools/<tool>.py run --input-file path/to/input.json
```

## Vendable Packages

The toolbox also contains packages that may be installed into target projects
only when explicitly justified:

- `_app-journal`: SQLite-backed shared journal
- `_constraint-registry`: task-scoped constraint injection and governance
- `_manifold-mcp`: reversible text-evidence-hypergraph workflows
- `_ollama-prompt-lab`: local prompt evaluation and Ollama comparison

Vendable packages are not automatically part of nGraphMANIFOLD. Installing or
re-homing one is a structural decision requiring documentation and a journal
entry.

## Recommended Phase Gates

Use these gates as future tranches mature:

- after scaffold: `file_tree_snapshot`
- after first core modules: `domain_boundary_audit`
- after persistence schema: `sqlite_schema_inspector`
- after schema migration begins: `schema_diff_tool`
- after tests exist: `smoke_test_runner`
- after modules grow: `python_complexity_scorer`
- before cleanup: `dead_code_finder`
- before UI integration: `scan_blocking_calls`

## Project Runtime Inspection Commands

The application now includes a project-owned raw MCP inspection command:

```text
python -m src.app mcp-inspect
python -m src.app mcp-inspect --dump-json
python -m src.app mcp-tools --dump-json
python -m src.app mcp-history
python -m src.app mcp-history --dump-json
python -m src.app mcp-ingest-docs --dump-json
python -m src.app mcp-score-tasks --dump-json
python -m src.app mcp-history-view
python -m src.app mcp-history-view --dump-json
python -m src.app mcp-search-seeds --query "Current Park Point"
python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json
python -m src.app ingest-lexicon --reset --dump-json
python -m src.app lookup-lexicon --query tortuous --dump-json
python -m src.app project-query --query "object" --dump-json
python -m src.app ingest-python-docs --reset --dump-json
python -m src.app ingest-python-docs --all-python-docs --reset --dump-json
python -m src.app ingest-python-docs --include-prose --reset --dump-json
```

This is runtime inspection surface, not a `.dev-tools` dependency. The command
opens a minimal raw JSON panel or emits the same payload for headless checks.
The `mcp-tools` command lists project-owned MCP tool registration candidates.
The `mcp-history` command shows persisted registered tool-call history.
The `mcp-ingest-docs` command ingests the bounded project-document set and runs
the registered traversal tool over it.
The `mcp-score-tasks` command scores real builder continuation tasks against
the ingested project documents and writes the latest score artifact.
The `mcp-history-view` command opens or emits a summarized history-aware
inspector payload while preserving the raw history snapshot.
The `mcp-search-seeds` command ranks persisted project-document semantic
objects, calls the registered traversal tool on the selected seed, records the
call in inspection history, and opens or emits the raw evidence payload.
The `ingest-lexicon` command builds a dedicated English lexical baseline
cartridge from the project-owned alpha-array dictionary source. The
`lookup-lexicon` command tests that cartridge by headword and returns a
caution note for inferred parser fields.
The `project-query` command projects a raw query through the current separated
context layers: English lexical prior, Python docs projection, and project
local docs. It returns per-layer candidates, scoring evidence, and a
provisional selected layer without claiming final semantic grounding. It now
routes through the shared command spine, emits command/result envelopes, and
records `ngraph.project.query` in MCP inspection history.
The `ingest-python-docs` command builds a dedicated Python documentation
projection cartridge from the project-owned official Python docs text corpus,
using standard-library AST summaries only for isolated parseable snippets.
The default build is a bounded projection set; `--all-python-docs` opts into the
full tree and `--include-prose` opts into broad documentation prose.

## Tooling Non-Goals

- Do not modify `.dev-tools` as part of normal app work.
- Do not import app runtime code from `.dev-tools`.
- Do not copy tool internals into `src/` without a contract-compliant
  provenance record.
- Do not let tool availability replace tests or architecture discipline.
- Do not include `.dev-tools` in cleanup or generated-cache pruning commands
  unless the user explicitly approves that tooling-maintenance scope.

## Phase Gate Note

`domain_boundary_audit` accepts a single `root` argument. Run it separately on
owned roots such as `src/` and `tests/`; do not point it at the project root
when `.parts` is present unless the intent is to inspect the quarantined
reference bins as well.

## Open Tooling Decisions

- Decide whether `_constraint-registry` should be vendored or simply referenced.
- Decide whether `_manifold-mcp` is a reference source for evidence-bag
  workflows or a future vendored subsystem.
- Decide which phase gates become mandatory before implementation tranches are
  considered complete.

