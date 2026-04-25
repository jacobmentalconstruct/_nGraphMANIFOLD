# Prototype Tuning And Scoring

_Status: Prototype completion gate accepted; disambiguation bias repair parked_

This document records the first post-prototype tuning harness. It is subordinate
to `builder_constraint_contract.md`.

## Purpose

The tuning harness evaluates whether the completed prototype spine is useful to
a builder or agent.

It does this by running repeatable builder-task fixtures through:

```text
source content
  -> semantic objects
  -> relation enrichment
  -> cartridge persistence
  -> traversal
  -> execution report
  -> MCP usefulness scoring
```

## Runtime Owner

- `src/core/coordination/prototype_scoring.py`
- `src/core/coordination/builder_task_scoring.py`
- `src/core/coordination/history_inspector.py`
- `src/core/coordination/seed_search.py`
- `src/core/coordination/seed_fitness.py`
- `src/core/coordination/context_projection_scoring.py`
- `src/core/coordination/host_workspace.py`
- `src/core/coordination/host_bridge.py`

This is a local evaluation harness, not a network adapter or MCP server.

## Default Fixtures

- `relation_evidence_trace`
- `execution_report_trace`
- `persistence_round_trip`

Each fixture uses a temporary semantic cartridge during tests and scoring.

## Current Scores

Acceptance threshold: `0.7`

| Fixture | Score | Accepted |
| --- | ---: | --- |
| `relation_evidence_trace` | `0.91` | yes |
| `execution_report_trace` | `0.91` | yes |
| `persistence_round_trip` | `0.91` | yes |

The current recommendation is to expose or adapt:

- `analysis.traverse_cartridge`

## Real Builder-Task Scores

Real project-document scoring now runs through:

```bat
python -m src.app mcp-score-tasks --dump-json
```

Current real-project score:

| Run | Score | Accepted |
| --- | ---: | --- |
| real project docs | `0.93` | yes |

Current real tasks:

- `current_tranche_lookup`
- `mcp_surface_lookup`
- `strangler_next_work_lookup`
- `operator_command_lookup`

The history-aware inspector now summarizes recent calls and keeps raw JSON:

```bat
python -m src.app mcp-history-view
```

Seed search can now select traversal seeds before calling the registered tool:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json
```

Recent query/response captures can be inspected as a formatted stream:

```bat
python -m src.app mcp-stream
```

The stream is derived from the same MCP inspection history used by the tuning
harness. It is useful for watching scoring and query-projection life cycles in
order, but it is not a separate scoring store.

Projection-candidate visibility and the unified cockpit now extend that same
inspection path:

```bat
python -m src.app project-query --query "class object function" --dump-json
python -m src.app mcp-cockpit --dump-json
```

The first command verifies that `project-query` exposes `selected_flow`; the
second verifies that the cockpit can assemble latest score artifacts, latest
projection, latest builder seed, and recent stream records into one read-only
payload.

`python -m src.app ui` is now a shared-host workspace over the same tuning
surfaces. It renders stream, active projection, active seed flow, score
summaries, and Raw JSON from one live in-process host snapshot rather than
rebuilding separate ad hoc views.

The local host bridge now lets opt-in external commands target that already-open
host:

```bat
python -m src.app project-query --query "class object function" --use-host-bridge
python -m src.app mcp-search-seeds --query "Current Park Point" --use-host-bridge
```

That means the tuning loop can now evaluate not only whether the result is
useful, but whether the live host session becomes more legible when the command
is delivered from outside the UI process.

The current bounded tuning pass also now covers the shared-command expansion
surfaces:

```bat
python -m src.app status --dump-json
python -m src.app mcp-tools --dump-json
python -m src.app mcp-score-tasks --dump-json
python -m src.app project-query-score --dump-json
python -m src.app loop-review --dump-json
python -m src.app mcp-bridge-maintenance --dump-json
```

Current results remain stable:

- `status`: healthy shared-dispatch response
- `mcp-tools`: healthy shared-dispatch response
- builder-task score: `0.93`, accepted
- projection arbitration score: `0.96`, accepted
- loop-review: `ready_for_controlled_expansion_review`
- bridge maintenance: removed `2` stale requests and `1` stale response in the
  current real-project run using the default retention window

Controlled expanded-doc profile:

- `python -m src.app mcp-ingest-docs --project-doc-profile expanded --dump-json`
  rebuilt the project-doc cartridge to `877` objects / `3280` relations
- `python -m src.app mcp-score-tasks --project-doc-profile expanded --dump-json`
  remained accepted at `0.93`
- `python -m src.app mcp-search-seeds --project-doc-profile expanded --query "Current Park Point" --dump-json`
  remained accepted at `0.93`

Interpretation:

- the expanded profile gives a wider project-local doctrine surface without
  degrading the current builder-task score
- it does, however, take materially longer to run
- that runtime cost is now part of bridge policy and operator experience, not
  just a performance footnote
- the bridge policy is now explicit:
  - global default remains `5000 ms`
  - builder-task scoring uses a heavy command-aware bridge default
  - projection scoring uses a medium command-aware bridge default
  - `--bridge-timeout-ms` remains available as a caller-owned override
  - bridged JSON payloads now report the effective policy through `_bridge`

Recent measured comparison:

| Profile | Objects | Relations | Score | Accepted | Elapsed |
| --- | ---: | ---: | ---: | --- | ---: |
| `core` | `605` | `2251` | `0.93` | yes | `60093 ms` |
| `expanded` | `879` | `3288` | `0.93` | yes | `84682 ms` |

The important hardening note is not just the difference in size. It is that
the profile boundary now actually holds: switching from `expanded` back to
`core` purges out-of-profile docs from the cartridge instead of carrying them
forward silently.

## Disambiguation Falsifier Panel

A project-owned falsifier panel for the substrate's central context-conditioned
disambiguation claim is now in place at:

```text
tests/test_disambiguation_panel.py
```

The panel records ten pre-committed query/expected-layer pairs and asserts that
the live arbitrated layer matches the pre-committed expectation for each query.
The panel is the new acceptance gate for the disambiguation claim: "stable" now
means "falsifier-backed" rather than "no current complaints."

Initial panel run reported 5/10 failures with a consistent headword-match bias
toward English. The Disambiguation Bias Repair tranche then made a localized
scoring rebalance in:

```text
src/core/coordination/context_projection.py
```

The five coordinated edits are:

- `bridge` added to `PROJECT_HINTS` so `host_bridge` is recognized at the term
  level
- `_english_score` headword bonus self-suppresses by `-7.0` when the headword is
  in `PROJECT_HINTS` or `PYTHON_HINTS`, with evidence tag
  `headword_suppressed_by_frame_hint`
- `_layer_score` English single-term layer bonus drops from `+2.0` to `+0.5`
  when the term is a frame hint; the `+2.0` still applies for pure English
  single-term queries
- `_layer_score` Python branch graduates: pure Python hints get the full `+6/+3`
  boost, ambiguous-only hints (in both `PYTHON_HINTS` and `PROJECT_HINTS`) get
  `+1`
- `_layer_score` project branch climbs to `+6.0` (from `+3.0`) for short queries
  (`len(terms) <= 2`) when at least one project hint is present, encoding
  "inside this project, short queries default to project frame"

After the rebalance the panel passes 10/10. The full suite remains green at
133 tests. Builder-task and projection arbitration scores are unchanged at
`0.93` and `0.96` respectively.

The repair is intentionally constrained:

- no embeddings were introduced
- no learning was introduced
- no cartridge merge was introduced
- no architectural lock was lifted
- the change is a layer-scoring rebalance, not a substrate redesign

The panel itself is parameter-fitted to its ten queries. New queries will find
new edges. The continuing discipline is to grow the panel against pre-committed
expectations, not against observed behavior. A separate panel for a different
substrate claim is queued behind the next tranche.

## Current Experimentation Doctrine

At this stage, an experiment is not accepted just because it "worked once."
The current doctrine is:

- fixture scores must remain acceptable
- real builder-task score must remain acceptable
- projection arbitration must remain acceptable
- the result must stay inspectable through the current visibility surfaces
- the result must remain contract-safe and boundary-clean

That means experiments are judged by both usefulness and legibility. A change
that produces an impressive local behavior but weakens inspection, boundary
discipline, or parked continuity is not a successful experiment.

The new hardening slice adds one more constraint to that doctrine:

- retained interaction history must remain bounded enough to stay vendorable
- durable evidence must remain intentional, not accidental
- bridge transport cleanup must not leave behind silent local debris
- filtered visibility must narrow attention without changing truth
- operator promotion controls may preserve evidence deliberately, but they must
  not circumvent score-linked durability guardrails or silently create new truth stores
- operator metadata may improve continuity, but it must remain bounded
  (`label`, `reason`, `note`) and remain part of inspection history rather than
  becoming cartridge truth or an uncontrolled taxonomy
- profile comparisons must remain honest about both usefulness and runtime
  weight; a smaller profile is only meaningful if the cartridge actually
  shrinks when selected
- loop-review should run before selecting a controlled expansion slice so the
  next action is grounded in declared project memory, semantic evidence, and
  explicit runtime policy
- bridge maintenance should be an explicit operator action when bridge debris
  is visible; loop-review may warn about debris but should not silently mutate
  transport state

## Interpretation

The seam is now tunable and scoreable through local code and real project docs.
It is still not a full MCP protocol server. Search-selected traversal seed
fitness passes the current builder-task score with aggregate `0.93`, and
context projection arbitration scores `0.96`. Projection candidate flow is now
visible through `selected_flow`, and the cockpit reduces the need to manually
stitch together history view, stream view, seed flow, and score artifacts.
The local host bridge proves that separate processes can target the already-open
host workspace while still reusing the same command model and dispatcher.

That is enough to treat the current bounded prototype as complete: structurally
correct, inspectable, and score-accepted, while still explicitly deferring
embeddings, merged cartridges, a real MCP server, and broad UI expansion.

## Next Scoring Work

- Keep the history-aware inspector, interaction stream, and cockpit attached to
  future scoring runs so query/response evidence remains visible.
- Decide whether rolling-trace retention should become an explicit scored gate
  rather than a currently-enforced lifecycle policy.
- Decide whether future scoring should include explicit human-facing inspection
  usefulness fixtures beyond the current qualitative tuning gate.
- Decide whether cockpit/stream filtering belongs in post-prototype hardening
  or should remain deferred.
- Decide whether operator-promoted durable evidence should eventually appear in
  scoring or remain purely operational memory.
- Decide whether bounded operator metadata is enough, or whether later tranches
  need a richer promotion taxonomy.
- Decide whether future tuning should explicitly score bridged host-session
  usefulness, not only query/projection correctness.
- Decide whether the disambiguation falsifier panel should grow beyond ten
  pre-committed queries, or hold at ten while a second panel for a different
  substrate claim is added.
- Treat falsifier-backed claim discipline as the new acceptance shape for the
  substrate's self-claims: "stable" means "covered by a pre-committed panel,"
  not "no complaints recently."
