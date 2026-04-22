# Builder Planning Checklist

_Status: Active planning aid_

Use this checklist before meaningful implementation work. It is derived from
`builder_constraint_contract.md` and `builder_constraint_index.yaml`.

## 1. Rehydrate Context

- Read or consult the contract capsule in `BUILDER_DIRECTIVE.md`.
- Check `builder_constraint_index.yaml` for structured planning rules.
- Review relevant app journal entries, backlog items, and architecture docs.
- Identify the active scaffold and current project root.

## 2. Declare The Tranche

- Current tranche:
- In scope:
- Explicit non-goals:
- Clean completion point:
- Expected changed files:

## 3. Check Boundaries

- Work stays inside the current project root.
- Project docs stay under `_docs/`.
- Runtime code does not depend on sibling folders or sandbox reference folders.
- Any external reference logic is re-homed and documented.
- Any material boundary deviation has explicit user approval.

## 4. Check Ownership

- Each touched component has one clear owner.
- UI logic remains under UI ownership.
- CORE logic remains under CORE ownership.
- Managers coordinate narrowly and do not absorb domain implementation.
- Orchestrators are bounded to UI-side or CORE-side authority.
- No new catch-all, junk-drawer, or mixed-concern modules are introduced.

## 5. Check Dependencies And State

- `src/app.py` remains the composition root when runtime work is involved.
- Shared state has explicit ownership.
- Routing follows the declared hierarchy.
- Runtime graph messages/routes are explicit when graph behavior is involved.
- SQLite event logging is represented as a dispatch ledger unless stronger
  event-sourcing mechanics exist.

## 6. Check Sourcing

- Original implementation is preferred.
- Bounded rewrite is preferred over extraction when practical.
- Structured extraction is narrow, owned, and necessary.
- Larger transplant has a contract-compliant justification.
- Provenance and journal notes are planned for meaningful borrowed logic.

## 7. Check Quality

- Application behavior uses logging, not `print()`.
- Failure handling is graceful and diagnosable.
- Configuration is centralized where practical.
- Important constants and mutable state are explicit.
- Types or schemas are used where they clarify subsystem contracts.
- Tests or verification steps match the risk of the change.

## 8. Check Reporting

- Meaningful phase gets a journal entry.
- Changed files are recorded.
- Testing is summarized.
- Deferred cleanup, risks, or next steps are placed in the app journal backlog
  when applicable.

## 9. Pushback Gate

Pause and surface the issue when the requested path appears to risk:

- correctness
- structural integrity
- contract compliance
- vendorable independence
- ownership clarity
- maintainability
- safe cleanup
