# Builder Directive

_Status: Active operational capsule_

This file is a compact working companion to `builder_constraint_contract.md`.
The contract remains authoritative. If this capsule and the contract ever
conflict, the contract wins.

## Prime Directive

Before meaningful implementation work, the builder shall read or consult:

- `_docs/builder_constraint_contract.md`
- `_docs/BUILDER_DIRECTIVE.md`
- `_docs/builder_constraint_index.yaml`
- relevant app journal entries or backlog records
- the active architecture/scaffold documents for the current tranche

The builder shall preserve the active constraint field across turns rather than
treating each prompt as an unconstrained task.

## Work Boundary

- The current project root is the only normal write domain.
- Project documents belong under `_docs/`, except `README.md` and `LICENSE.md`.
- Runtime code must not depend on sibling projects, `.parts`, `.dev-tools`,
  `_PARTS`, `_dev_tools`, or other sandbox-level reference locations.
- Reference sources may inform work only when re-homed and documented according
  to the contract.

## Planning Discipline

Before substantial work, identify:

- current tranche
- in-scope work
- explicit non-goals
- affected ownership domains
- likely files to touch
- verification plan
- journal/reporting needs

Prefer bounded tranches over broad rewrites. Preserve separation between
scaffold work, implementation work, integration work, cleanup, and polish.

## Architecture Discipline

- Preserve the scaffold and existing project geometry.
- `src/app.py` is the composition root and canonical app-state authority when
  app runtime work exists.
- UI-owned logic belongs under `src/ui/`.
- CORE-owned logic belongs under `src/core/`.
- Managers coordinate narrow adjacent domains; they do not absorb broad
  implementation logic.
- Orchestrators must remain bounded to UI-side or CORE-side authority.
- Do not create catch-all modules, hidden mixed ownership, or vague abstraction
  layers.

## Dependency And State Rules

- Prefer explicit routing through the declared hierarchy.
- Prefer message traversal over hidden cross-calls when using the runtime graph.
- Shared state must be explicitly owned.
- Local node state must remain narrow.
- The SQLite event ledger, if used, is an append-only dispatch trace unless full
  event-sourcing mechanics are actually implemented.

## Sourcing Rules

Preferred sourcing order:

1. original implementation inside the project
2. bounded rewrite informed by references
3. narrow structured extraction
4. larger transplant only under strict exception conditions

Any meaningful borrowed, extracted, or transplanted logic requires provenance
documentation under `_docs/` and a journal note.

## Code Quality Rules

- Use logging for application behavior; do not use `print()` as app output.
- Fail gracefully with useful diagnostics.
- Centralize configuration where practical.
- Avoid hidden globals and unexplained magic constants.
- Use typed structures where they clarify contracts.
- Add tests for meaningful behavior and risk.
- Clean temporary/dead files conservatively and record meaningful cleanup.

## Reporting Rules

After each meaningful phase, append an app journal entry recording:

- date/time and meaningful entry identifier
- changed files
- summary of what changed
- implementation notes or decisions
- testing performed
- deferred work, risks, or backlog items when applicable

## Pushback Rule

If a request risks correctness, contract compliance, structural integrity, or
long-term maintainability, the builder should surface the risk, clarify intent
when needed, and propose a stronger path rather than silently complying.
