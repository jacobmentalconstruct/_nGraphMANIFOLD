# Project Status

_Status: Active parking surface_

This file is the quick continuation marker for parking between tranches. The app
journal remains the authoritative phase ledger.

## Current Park Point

Tranche: Projection Scoring And MCP Inspection: Shared Command Spine

Status: parked complete in bounded prototype form

Started: 2026-04-22

Parked: 2026-04-22

## Scope

In scope:

- generic English lexical baseline naming:
  `ingest-lexicon`, `lookup-lexicon`,
  `data/cartridges/base_english_lexicon.sqlite3`
- removal of the old generated source-branded cartridge filename after the
  sanitized cartridge was rebuilt
- `src/core/coordination/context_projection.py`
- `src/core/coordination/interaction_spine.py`
- deterministic query tokenization that preserves code-shaped terms
- per-layer projection over English lexical, Python docs, and project-local
  cartridges
- provisional layer/candidate selection with evidence notes and caution text
- shared `CommandEnvelope`, `ToolResultEnvelope`, and `InteractionCapture`
- `ngraph.project.query` registered as an MCP-shaped tool candidate
- `python -m src.app project-query --query "object" --dump-json` records the
  shared interaction capture in MCP inspection history
- focused tests for English lexical naming and context projection
- focused tests for command spine, history recording, and SemanticObject
  projection adapters

Explicit non-goals:

- no network server
- no full MCP protocol implementation
- no external runtime dependency
- no autonomous agent loop
- no hidden reference/tool-bin coupling
- no host tool installation
- no protocol transport
- no new document ingestion scope beyond the existing bounded docs
- no polished dashboard
- no new UI button
- no custom visualization widgets
- no raw JSON removal
- no embeddings
- no repo-wide scan
- no full-text search engine
- no conversation corpus ingestion
- no merge into the project-document cartridge
- no merge into the English lexical cartridge
- no merge into the Python docs cartridge
- no `.dev-tools` runtime dependency
- no Docling runtime dependency
- no custom Python parser beyond docs-text segmentation
- no final semantic grounding claim
- no learned disambiguation

## Completed Prototype Spine

The first prototype spine is now complete:

```text
source content
  -> SemanticObject
  -> relation enrichment
  -> semantic cartridge persistence
  -> traversal / analysis
  -> traceable execution result
  -> thin MCP usefulness seam
  -> repeatable prototype tuning/scoring fixtures
  -> local traversal adapter pilot
  -> raw MCP inspection payload / panel
  -> local MCP tool registration candidate
  -> persistent MCP inspection history
  -> selected project-document ingestion
  -> real builder-task scoring
  -> history-aware MCP inspector
  -> traversal seed search / selection
  -> English lexical baseline cartridge
  -> Python docs projection cartridge
  -> context projection frame
  -> shared command/result spine for project-query
```

## Next Park Target

Immediate next work after parking this tranche:

- UI Command Spine Pilot

This should add the first minimal human-facing control that emits the same
`CommandEnvelope` shape as CLI/MCP-shaped calls and displays the resulting
`InteractionCapture` through the existing inspector.

Next-session handoff:

- `_docs/THOUGHTS_FOR_NEXT_SESSION.md` captures the conceptual read on the
  current prototype, what the latest layered probe taught us, implications for
  context projection, and a suggested next tranche shape.

## Current Scoring Snapshot

Default fixture scores:

- `relation_evidence_trace`: `0.91`, accepted
- `execution_report_trace`: `0.91`, accepted
- `persistence_round_trip`: `0.91`, accepted

All default fixtures pass the `0.7` usefulness acceptance threshold. The current
recommended first adapter candidate is `analysis.traverse_cartridge`.

Local adapter snapshot:

- `analysis.traverse_cartridge`: `0.93`, accepted
- registered tool candidate: `ngraph.analysis.traverse_cartridge`
- registered tool candidate: `ngraph.project.query`
- raw captures include capability descriptor, seam manifest context where
  applicable, request/command envelope, response/result envelope, usefulness
  report, and builder notes
- persisted history path: `data/mcp_inspection/history.sqlite3`
- project document cartridge path: `data/cartridges/project_documents.sqlite3`
- bounded document set: `README.md`, `_docs/PROJECT_STATUS.md`,
  `_docs/MCP_SEAM.md`, `_docs/STRANGLER_PLAN.md`
- builder task score artifact: `data/mcp_inspection/builder_task_scores.json`
- current real-doc aggregate score: `0.87`, accepted
- history-aware command: `python -m src.app mcp-history-view`
- seed-search command: `python -m src.app mcp-search-seeds --query "Current Park Point"`
- English lexical baseline cartridge path: `data/cartridges/base_english_lexicon.sqlite3`
- English lexical source path: `assets/_corpus_examples/dictionary_alpha_arrays.json`
- English lexical build command: `python -m src.app ingest-lexicon --reset --dump-json`
- English lexical lookup command: `python -m src.app lookup-lexicon --query tortuous --dump-json`
- context projection command:
  `python -m src.app project-query --query "object" --dump-json`
- project query history tool name: `ngraph.project.query`
- Python docs projection cartridge path: `data/cartridges/python_docs.sqlite3`
- Python docs source path:
  `assets/_corpus_examples/python-3.11.15-docs-text`
- bounded Python docs projection set: `library/functions.txt`,
  `reference/compound_stmts.txt`, `reference/simple_stmts.txt`,
  `tutorial/controlflow.txt`
- Python docs build command:
  `python -m src.app ingest-python-docs --reset --dump-json`
- full-tree option:
  `python -m src.app ingest-python-docs --all-python-docs --reset --dump-json`
- Python docs broad-prose option:
  `python -m src.app ingest-python-docs --include-prose --reset --dump-json`
- next-phase plan: `_docs/TODO.md`

## Latest Verification

- `python -m unittest tests.test_scaffold` passed with 4 tests.
- `python -m src.app status` reports
  `active_tranche=Projection Scoring And MCP Inspection: Shared Command Spine`
  and `next_tranche=UI Command Spine Pilot`.
- `python -m unittest discover -s tests` passed with 89 tests.
- `python -m compileall src tests` passed.
- forbidden runtime/source-name scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, `NodeWALKER`,
  `docling`, `Docling`, or source-branded English lexicon component names.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=42`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=20`, `total_violations=0`.
- `python -m src.app project-query --query "class object function" --dump-json`
  emitted a shared interaction capture with `CommandEnvelope`,
  `ToolResultEnvelope`, projection frame, and usefulness report; it selected
  `python_docs_projection` and recorded `ngraph.project.query` in
  `data/mcp_inspection/history.sqlite3`.
- `python -m src.app mcp-tools --dump-json` listed both
  `ngraph.analysis.traverse_cartridge` and `ngraph.project.query`.
- `python -m src.app mcp-history-view --dump-json --history-limit 5` showed
  project-query records beside traversal records with
  `selected_layer=python_docs_projection` and `candidate_count=327`.
- `python -m src.app mcp-ingest-docs --dump-json` refreshed the bounded project
  document cartridge after parking docs were updated: `380` semantic objects
  and `1398` relations.
- `python -m src.app mcp-score-tasks --dump-json` refreshed the real-doc
  builder score artifact with aggregate score `0.87`, accepted.
- `python -m unittest discover -s tests` passed with 89 tests.
- `python -m compileall src tests` passed.
- `python -m src.app project-query --query "class object function" --dump-json`
  emitted a shared interaction capture with `CommandEnvelope`,
  `ToolResultEnvelope`, projection frame, and usefulness report; it selected
  `python_docs_projection` and recorded `ngraph.project.query` in
  `data/mcp_inspection/history.sqlite3`.
- `python -m src.app mcp-tools --dump-json` listed both
  `ngraph.analysis.traverse_cartridge` and `ngraph.project.query`.
- `python -m src.app mcp-history-view --dump-json --history-limit 3` summarized
  the project-query record with `selected_layer=python_docs_projection` and
  `candidate_count=327`.
- `python -m unittest discover -s tests` passed with 85 tests.
- `python -m compileall src tests` passed.
- forbidden runtime/source-name scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, `NodeWALKER`,
  `docling`, `Docling`, or source-branded English lexicon component names.
- app-owned Markdown/text documentation scan over `README.md` and `_docs/`
  found no active source-branded English lexicon component names. Historical
  app-journal entries remain append-only records and were corrected by a new
  journal entry instead of rewritten.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=41`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=19`, `total_violations=0`.
- `python -m src.app project-query --query "class object function" --dump-json`
  selected `python_docs_projection` and surfaced `class Foo(object): pass` as
  the top candidate while preserving English lexical and project-local
  candidates.
- `python -m src.app mcp-ingest-docs --dump-json` was rerun after parking docs
  were updated so the project-local cartridge includes the current park state.
- `python -m src.app status` now reports
  `active_tranche=Projection Scoring And MCP Inspection: Shared Command Spine`
  and `next_tranche=UI Command Spine Pilot`.
- `python -m unittest tests.test_english_lexicon tests.test_context_projection
  tests.test_scaffold` passed with 16 tests.
- `python -m src.app ingest-lexicon --reset --dump-json` rebuilt the sanitized
  English lexical baseline cartridge with `102104` entries, `102104` semantic
  objects, `117553` relations, and `102104` provenance records at
  `data/cartridges/base_english_lexicon.sqlite3`.
- The old generated source-branded cartridge file was removed after the
  sanitized cartridge was verified.
- `python -m src.app lookup-lexicon --query object --dump-json` returned the
  expected `object` headword from
  `data/cartridges/base_english_lexicon.sqlite3`.
- `python -m src.app project-query --query "object" --dump-json` returned all
  three context layers: `english_lexical_prior`, `python_docs_projection`, and
  `project_local_docs`.
- `python -m src.app project-query --query "for element in iterable return False"
  --dump-json` selected `python_docs_projection` and surfaced the
  `all(iterable)` / `any(iterable)` code examples.
- `python -m src.app project-query --query "semantic object provenance relations"
  --dump-json` selected `project_local_docs` and surfaced project-local
  semantic object / provenance / relations doctrine.
- 2026-04-22 reassessment read the builder constraint contract, inspected the
  Python docs projection code, and confirmed the tranche remains project-owned
  with no runtime dependency on `.parts`, `.dev-tools`, or Docling.
- `python -m unittest tests.test_python_docs_corpus` passed with 5 tests.
- `python -m src.app ingest-python-docs --reset --dump-json` rebuilt the
  bounded Python docs projection cartridge with `387` semantic objects,
  `2170` relations, `90` API signatures, `106` code examples, `77` doctest
  examples, `42` grammar rules, and `183` AST-parseable snippets.
- `python -m src.app mcp-ingest-docs --dump-json` refreshed the bounded project
  document cartridge with `334` semantic objects and `1230` relations.
- A bounded layered probe over `object`, `class object function`,
  `for element in iterable return False`, and
  `semantic object provenance relations` showed useful layer separation:
  English lexical layer returns lexical headword/definition anchors, Python docs returns
  API/code/grammar anchors such as `class Foo(object): pass`,
  `issubclass(class, classinfo)`, and `all(iterable)`/`any(iterable)` examples,
  while project docs return project-local `SemanticObject`/provenance doctrine.
- Interpretation: the current prototype supports separable context lenses and
  justifies the next context projection tranche. It does not yet implement true
  query rebinding, layer arbitration, embeddings, or final semantic grounding.
- `python -m unittest discover -s tests` passed with 80 tests.
- `python -m compileall src tests` passed.
- forbidden runtime reference scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, `NodeWALKER`,
  `docling`, or `Docling` references.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=40`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=18`, `total_violations=0`.
- `_docs/THOUGHTS_FOR_NEXT_SESSION.md` added as a non-authoritative research
  and next-session handoff document.
- `python -m unittest tests.test_python_docs_corpus` passed with 5 tests.
- `python -m src.app ingest-python-docs --reset --dump-json` built the bounded
  Python docs projection cartridge with `387` semantic objects, `2170`
  relations, `90` API signatures, `106` code examples, `77` doctest examples,
  `42` grammar rules, and `183` AST-parseable snippets.
  Full-tree and broad prose extraction are explicit via `--all-python-docs`
  and `--include-prose`.
- `python -m unittest discover -s tests` passed with 80 tests after parking the
  Python docs projection corpus tranche.
- `python -m compileall src tests` passed.
- forbidden runtime reference scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, `NodeWALKER`,
  `docling`, or `Docling` references.
- `python -m src.app ingest-lexicon --reset --dump-json` built
  `102104` lexical entries, `102104` semantic objects, and `117553` relations
  into `data/cartridges/base_english_lexicon.sqlite3`.
- `python -m src.app lookup-lexicon --query tortuous --dump-json` returned one
  `tortuous` candidate with `4` senses, `Astrol` domain label, and `4`
  usage-example candidates.
- `python -m src.app lookup-lexicon --query true-blue --dump-json` returned one
  `true-blue` candidate with the cross-reference `True blue, under Blue`.
- `python -m unittest tests.test_english_lexicon tests.test_persistence`
  passed with 14 tests.
- `python -m unittest discover -s tests` passed with 75 tests after parking the
  English lexical baseline tranche.
- `python -m compileall src tests` passed.
- forbidden runtime reference scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, or `NodeWALKER`
  references.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=37`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=17`, `total_violations=0`.
- `python -m unittest tests.test_seed_search tests.test_project_documents`
  passed with 7 tests.
- `python -m unittest tests.test_seed_search tests.test_project_documents
  tests.test_scaffold` passed with 11 tests.
- `python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json`
  emitted ranked candidates, selected seed metadata, registered traversal
  output, and a history record.
- user-facing seed-search inspector is running with display pid `135904`.
- `python -m unittest discover -s tests` passed with 67 tests after parking the
  traversal seed-search tranche.
- `python -m compileall src tests` passed.
- forbidden runtime reference scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, or `NodeWALKER`
  references.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=35`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=16`, `total_violations=0`.
- focused history-aware inspector tests passed during the tranche.
- `python -m src.app mcp-history-view --dump-json` emitted `summary_text`,
  compact `calls`, and raw history payload.
- `python -m src.app mcp-ingest-docs --dump-json` emitted selected document
  paths, object count, and `ngraph.analysis.traverse_cartridge` over the real
  project document set.
- `python -m src.app mcp-score-tasks --dump-json` over real project docs emitted
  aggregate score `0.93` and `meets_acceptance=true`.
- `python -m unittest discover -s tests` passed with 64 tests after parking the
  history-aware inspector tranche.
- `python -m compileall src tests` passed.
- forbidden runtime reference scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, or `NodeWALKER`
  references.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=34`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=15`, `total_violations=0`.
- `python -m compileall src tests` passed.
- `python -m src.app mcp-tools --dump-json` emitted the local registry with
  `ngraph.analysis.traverse_cartridge`.
- `python -m src.app mcp-inspect --dump-json` emitted a raw payload containing
  persisted `record_count`, `ngraph.analysis.traverse_cartridge`, and adapter
  aggregate score `0.93`.
- `python -m src.app mcp-history --dump-json --history-limit 1` emitted the
  persisted history path and recent record count.
- forbidden runtime reference scan over Python files in `src/` and `tests/`
  found no `.parts`, `.dev-tools`, `_BDHyper`, `Tripartite`, or `NodeWALKER`
  references.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `src/`: `files_scanned=31`, `total_violations=0`.
- `.dev-tools/_project-authority` `domain_boundary_audit` gate passed on
  `tests/`: `files_scanned=12`, `total_violations=0`.

## Boundary Incident

During Phase 1 cleanup, a broad `__pycache__` removal command also removed
cache folders under `.parts` and `.dev-tools`. The affected items were generated
Python cache directories, not source files, but the command still crossed the
contract's off-limits write boundary for reference/tool surfaces.

Mitigation going forward:

- cleanup commands must target `src/`, `tests/`, or another explicitly owned
  project runtime folder unless broader cleanup is approved
- `.parts` and `.dev-tools` must be excluded from cleanup and generated-file
  pruning commands
- future journal entries must record this as a tranche note, not hide it

