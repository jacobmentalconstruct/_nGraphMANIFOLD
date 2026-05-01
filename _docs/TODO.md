# TODO

_Status: Active continuation checklist, visible host lifecycle hardening parked_

This file is the human-readable next-work checklist. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Just Completed

- [x] Visible Host Lifecycle Hardening

What that means:

- [x] bridged `mcp-search-seeds` now uses the medium bridge timeout policy
      instead of the flat five-second default
- [x] the Status panel exposes the seed-search bridge timeout alongside
      builder/projection bridge timeouts
- [x] the Tool Registry panel readback now renders the current `tools` payload
      shape as well as the older `registrations` shape
- [x] stale session manifests are no longer deleted by passive live-session
      reads, so the visible host owner can recover them
- [x] bridge request processing refreshes the owner heartbeat before and after
      dispatch, so long-running visible commands do not break follow-up calls
- [x] focused host bridge/workspace regression tests are green
- [x] full test suite is green at 138 tests

- [x] Scored Human-Facing Inspection Usefulness Fixture

What that means:

- [x] `src/core/coordination/human_visibility_scoring.py` defines four
      pre-committed visibility fixtures
- [x] `python -m src.app mcp-score-visibility --dump-json` writes
      `data/mcp_inspection/human_visibility_scores.json`
- [x] projection, seed, promotion, status/tool, and score visibility are
      scored across existing host/readback surfaces
- [x] current real-project human visibility score is `0.96`, accepted
- [x] full test suite is green at 136 tests
- [x] no embeddings, vector views, cartridge rewrite, global event bus, or
      hidden app-state ingestion was introduced

## Recent Tranches

- [x] Lens-Guided Companion Evidence Evaluation

What that means:

- [x] app-owned side retrieval/evidence harnesses now live under
      `src/core/coordination/` and are callable through `src.app`
- [x] fixed-lens bag, fixed-lens comparison, adaptive deterministic weighting,
      and baseline-plus-companion comparison all write project-owned artifacts
      under `data/mcp_inspection/`
- [x] adaptive weight rotation of the current deterministic scorer did not beat
      the baseline
- [x] baseline seed plus auto-lens companion bag improved supporting evidence
      coverage without degrading the baseline top choice
- [x] the current carry-forward conclusion is bounded:
      keep baseline as primary chooser and treat the bag as companion context

- [x] Protected Baseline And Semantic Docking Doctrine

What that means:

- [x] deterministic English lexical, Python docs, and project-doc cartridges
      are recorded as protected local evidence in
      `CANONICAL_DETERMINISTIC_BASELINE.md`
- [x] semantic docking is now subordinate to baseline preservation
- [x] future embedding output is limited to derived vector views and evidence
      candidates until explicit relations are promoted
- [x] future baseline manifest contract is recorded for
      `data/cartridges/baseline_manifest.json`
- [x] no schema migration, vector generation, Ollama embedding call, or
      cartridge rewrite was performed in this doctrine tranche

- [x] Disambiguation Bias Repair

What that means:

- [x] live-substrate disambiguation falsifier panel exists in `tests/test_disambiguation_panel.py`
      with ten pre-committed query/expected-layer assertions, passing 10/10
- [x] `src/core/coordination/context_projection.py` now suppresses headword-match dominance
      when the headword is a project or python frame hint
- [x] english single-term layer bonus weakened when the term is a frame hint
- [x] python graduated layer boost weakens for ambiguous (project+python) terms
- [x] project graduated layer boost climbs for short queries when at least one project hint is present
- [x] `bridge` added to PROJECT_HINTS so `host_bridge` is recognized at the term level
- [x] full suite green at 133 tests; builder-task score holds at 0.93; projection arbitration holds at 0.96
- [x] between-tranche realignment artifacts recorded in journal: falsifier fixture, doctrine note
      ("foundation sound, bend localized"), contract amendment motion ("bounded substantive non-goal
      re-examination mechanic", awaiting approval), and a follow-up doctrine note
      ("motion mechanic has no active case")

- [x] Bridge Transport And Profile Discipline

What that meant:

- [x] `status --dump-json` exposes bridge transport kind, runtime state, and profile manifest
- [x] builder-task scoring reports corpus object/relation counts and elapsed runtime
- [x] projection scoring reports elapsed runtime
- [x] project-doc profile switching purges out-of-profile docs instead of carrying them forward
- [x] measured comparison supports the current hold decision:
      keep file-backed bridge, keep `core` and `expanded`

## Current Active Tranche

- [x] Post-Prototype Hardening And Expansion

Current interpretation:

- harden what now exists before broadening scope
- avoid turning transport into the architecture
- avoid reopening prototype-definition questions we have already settled

## What Shifted

- [x] We are no longer proving whether the bounded prototype can exist
- [x] We are now hardening a prototype that already works and is inspectable
- [x] We are moving from adding visibility surfaces to clarifying surface ownership
- [x] We are moving from accumulating inspection history to defining a rolling trace
- [x] We are moving from "can the bridge work?" to "how does the bridge stay bounded?"
- [x] We are keeping interaction envelopes inspection-only until a later truth-surface decision

## Immediate Next Step

- [x] Add a bounded loop-safeguard review surface now that bridge/profile policy is explicit
- [x] Use the loop-safeguard review result to choose exactly one controlled expansion slice
- [x] Add explicit bridge transport maintenance for the first loop-review warning
- [x] Record a project-owned disambiguation falsifier panel against the live cartridges
- [x] Repair the projection scoring bias surfaced by the falsifier (panel now passes 10/10)
- [x] Park the visibility/introspection boundary before opening the human-facing fixture
- [x] Record the protected deterministic baseline doctrine before opening any
      embedder/vector docking work
- [x] Open and complete the Scored Human-Facing Inspection Usefulness Fixture tranche
- [x] Open visible host lifecycle hardening after live monitor smoke surfaced
      seed-search bridge timeout and tool-panel text projection gaps

Why this next:

- the substrate's central disambiguation claim is now backed by a falsifier rather than a docs aspiration;
  "stable" going forward means falsifier-backed, not just absence of complaints
- the deferred backlog item "scored human-facing inspection usefulness fixture" has been waiting on
  exactly this kind of clearer scoring discipline; it is the cleanest next controlled-expansion slice
- queued behind it: extend falsifier-backed claim discipline to additional substrate properties
  (a second pre-committed panel for a different claim the docs make)
- the gate-lift motion remains drafted in the journal as a proposal-without-current-case;
  no contract action is pending unless a future tranche surfaces a real lock-vs-progress conflict
- the visibility/introspection discussion clarified a sibling opportunity without changing
  the current tranche: runtime monitoring events may later become gated inspection evidence,
  but they do not become semantic cartridge truth and they do not enter hidden substrate memory

Current recommended framing:

```text
Falsifier-Backed Claim Discipline:
  every claim the substrate makes about itself should be testable against
  pre-committed expectations recorded as a project artifact

Scored Human-Facing Inspection Usefulness:
  measure whether the operator-facing inspection surfaces are useful in
  the way the human operator expects, not only whether they emit data

Visibility / Introspection Boundary:
  align the human operator and builder around shared inspection evidence
  while keeping runtime monitoring, logging, and app-state introspection
  gated, explicit, and outside semantic cartridge truth
```

## Next Work Queue

- [x] Decide whether the next controlled expansion should be a scored
      human-facing inspection usefulness fixture or a narrow shared-command
      action expansion — chose the inspection usefulness fixture
- [x] Classify the proposed runtime logging/introspection spine as future
      gated monitoring work, not current substrate truth or current fixture
      implementation
- [x] During the human-facing fixture, score whether the operator and builder agent can
      compare the same inspection evidence from existing surfaces without
      relying on private or inferred app state
- [ ] Decide whether to grow the disambiguation falsifier panel beyond ten
      pre-committed queries, or hold at ten and add a second panel for a
      different substrate claim
- [ ] Revisit journal importance scale calibration (user-deferred background
      thread; recorded as journal entry 49). Builder should not initiate; user
      will surface when ready.
- [ ] Decide whether command/result SemanticObjects remain inspection-only or become persisted truth later
- [ ] Decide whether the current `core` / `expanded` project-doc profile split is enough for now
- [ ] Decide whether the bridge should remain file-backed or later move to a
      thinner local IPC transport
- [ ] Decide whether operator metadata should later support taxonomy or richer structure beyond label / reason / note
- [ ] Review the loop-frailty side conversation and distill only the grounded safeguards worth keeping
- [ ] If retrieval work reopens later, decide whether baseline seed plus
      companion bag should graduate from side harness to a first-class
      inspection surface after the current next tranche is complete
- [ ] Keep docs, score artifacts, and journal continuity current while hardening
- [ ] Add the future generated baseline manifest helper before any persisted
      vector-view pilot
- [x] Rerun visible monitor lifecycle smoke after the host lifecycle hardening patch

## Visible Horizon

### Near Horizon

- [ ] Hardening: retention, bridge discipline, visibility filtering, lifecycle cleanup
- [x] Visible lifecycle hardening: medium seed-search bridge policy and
      tool-registry panel text readback
- [ ] Protected baseline: manifest counts and hashes before persisted vector views
- [x] Human visibility: score shared inspection usefulness across cockpit,
      stream, history, host workspace, and panel readback
- [ ] Visibility boundary: keep runtime monitoring/introspection gated and
      inspection-only if it is later added

### Medium Horizon

- [ ] Controlled expansion of shared-command actions
- [ ] Controlled expansion of bounded corpora and tuning
- [ ] Consider a structured runtime event/logging spine only after the
      human-facing inspection fixture defines which evidence actually helps

## Proposed Next Tranche

- [x] Loop Safeguards And Controlled Expansion Review
- [x] Scored Human-Facing Inspection Usefulness Fixture
- [x] Visible Host Lifecycle Hardening
- [ ] Choose next bounded slice: traversal seed-selection falsifier panel or
      baseline manifest helper before vector-view work

### Later Horizon

- [ ] Truth-surface decision for interaction-envelope persistence
- [ ] Decide whether a gated runtime event/logging spine should become a
      queryable app-monitoring surface, while remaining outside semantic
      cartridge truth
- [ ] Real MCP wrapper / broader platform decisions only if justified

## Active Non-Goals

- [ ] No embeddings unless a separate tranche authorizes them after baseline
      protection is preserved
- [ ] No repo-wide scan as a default ingestion path
- [ ] No real network MCP server
- [ ] No FastAPI / websocket transport by default
- [ ] No cartridge merge
- [ ] No hidden interaction persistence
- [ ] No hidden app-state ingestion
- [ ] No runtime monitoring/logging events promoted to semantic cartridge truth
- [ ] No broad dashboard rewrite
- [ ] No new graph visualization

These stay unchecked on purpose. They are guardrails, not pending promises.

## Backlog

- [ ] Add search-scored traversal tuning after lexical layering has a baseline
- [ ] Decide whether the bounded document set should expand beyond the current
      four docs
- [ ] Decide if and when to wrap the local registry in a real MCP protocol server
- [ ] Decide whether the raw dictionary text should be compared against the
      alpha-array JSON for richer example extraction
- [ ] Decide when command/result SemanticObject projections should become
      persisted cartridge truth instead of inspection-only adapters
- [ ] Decide if and when runtime logging records should be normalized into a
      gated event spine for app monitoring and cross-surface inspection
- [ ] Decide which UI actions beyond `project-query` should join the shared
      command spine after the first button/control pilot
- [ ] Decide whether the bridge should stay file-backed or later move to a
      thinner local IPC transport

## Short Sync

If reopening the project quickly, the shortest accurate read is:

```text
prototype substrate: stable
visibility layer: stable
local host bridge: stable in bounded form
rolling trace + promotion controls: stable
operator metadata: stable
panel readback + shared command expansion: stable
bridge timeout policy: stable
bridge/profile discipline: explicit first answer
loop-review gate: implemented
bridge maintenance: implemented
loop-review status: ready_for_controlled_expansion_review
disambiguation falsifier panel: 10/10 passing (project-owned)
projection scoring rebalance: landed (no architectural lock lifted)
contract amendment motion: drafted, no active case, awaiting approval
journal importance scale: calibration question recorded (entry 49), user-deferred
human visibility score: 0.96 accepted
visible lifecycle hardening: seed-search bridge timeout + tool panel readback patched
visible monitor smoke: seed search, immediate tool registry follow-up, seed panel, tools panel, and status panel all passed
next tranche: choose traversal seed-selection falsifier panel or baseline manifest helper
```
