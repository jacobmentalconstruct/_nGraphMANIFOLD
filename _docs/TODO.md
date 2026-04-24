# TODO

_Status: Active continuation checklist, hardening slice parked_

This file is the human-readable next-work checklist. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Just Completed

- [x] Operator Metadata Decisions

What that means:

- [x] promoted durable evidence now supports label / reason / note metadata
- [x] `mcp-promote-call` accepts `--label`, `--reason`, and `--note`
- [x] host workspace promotion controls now capture compact operator metadata
- [x] history, stream, cockpit, and host panels now expose operator metadata visibly
- [x] operator metadata remains inspection-history evidence, not semantic cartridge truth

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

- [ ] Decide whether the file-backed bridge should remain the local transport for the next band or later move to thinner IPC

Why this next:

- operator metadata now exists, so the next ambiguity is transport discipline rather than evidence shape
- the expanded doc profile is useful but heavier, which makes bridge/runtime discipline the next practical pressure
- the project now needs one clean answer about whether file-backed local transport remains the right bounded choice for the next band

Current recommended framing:

```text
Bridge Discipline:
  local, inspectable, file-backed, bounded, subordinate

Profile Discipline:
  keep `core` / `expanded` explicit, only widen scope if usefulness
  or continuity clearly justify the added weight
```

## Next Work Queue

- [ ] Decide whether command/result SemanticObjects remain inspection-only or become persisted truth later
- [ ] Decide whether the current `core` / `expanded` project-doc profile split is enough for now
- [ ] Decide whether the bridge should remain file-backed or later move to a
      thinner local IPC transport
- [ ] Decide whether operator metadata should later support taxonomy or richer structure beyond label / reason / note
- [ ] Keep docs, score artifacts, and journal continuity current while hardening

## Visible Horizon

### Near Horizon

- [ ] Hardening: retention, bridge discipline, visibility filtering, lifecycle cleanup

### Medium Horizon

- [ ] Controlled expansion of shared-command actions
- [ ] Controlled expansion of bounded corpora and tuning

## Proposed Next Tranche

- [ ] Bridge Transport And Profile Discipline

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
next step: decide bridge/profile discipline cleanly, then widen scope in a controlled way
```
