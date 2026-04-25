# TODO

_Status: Active continuation checklist, hardening slice parked_

This file is the human-readable next-work checklist. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Just Completed

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

## Recent Tranches

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
- [ ] Open the Scored Human-Facing Inspection Usefulness Fixture tranche

Why this next:

- the substrate's central disambiguation claim is now backed by a falsifier rather than a docs aspiration;
  "stable" going forward means falsifier-backed, not just absence of complaints
- the deferred backlog item "scored human-facing inspection usefulness fixture" has been waiting on
  exactly this kind of clearer scoring discipline; it is the cleanest next controlled-expansion slice
- queued behind it: extend falsifier-backed claim discipline to additional substrate properties
  (a second pre-committed panel for a different claim the docs make)
- the gate-lift motion remains drafted in the journal as a proposal-without-current-case;
  no contract action is pending unless a future tranche surfaces a real lock-vs-progress conflict

Current recommended framing:

```text
Falsifier-Backed Claim Discipline:
  every claim the substrate makes about itself should be testable against
  pre-committed expectations recorded as a project artifact

Scored Human-Facing Inspection Usefulness:
  measure whether the operator-facing inspection surfaces are useful in
  the way the human operator expects, not only whether they emit data
```

## Next Work Queue

- [x] Decide whether the next controlled expansion should be a scored
      human-facing inspection usefulness fixture or a narrow shared-command
      action expansion — chose the inspection usefulness fixture
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
- [ ] Keep docs, score artifacts, and journal continuity current while hardening

## Visible Horizon

### Near Horizon

- [ ] Hardening: retention, bridge discipline, visibility filtering, lifecycle cleanup

### Medium Horizon

- [ ] Controlled expansion of shared-command actions
- [ ] Controlled expansion of bounded corpora and tuning

## Proposed Next Tranche

- [ ] Loop Safeguards And Controlled Expansion Review

### Later Horizon

- [ ] Truth-surface decision for interaction-envelope persistence
- [ ] Real MCP wrapper / broader platform decisions only if justified

## Active Non-Goals

- [ ] No embeddings unless a separate tranche authorizes them
- [ ] No repo-wide scan as a default ingestion path
- [ ] No real network MCP server
- [ ] No FastAPI / websocket transport by default
- [ ] No cartridge merge
- [ ] No hidden interaction persistence
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
next tranche: Scored Human-Facing Inspection Usefulness Fixture
```
