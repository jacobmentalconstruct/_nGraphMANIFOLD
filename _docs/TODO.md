# TODO

_Status: Active continuation checklist, local host bridge parked_

This file is the human-readable next-work checklist. The app journal remains the
authoritative ledger, and `PROJECT_STATUS.md` remains the quick park marker.

## Just Completed

- [x] Local Host Bridge And Cross-Process Session Control

What that means:

- [x] bounded same-instance cross-process targeting now exists
- [x] the live host can publish and heartbeat a bridge session
- [x] `project-query` can target the already-open host
- [x] `mcp-search-seeds` can target the already-open host
- [x] the bridge still reuses the canonical command spine
- [x] the bridge did not force us into network/server architecture

## Proposed Next Tranche

- [ ] Post-Prototype Hardening And Expansion

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

- [ ] Define MCP inspection history retention/pruning policy

Why this first:

- inspection history is now central to stream, cockpit, host state, and bridge
  usefulness
- the bridge increases the value of clean session/history behavior
- this is the healthiest hardening move before we expand control surfaces

Current recommended framing:

```text
Active Reasoning:
  recent rolling trace, auto-pruned, operational, not sacred

Durable Evidence:
  accepted scores, journaled phase decisions, pinned/proven captures,
  preserved intentionally
```

## Next Work Queue

- [ ] Define retention/pruning policy for `data/mcp_inspection/history.sqlite3`
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
