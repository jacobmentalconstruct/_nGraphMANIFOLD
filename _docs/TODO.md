# TODO

_Status: Active continuation checklist, hardening slice parked_

This file is the human-readable next-work checklist. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Just Completed

- [x] Bridge Transport And Profile Discipline

What that means:

- [x] `status --dump-json` now exposes bridge transport kind, runtime state, and profile manifest
- [x] builder-task scoring now reports corpus object/relation counts and elapsed runtime
- [x] projection scoring now reports elapsed runtime
- [x] project-doc profile switching now purges out-of-profile docs instead of carrying them forward
- [x] measured comparison now supports the current hold decision:
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

- [ ] Reassess the larger collaboration loop and its failure modes now that bridge/profile policy is explicit

Why this next:

- bridge/profile discipline now has a measured first answer
- the next uncertainty is not transport mechanics but loop integrity and where controlled expansion should happen next
- this is the right moment to pressure-test the collaboration loop before we widen scope again
- journal parks now also have a clearer high-signal shape for lessons learned,
  which should help future loop reviews stay grounded instead of impressionistic

Current recommended framing:

```text
Loop Safeguards:
  keep current-anchor resolution, traversal authority, scoring clarity,
  and doc/runtime sync visible enough that the build loop does not self-drift

Controlled Expansion:
  widen only where the loop still remains legible, testable, and contract-safe
```

## Next Work Queue

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
next step: reassess loop safeguards cleanly, then widen scope in a controlled way
```
