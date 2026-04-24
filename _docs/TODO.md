# TODO

_Status: Active continuation checklist, hardening slice parked_

This file is the human-readable next-work checklist. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Just Completed

- [x] Rolling Trace Retention And Bridge Cleanup

What that means:

- [x] unpinned interaction history now uses a bounded rolling trace
- [x] score-referenced call ids are pinned as durable evidence
- [x] host, stream, cockpit, and history payloads expose retention state
- [x] stale bridge request/response/session files are cleaned conservatively
- [x] the bridge remains file-backed and subordinate to command/state
- [x] the hardening pass did not create a new truth store

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

- [ ] Decide whether `mcp-stream` and `mcp-cockpit` need filtering by tool/layer

Why this next:

- retention and bridge cleanup now exist, so the next question is how much
  live visibility should be filtered before the surfaces become noisy
- the surfaces now have declared ownership, which makes filtering a bounded
  refinement rather than a blind UI expansion
- this is the healthiest next step before adding more commands or more corpus
  scope

Current recommended framing:

```text
Active Reasoning:
  recent rolling trace, auto-pruned, operational, not sacred

Durable Evidence:
  accepted scores, journaled phase decisions, pinned/proven captures,
  preserved intentionally
```

## Next Work Queue

- [ ] Decide whether operator-facing pin/promotion controls are needed beyond score-artifact pinning
- [ ] Decide whether the bridge should remain file-backed or later move to a
      thinner local IPC transport
- [ ] Decide whether `mcp-stream` and `mcp-cockpit` need filtering by tool/layer
- [ ] Decide whether more UI actions should join the shared command spine
- [ ] Decide whether command/result SemanticObjects remain inspection-only or
      become persisted truth later
- [ ] Decide whether to expand the bounded project-document set beyond the
      current four docs
- [ ] Keep docs, score artifacts, and journal continuity current while hardening

## Visible Horizon

### Near Horizon

- [ ] Hardening: retention, bridge discipline, visibility filtering, lifecycle cleanup

### Medium Horizon

- [ ] Controlled expansion of shared-command actions
- [ ] Controlled expansion of bounded corpora and tuning

## Proposed Next Tranche

- [ ] Controlled Expansion And Visibility Filtering

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
next step: harden history and bridge discipline before expanding scope
```
