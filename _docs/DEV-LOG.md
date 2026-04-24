# DEV-LOG

_This file is a generated mirror of the authoritative app journal. The source of truth remains_
`_docs/_journalDB/app_journal.sqlite3`_. Export generated: `2026-04-24T12:19:59Z`._

Append-only export order follows `journal_entries.id ASC`.

---

## Entry 1 - Builder Constraint Contract

- `created_at`: `2026-04-22T00:14:07Z`
- `updated_at`: `2026-04-22T00:14:07Z`
- `kind`: `contract`
- `status`: `active`
- `source`: `system`
- `author`: `project-authority-kit`
- `importance`: `10`
- `entry_uid`: `contract_8c991116f859`

### Body

# Builder Constraint Contract

_Status: Draft in progress_

## 0. Definitions

For the purposes of this contract, the following terms shall have the meanings below.

### 0.1 Sandbox root
The sandbox root is the top-level workspace directory accessible to the builder for the current conversation/project context. It may contain the active project folder, sibling project folders, `_PARTS/`, `_dev_tools/`, and other sandbox-level items.

### 0.2 Project root
The project root is the single active folder in which the current project is built. It is the only authorized write domain for the builder unless the user explicitly approves a broader scope.

### 0.3 Vendored / vendorable project
A vendored or vendorable project is a self-contained project that can be moved, reused, or handed off without depending on sibling projects, sandbox reference folders, or hidden local coupling.

### 0.4 Scaffold
The scaffold is the approved project folder/file structure supplied by the user, whether as a pre-created tree with placeholder files or as a declared file tree map to be instantiated.

### 0.5 Ownership
Ownership is the assignment of a file, module, component, or logic unit to one clear domain of responsibility within the project structure.

### 0.6 Domain
A domain is a coherent responsibility area such as UI, core processing, configuration, data handling, logging, testing, or another clearly bounded subsystem.

### 0.7 Owned component
An owned component is a file, module, class, service, helper, or other logic unit that belongs to one domain and is placed in the project according to that domain’s hierarchy and rules.

### 0.8 Manager
A manager is a coordination-layer component that supervises a very small cluster of adjacent domain responsibilities without absorbing their full implementation logic.

### 0.9 Orchestrator
An orchestrator is a higher-level coordination node that connects `app.py` to manager-level or subsystem-level behavior. Under this contract, orchestrators are bounded to a defined side or layer such as UI or CORE unless an explicitly justified additional orchestration layer is approved.

### 0.10 Structured hunk
A structured hunk is a bounded fragment of logic copied or extracted from a reference source that has clear ownership, clear purpose, and a maintainable size and can be re-homed into the local scaffold without dragging in unnecessary surrounding code.

### 0.11 Transplant
A transplant is the movement of a larger unit of logic, such as a major component, module, or whole script, into the current project when a smaller extraction or rewrite is not reasonably sufficient.

### 0.12 Re-home / re-homing
Re-homing is the process of integrating borrowed or extracted logic into the current project so that it becomes locally owned, properly placed, cleaned of accidental old-environment coupling, and structurally compliant with this contract.

### 0.13 Meaningful phase
A meaningful phase is a coherent unit of work substantial enough to justify project reporting, such as completion of a contract section, a subsystem implementation step, a structural refactor, a tooling addition, a cleanup pass, or another bounded set of related changes.

### 0.14 Graceful failure
Graceful failure means failing in a controlled and diagnosable way that preserves logs, avoids unnecessary corruption or loss, and leaves the project or application in the safest practical state under the circumstances.

### 0.15 Tool metadata
Tool metadata is the minimum identifying and usage information needed for another agent or user to understand what a tool does, how to invoke it, what scope it affects, and what constraints apply.

### 0.16 Reference source
A reference source is an approved non-target source such as `_PARTS/`, `_dev_tools/`, or project documentation that may inform implementation but may not become an undeclared runtime dependency.

### 0.17 Runtime control graph
A runtime control graph is an approved coordination/state-topology model rooted in `app.py` that may use bounded nodes, declared routes, isolated local state, root-owned shared state, and message traversal to manage runtime coordination. The detailed design of any specific runtime graph belongs in the application blueprint, not in this contract.

### 0.18 Contract compliance
Contract compliance means acting in a way that satisfies not only the literal wording of this document but also its structural intent: bounded ownership, clear hierarchy, clean dependency flow, safe sourcing, local vendorable build behavior, robust documentation, and conservative cleanup.

### 0.19 Constraint field
A constraint field is the stable set of project laws, records, boundaries, phase goals, and explicit non-goals that focus builder behavior across many inference cycles so the project is not treated as a fresh unconstrained task each turn.

### 0.20 Tranche
A tranche is a bounded work slice with a defined scope, explicit non-goals, and a clean stopping point such that scaffold work, implementation work, integration work, or cleanup work are not accidentally collapsed together.

### 0.21 Explicit non-goal
An explicit non-goal is a concretely stated thing that the builder shall not implement, redesign, or expand within the current tranche even if doing so appears tempting or locally convenient.

### 0.22 Builder memory
Builder memory is the project-side operational memory used to preserve doctrine, work history, TODO state, onboarding notes, and other builder-facing continuity records across sessions and contract resets. Under this project, builder memory belongs in the app journal rather than in runtime application data stores.

### 0.23 Shared registry
A shared registry is a small explicit state surface, typically file-backed, that records the current visible tool or viewer state so that the human operator and the builder can synchronize on the same query, mode, provider, selection, and recent actions.

### 0.24 Shared visible workflow
A shared visible workflow is a collaboration pattern in which the builder and the human synchronize to the same visible state surface before acting, reason from that same state, and then resynchronize after actions rather than relying on hidden or stale state.

---

This document defines the operational constraints, architectural boundaries, sourcing rules, and build discipline for the builder agent working inside the target project root.

## Contract Use Preamble

The builder shall read this contract before performing meaningful implementation work.

This contract is not a suggestion set, style guide, or optional preference list. It is the governing build discipline for the project unless the user explicitly overrides a specific point.

The builder shall use this contract to:
- interpret the user’s blueprint conservatively,
- preserve structural integrity,
- avoid unnecessary architectural drift,
- keep the project vendorable and self-contained,
- and maintain continuity across interrupted or multi-phase work.

When a conflict appears between convenience and contract discipline, the builder shall prefer contract discipline unless the user explicitly authorizes the deviation.

When a conflict appears between a surface-level user request and the long-term health of the application, the builder shall apply the pushback rule in this contract, clarify intent, warn about consequences, and propose a stronger path when appropriate.

The builder shall treat this contract as both:
- a permission boundary, and
- a quality floor.

Anything not clearly authorized here but materially affecting structure, dependency, sourcing, tooling scope, cleanup, or long-term maintainability requires explicit user approval.

---

## Builder Workflow Discipline Amendment

The builder shall operate under stable project laws rather than treating each
prompt as a new unconstrained universe.

This amendment formalizes the workflow discipline that has proven effective for
long-running architecture work in this project.

### A. Stable constraint-field rule

The builder shall preserve and work within the active constraint field for the
project.

The constraint field includes:
- the contract,
- active architecture doctrine,
- app journal builder-memory records,
- tranche boundaries,
- explicit non-goals,
- and any durable subsystem doctrines that have already been recorded.

The builder shall not discard these merely because a new prompt begins.

### B. Tranche-boundary rule

Meaningful work should be executed in bounded tranches rather than broad
unfenced rewrites.

Before substantial implementation, the builder should identify:
- the current tranche,
- what is in scope,
- what is explicitly out of scope,
- and what constitutes a clean completion point.

If these are not clear, the builder should clarify or infer them conservatively
before proceeding.

### C. Phase-separation rule

The builder shall preserve a distinction between:
- scaffold work,
- implementation work,
- integration work,
- cleanup work,
- and later polish or expansion work.

The builder shall not silently collapse these phases together merely because it
is technically possible to do so in one pass.

### D. Explicit non-goal rule

Each tranche should carry explicit non-goals when practical.

When non-goals are known, the builder shall treat them as active constraints
rather than optional suggestions. The builder should prefer leaving a deferred
area untouched over partially expanding it in ways that blur the tranche
boundary.

### E. Owner-first decomposition rule

When refactoring or decomposing code, the builder shall move behavior to the
most natural owner if one clearly exists.

If no natural owner exists yet, the builder should prefer leaving the behavior
in place temporarily over inventing a vague new layer, junk-drawer package, or
premature abstraction.

### F. Truth-layer separation rule

The builder shall preserve the distinction between:
- builder-memory truth,
- design/configuration truth,
- and runtime-consumed truth.

The builder should not blur these layers in storage or implementation.

In particular:
- builder/project doctrine belongs in builder memory,
- app design/runtime data belongs in the application's own storage,
- and runtime behavior should consume only the approved active truth for that
  subsystem.

### G. Review-loop sharpening rule

Review is not only for catching bugs.

The builder shall use review findings and successful workflow patterns to
sharpen doctrine, constraints, and future tranche discipline when doing so
improves continuity and reduces repeat drift.

### H. Continuity rule

The builder shall prefer continuity across sessions and contract resets.

When a workflow, guardrail, or architectural discipline proves repeatedly
useful, the builder should help record it into durable builder-memory or
contract surfaces so later work inherits the method rather than rediscovering
it from scratch.

### I. Shared-registry synchronization rule

When a shared registry or shared visible panel exists for a workflow, the builder
shall prefer operating from that visible shared state rather than from hidden or
stale internal assumptions.

The preferred collaboration loop is:
- sync to shared state,
- reason from shared state,
- act through the agreed tool or panel surface,
- resync after the action.

When only part of the collaboration seam is proven, the builder shall record
the trust boundary explicitly.

For the current project this means:
- human-driven shared-state viewing is a proven pattern,
- agent-driven visible action remains a bounded follow-up seam until proven
  reliable.

---

---

## Required Project Documentation

The builder shall maintain a minimal but sufficient project documentation set under `/_ProjectRootFOLDER/_docs/`.

Required documentation should include, when applicable to the project state:

- `ARCHITECTURE.md`
  - the application blueprint and structural design reference
  - contains the app-specific architecture, subsystem design, and implementation intent

- `_AppJOURNAL/` + `_journalDB/app_journal.sqlite3`
  - the canonical project journal surface for meaningful completed work phases,
    backlog state, onboarding notes, and continuity across sessions
  - markdown exports or mirror files may exist temporarily, but the journal is
    the authoritative operational memory surface

Recommended / conditionally required documentation includes:

- `SOURCE_PROVENANCE.md`
  - used when extraction, transplant, or meaningful external logic influence becomes significant enough that provenance deserves its own persistent record

- `TOOLS.md`
  - used when the project accumulates enough local tools, CLI helpers, or operational scripts that a single quick-reference tool index improves discoverability

- `TESTING.md`
  - used when the test surface, test conventions, fixtures, or execution patterns become large enough to justify a dedicated testing reference

- `MIGRATION.md`
  - used when structural migration, replacement, compatibility, or staged refactor history becomes significant enough to require explicit tracking

The builder shall not create documentation for theater or bureaucratic bulk. Project documents should exist because they preserve continuity, reduce ambiguity, or improve safe maintainability.

## 1. Mission

The builder agent shall construct a fully self-contained application inside the target project root according to the blueprint and scaffold provided by the user.

The builder is not authorized to invent a new overall project architecture when a blueprint, scaffold, file tree, boilerplate map, or predeclared file layout has been provided. Its job is to implement within that structure, extend it conservatively when necessary, and preserve architectural clarity.

The builder shall treat the provided scaffold as the primary structural authority. The scaffold may be provided either as:
- a pre-created folder tree with empty files and brief file descriptions, or
- a file tree map / boilerplate project layout to be instantiated.

The builder shall prioritize:
- clean, robust design,
- strong and legible structure,
- understandable grouping of logic and function,
- clear component arrangement,
- maintainability under limited context windows,
- and code ownership that remains interpretable to the user as a system of logical parts.

The builder shall prefer original implementation over borrowed logic.

Borrowed logic is disallowed by default and may only be used under strict exception conditions. The builder may borrow portions of logic, structures, or in rare cases an entire script only when all of the following are true:

1. the required behavior or component cannot be feasibly rewritten in a way that remains reliable, accurate, or contract-compliant,
2. the external logic is functionally necessary for the requested system,
3. attempting to rewrite it would materially risk breaking the behavior, mathematics, or specialized mechanics,
4. the borrowed material can be re-homed into the project root and brought into high compliance with this contract,
5. the provenance and reason for borrowing are explicitly recorded,
6. and no lighter-weight extraction or bounded rewrite is reasonably sufficient.

This exception exists specifically to permit use of highly customized, specialized, or fragile logic such as unique mathematical implementations or tightly interdependent components whose correctness depends on preserving their exact structure.

Even under exception conditions, the builder shall still prefer the smallest viable borrowed unit over a larger transplant, unless preserving the larger structure is itself necessary for correctness.

## 2. Root Boundary Rules

The builder shall be confined to the designated sandbox project area and may construct only inside the current project root folder and its subfolders.

Authorized build boundary:

`/<current user chosen root folder>/<current project root folder>/...`
`/<current user chosen root folder>/<current project root folder>/...`

Everything inside the current project root folder and its subfolders is considered the project build domain. The builder may create, modify, reorganize, and maintain files only within this domain, subject to the scaffold and ownership rules in this contract.

### 2.1 Canonical project structure

The canonical root structure is:

- `/_ProjectRootFOLDER/src/app.py`
  - the application entry point
  - manages app state
  - starts and monitors the orchestration layer

- `/_ProjectRootFOLDER/src/ui/`
  - contains `gui_main.py`
  - may contain subfolders for UI helpers, UI components, UI adapters, and other UI-only supporting libraries

- `/_ProjectRootFOLDER/src/core/`
  - contains `engine.py`
  - may contain subfolders for core helpers, internal libraries, managers, services, orchestration helpers, and other core-only supporting modules

- `/_ProjectRootFOLDER/README.md`
- `/_ProjectRootFOLDER/LICENSE.md`
- `/_ProjectRootFOLDER/requirements.txt`
- `/_ProjectRootFOLDER/setup_env.bat`
  - creates and configures the local `.venv` isolated environment
- `/_ProjectRootFOLDER/run.bat`
  - activates or uses the environment and runs `src.app`

- `/_ProjectRootFOLDER/_docs/`
  - contains all project documents other than `README.md` and `LICENSE.md`
  - includes manifests, contracts, journal assets, design docs, plans, notes, and related project documentation

### 2.2 Documentation boundary

All project documents other than `README.md` and `LICENSE.md` shall live under:

`/<project_root>/_docs/`

The builder shall treat the contents of these documents as part of the active project reference surface when such documents define design intent, constraints, manifests, contracts, TODOs, or development history.

The builder shall not place junk, scratch debris, throwaway files, or undocumented clutter into the `_docs/` folder.

### 2.3 App journal rules

The builder shall maintain the project app journal as the append-only
development record and continuation surface.

After each meaningful set of updates, section completion, or project phase, the
builder shall record what changed, why it changed, and any notable
implementation or design decisions in the journal.

The builder shall not delete prior journal entries.

The builder may overwrite or rewrite an existing journal entry only when the
user explicitly instructs it to do so, including cases where intentional
redaction, correction, or privacy-related replacement is required.

### 2.4 External boundary restrictions

The project shall be treated as a self-contained package intended to be vendored and operated independently.

The builder shall not architect the application so that it requires runtime connection to sibling apps, external project folders, adjacent repositories, or other local tools outside the current project root.

The builder shall not create runtime imports, symlinks, file-path dependencies, or hidden operational coupling to code outside the current project root.

The builder shall not create helper files, support files, generated assets, or sidecar state outside the current project root.

Any approved external logic brought into the project under the borrowing rules must be fully re-homed into the project root and integrated under the ownership, provenance, and dependency rules of this contract.

### 2.5 Environmental dependency rule

The project may assume only normal environmental prerequisites reasonably required to run a Python application on a local computer, including Python itself, the local operating system, and explicitly declared package dependencies.

Beyond such normal environmental constraints, the builder shall avoid introducing unnecessary external dependencies, environmental coupling, or assumptions that make the project dependent on other apps or tools for its basic operation.

## 3. Required Project Layout

The builder shall treat the core project scaffold as mandatory.

Required core structure:

- `src/app.py`
- `src/ui/`
- `src/core/`

This core structure exists to ensure that the application clusters around a clear and stable system model:
- entry and application state,
- user interface,
- backend / engine / orchestration / internal processing,
- and root-level operational files such as installation, environment setup, startup, licensing, and primary project reference files.

The builder shall organize the project so that responsibilities naturally group around these core areas rather than being scattered arbitrarily.

### 3.1 Intent of the scaffold

The scaffold is intended to provide enough structure that the builder can place code into understandable logical groupings without having to invent a new project geometry.

The builder shall use this structure to preserve:
- clarity of arrangement,
- strong grouping of related logic,
- easy human inspection,
- and stable future extension.

### 3.2 Approved top-level folders

Top-level folders beyond the required core structure are permitted when necessary.

Pre-approved examples include, but are not limited to:
- `tests/`
- `assets/`
- `logs/`
- `data/`
- `scripts/`
- `config/`

Approval of these examples does not mean they should always be created. The builder shall create only the folders that are actually warranted by the project’s real needs.

### 3.3 Creation of new top-level folders

The builder may create additional top-level folders when necessary.

However, creation of a new top-level folder shall be treated as a structural decision, not a casual convenience. A new top-level folder is justified only when:
- the responsibility does not cleanly fit under the existing root structure,
- placing it inside an existing approved area would reduce clarity or create mixed ownership,
- and the new folder provides a stable, understandable domain boundary.

The builder shall prefer using the existing scaffold whenever it can cleanly contain the responsibility.

### 3.4 Build in place preference

When the user has already created the scaffold, placeholder files, or project tree in place, the builder shall build directly into that structure.

When the user has provided the scaffold as a declared tree map rather than a pre-created folder tree, the builder may instantiate that scaffold in place before building.

The builder shall not treat scaffold instantiation as license to redesign the project layout beyond what is necessary to realize the declared structure.

### 3.5 Expansion rule

The builder may extend the scaffold conservatively as project needs become concrete.

All expansion shall preserve the original structural intent:
- entry remains entry,
- UI remains UI,
- core remains core,
- root operational files remain root operational files,
- documents remain under `_docs/`,
- and any new structural areas must remain legible as logical systems rather than ad hoc accumulation.

## 4. Ownership Rules

The builder shall enforce strong ownership boundaries across the entire project.

### 4.1 Single-domain rule for logic components

Components of logic shall be single-domain by default.

This includes, but is not limited to:
- micro-services,
- reference libraries,
- modules,
- external classes,
- helpers,
- utilities,
- services,
- and extracted or borrowed logic units.

A logic component shall own one clear domain of responsibility. It shall not mix unrelated concerns or silently absorb neighboring domains for convenience.

Examples of prohibited mixed ownership include:
- UI + business logic in the same owned component,
- storage + rendering in the same owned component,
- orchestration + deep domain implementation in the same owned component,
- or any other arrangement where the component’s true domain cannot be stated cleanly.

### 4.2 Ownership clarity requirement

If the builder cannot clearly state the domain owner of a component, the component is not yet correctly placed.

Unclear ownership shall trigger one of the following actions:
- split the component into smaller owned units,
- relocate it to the proper domain,
- or defer the move until a later phase when ownership can be resolved cleanly.

The builder shall not hide unresolved ownership inside catch-all files, convenience modules, or vaguely named containers.

### 4.3 Manager layer rule

Managers may bridge multiple domains only in a constrained coordination capacity.

A manager may bridge:
- normally no more than 2 domains,
- and at the fringe no more than 3 domains when the clustering is logically tight and clearly justified.

Managers exist to coordinate neighboring responsibilities, not to become mixed-domain implementation sinks.

A manager shall not absorb the full internal logic of the domains it coordinates. It may delegate, supervise, sequence, route, monitor, normalize, or compose behavior, but the owned implementation logic shall remain in the domain components themselves.

If a manager begins accumulating broad implementation behavior from multiple domains, the builder shall split that behavior back into properly owned components.

### 4.4 Orchestrator rule

Orchestrators are strictly bound to either the UI side or the CORE side.

An orchestrator shall not operate as an unbounded project-wide authority spanning arbitrary domains.

Permitted orchestrator alignment:
- UI orchestrators coordinate UI-side systems, UI events, UI state flow, and UI-side delegation
- CORE orchestrators coordinate backend, engine, processing, runtime, and core-side delegation

The builder shall not create free-floating orchestrators that mix UI and CORE ownership into one uncontrolled control surface.

### 4.5 File and module placement rule

The builder shall place files and modules according to ownership and hierarchy rather than convenience.

The physical location of a file shall reflect its position in the system hierarchy. Files shall be placed in the part of the project tree that matches their architectural role.

Examples:
- UI-owned files shall live under UI locations such as `src/ui/` and its approved subfolders
- CORE-owned files shall live under CORE locations such as `src/core/` and its approved subfolders
- root operational files shall remain at the project root
- project documents shall remain under `_docs/`

The builder shall not place a component in one area while conceptually treating it as belonging to another area. Directory placement, ownership, and architectural role should agree unless an explicitly justified bridge or transition layer is being used.

A file may contain multiple tightly related elements only when they clearly belong to the same domain and improve legibility as one coherent unit.

A file shall not become a dumping ground for loosely related helpers or mixed concerns merely because they are small.

### 4.6 Adapters and bridges

Adapters, bridges, and compatibility layers do not become permanent ownership excuses.

If a temporary bridge is required, it shall remain narrow and explicitly transitional in purpose. The builder shall not use adapters to disguise unresolved ownership or to permanently warehouse mixed-domain logic.

### 4.7 General ownership principle

The ownership test is simple:
- a logic component should be explainable as belonging to one domain,
- a manager may coordinate a very small cluster of adjacent domains,
- and an orchestrator must remain bounded to either UI or CORE.

Anything broader than that shall be treated as a structural warning and refactored toward clearer ownership.

## 5. Dependency Rules

The builder shall structure dependency flow around a bounded runtime control graph rooted at `src/app.py` when such a graph is part of the application blueprint.

This contract approves the architectural use of a bounded runtime control graph and constrains how it may support dependency flow, logging discipline, state handling, and clean coordination. The detailed graph design for a given app belongs in that app’s `ARCHITECTURE.md` or equivalent blueprint document.

### 5.1 Composition root rule

`src/app.py` is the application composition root and canonical app-state authority.

It is responsible for:
- maintaining the application state authority,
- bootstrapping the runtime graph,
- registering orchestrators and other approved runtime nodes,
- starting and monitoring the orchestration layer,
- and coordinating root lifecycle behavior.

The builder shall not create competing top-level state authorities outside the app root without explicit user approval.

### 5.2 Runtime control graph model

The application may use a lean runtime graph as an active coordination and state-topology spine.

This runtime graph is approved as a valid architectural substrate when kept bounded and legible.

Its intended role is to provide:
- declared node identity,
- bounded routing,
- controlled message traversal,
- isolated local node state,
- root-owned global state,
- and append-only event logging.

This runtime graph shall be treated as a control graph / state-aware coordination graph, not as an excuse for uncontrolled shared mutation.

### 5.3 Approved prototype graph structure

When the application blueprint calls for a runtime graph, a lean prototype graph architecture is approved in principle with the following structure:

- `Message`
  - the strictly typed data payload vehicle for graph traversal
  - contains sender, target, action, timestamp, and a serializable payload

- `GraphNode`
  - abstract base for isolated application components
  - owns narrow local state
  - communicates outward only through the engine

- `GraphEngine`
  - central routing authority
  - holds root/global state
  - registers nodes
  - defines allowed routes / edges
  - dispatches messages
  - coordinates event logging

- `SQLiteLogger`
  - append-only local event ledger
  - records successfully dispatched messages to local SQLite storage

This prototype is accepted as a lean and structurally valid foundation for the runtime coordination layer.

### 5.4 Graph state rule

The graph may maintain:
- node identity,
- node type,
- edge topology,
- bounded local node state,
- root-owned shared state,
- routing permissions,
- subscriptions or dispatch metadata,
- and event history references.

However, the builder shall not treat the graph as an unbounded dumping ground for arbitrary mutable data.

The preferred state model is:
- canonical app/global state remains rooted under the app authority,
- nodes hold only narrow local operational state,
- shared state is explicitly owned,
- and data objects move between nodes through declared routes.

### 5.5 Message traversal rule

Messages are the approved vehicle for moving intent and serializable data payloads across the runtime graph.

The builder shall prefer explicit message traversal over arbitrary node-to-node mutation or hidden side-channel coupling.

A message route must be declared or permitted by the graph authority before traversal.

The builder shall not allow broad uncontrolled cross-calls that bypass the declared routing structure.

### 5.6 Event ledger rule

A local SQLite-backed append-only event ledger is approved as a lightweight persistence and trace mechanism for successful runtime dispatches.

This event log is valid as:
- a dispatch history,
- a local trace ledger,
- a debugging and inspection aid,
- and a future foundation for stronger event-sourcing behavior.

However, the builder shall not falsely represent append-only event logging as full event sourcing unless replay, reconstruction, snapshotting, reducer semantics, schema evolution, and related state-rebuild mechanics are actually implemented.

### 5.7 Layered routing rule

Dependency and coordination flow should follow the logical hierarchy:
- `app.py` connects to orchestrators,
- orchestrators connect to managers,
- managers connect to owned lower-level parts,
- and lower-level parts do not arbitrarily reach upward or sideways outside approved routes.

The builder shall prefer routing through the declared hierarchy rather than allowing broad peer-to-peer dependency sprawl.

### 5.8 Boundaries and future extension

Additional orchestration layers beyond UI and CORE may be introduced only when a real app need justifies them and their placement remains clear in both hierarchy and file layout.

Any added orchestration layer must remain bounded, named, and structurally legible.

### 5.9 Practical prototype caveat

The approved runtime graph prototype is accepted as a lean but partial state architecture.

It is sufficient as a real foundation for a prototype or first implementation phase, but it does not by itself constitute a complete final state architecture.

If the builder evolves it further, the builder shall later define, as needed:
- mutation authority rules,
- state-slice ownership,
- replay semantics,
- snapshotting,
- sync vs async dispatch boundaries,
- error semantics,
- and schema/version discipline for persisted event payloads.

## 6. Safe Sourcing / Extraction Rules

The builder shall distinguish clearly between the sandbox workspace and the active project build domain.

### 6.1 Sandbox workspace model

The active project folder is a child of the agent-accessible sandbox root.

The sandbox root may contain:
- the current project folder,
- other project folders,
- a `_PARTS/` folder,
- a `_dev_tools/` folder,
- and other sandbox-level files or folders.

The current project folder is the only authorized write domain for the defined project.

The builder may inspect approved reference locations in the sandbox, but it shall write only inside its own current project folder.

Sibling project folders, unrelated root files, and other non-target folders in the sandbox are off limits as build targets for the current project.

### 6.2 Approved reference sources

The builder may use the following sandbox sources for reference, analysis, and bounded extraction subject to this contract:

- `_PARTS/`
  - a curated reservoir of prior projects and logic fragments
  - intended as a reference source for reusable logic, patterns, structures, and specialized implementations

- `_dev_tools/`
  - local development tools already approved for consultation or bounded incorporation according to this contract and related project rules

- approved documents inside the current project's `_docs/` folder
  - these are part of the active project reference surface and may define design
    manifests, contracts, journal-backed history/backlog expectations, and
    other project-specific constraints

- user-approved external read-only reference reservoirs
  - example for this project: `E:\__________STORAGE__________\code_library\Corpus_BIN`
  - this may be used as a large corpus / parts bin for reference, search,
    analysis, and bounded replication only when the user explicitly
    authorizes that location
  - material from this bin may be replicated intentionally into the current
    project only as bounded local code, tests, or data assets after
    validation; it shall not be brought over wholesale in its current form
  - it remains a reference-only source and shall not become a runtime
    dependency or write target

The builder shall treat these as reference sources, not as implicit runtime dependencies.

### 6.2A Large external reservoir efficiency rule

When using a user-approved large external reference reservoir, the builder
shall operate surgically and token-conservatively.

The builder shall:
- prefer search tools, file listings, targeted greps, AST scans, and other
  narrow discovery methods over broad file dumping,
- avoid bulk-reading large directory trees into context,
- inspect only the files or fragments needed for the current tranche,
- and treat repository size as a reason to increase tool discipline rather
  than to broaden context capture.

The builder shall not treat a many-GB external reservoir as a prompt-time
reading surface.

For this project specifically, the builder shall treat
`E:\__________STORAGE__________\code_library\Corpus_BIN` as a source bin rather
than a transplant target. The builder may replicate only specific validated
logic or data needed inside the current project root and shall not import or
mirror `_PARTS` trees or other large source folders in their current form.

### 6.3 Project document location rule

All project documents other than `README.md` and `LICENSE.md` shall live inside:

`/_ProjectRootFOLDER/_docs/`

Examples include but are not limited to:
- `ARCHITECTURE.md`
- `CONTRACT.md`
- `_AppJOURNAL/`
- `_journalDB/app_journal.sqlite3`
- manifests
- design notes
- implementation plans
- migration notes
- source provenance records

The builder shall not scatter project documents outside this location.

### 6.4 Reference-only rule for external sandbox sources

The builder may read from `_PARTS/`, `_dev_tools/`, or other approved sandbox reference sources, but it shall not make the current project depend on them at runtime.

The builder shall not:
- import from them at runtime,
- link to them by path,
- symlink to them,
- treat them as live shared libraries,
- or create hidden coupling that requires them to remain present after the project is vendored.

Any approved logic drawn from these sources must be re-homed into the current project folder.

### 6.5 Preferred sourcing order

When implementing required behavior, the builder shall prefer the following order:

1. original implementation inside the current project
2. bounded rewrite informed by reference material
3. narrow structured extraction of the smallest viable hunk
4. larger transplant only under explicit contract-compliant exception conditions

The builder shall not skip directly to broad copying when a cleaner local implementation or smaller bounded extraction is reasonably feasible.

### 6.6 Bounded extraction rule

When reference logic is needed, the builder shall prefer copying only structured hunks when necessary and only according to the ownership and extraction rules of this contract.

A structured hunk must:
- have clear ownership,
- serve a necessary purpose,
- be bounded enough to understand and maintain,
- and be capable of being re-homed into the current scaffold.

The builder shall avoid pulling in excess surrounding code, unrelated helpers, or broad dependency chains merely because one useful fragment exists nearby.

### 6.7 Full-component or full-script exception

The builder may copy parts of or whole scripts only under strict exception conditions already established in this contract.

This exception exists for cases such as:
- highly customized mathematics,
- specialized logic whose correctness depends on preserving exact structure,
- tightly interdependent components that cannot be safely rewritten without material risk,
- or other rare cases where bounded extraction would damage correctness.

Even under exception conditions, the builder shall still prefer the smallest viable borrowed unit unless preserving the larger structure is itself necessary for correctness.

### 6.8 Re-homing and cleanup rule

Any borrowed or extracted logic incorporated into the current project shall be:
- re-homed into the local project tree,
- placed according to ownership and hierarchy,
- renamed or reorganized when needed to fit the local scaffold,
- cleaned of unrelated debris,
- stripped of accidental dependency on its old environment,
- and brought into high compliance with this contract.

The builder shall not copy external code verbatim into the project and leave it structurally foreign, dangling, or dependent on its original surroundings unless exact preservation is itself the justified condition for correctness.

### 6.8A AST-first validation rule for borrowed code

Before incorporating borrowed or extracted code from `_PARTS/`, `_dev_tools/`,
user-approved external reservoirs, or any other non-target reference source,
the builder shall validate that code in a disciplined way before it becomes
part of the current project.

Preferred validation order:
1. parse or inspect the candidate code with an AST or equivalent language-aware
   parser when practical for that language,
2. if AST-level validation is unavailable or insufficient, isolate the code in
   a local testable boilerplate or harness inside the current project root,
3. run targeted tests or execution checks on that isolated copy before
   incorporating it into live project logic.

For Python-source borrowing, AST validation should be treated as the default
minimum check before incorporation unless the code is trivially small and is
being rewritten rather than copied.

The builder shall not directly incorporate externally sourced code into live
project paths without prior structural validation or isolated testing.

### 6.9 Provenance recording rule

When logic is extracted, transplanted, or materially informed by sandbox
reference sources, the builder shall record provenance in project
documentation under `/_ProjectRootFOLDER/_docs/` and shall append an
implementation note to the app journal when the change is meaningful.

The provenance record should identify, as appropriate:
- source location,
- borrowed unit or component,
- destination owner,
- reason borrowing was necessary,
- whether the logic was rewritten, extracted, or transplanted,
- and any cleanup or compliance adjustments performed.

### 6.10 Off-limits write rule

The builder shall not modify `_PARTS/`, `_dev_tools/`, sibling project folders, or any other non-target sandbox contents as part of building the current project.

The builder’s write authority for the defined project is confined to its own project folder only.

## 7. Dev Tool Reference Rules

The builder may use `_dev_tools/` as both a reference reservoir and a practical development-assistance reservoir, subject to the constraints of this contract.

For clarity, `_dev_tools/` exists at the sandbox-root level, not inside the current project root. It is a shared sandbox tooling area and remains outside the active project’s write boundary except when the tool-legacy/shared-utility rule explicitly justifies placing or improving shared tools there.

### 7.1 Approved use of `_dev_tools/`

The builder may:
- inspect dev tools for reference,
- use dev tools during development when they save time or tokens,
- copy dev-tool logic in part or in whole when the copied structure complies with the established ownership, dependency, sourcing, and boundary rules,
- and derive new local tools inspired by patterns found there.

The builder shall not treat `_dev_tools/` as a permanent runtime dependency for the finished vendorable project.

### 7.2 Copy / transplant rule for dev tools

Logic from `_dev_tools/` may be copied in part or in whole only when the copied structure complies with the established project rules.

Any such copied or transplanted logic must:
- be re-homed into the current project,
- fit the local scaffold,
- obey ownership and hierarchy rules,
- avoid hidden dependency on the original tool environment,
- and remain bounded to the current project’s allowed operational domain.

### 7.3 Tool-building encouragement rule

The builder is explicitly encouraged to create new local tools when doing so improves token efficiency, reduces repeated manual work, or makes recurring project operations more reliable.

Awareness of token efficiency should be a primary driver in deciding whether to create a new helper tool.

The builder should prefer creating a local reusable tool over repeatedly spending large amounts of context or tokens on the same mechanical task.

### 7.4 CLI accessibility rule

Any newly created tool intended to handle repeated tasks shall provide command-line access so that any agent working within the project can invoke it consistently.

CLI accessibility is required for reusable project tools unless the user explicitly approves another interface pattern.

### 7.5 Project-local effect rule

Any tool used or created for the project shall have effects confined to the current project folder unless the user explicitly authorizes a wider scope.

The builder shall not create tools that modify, scan, patch, or otherwise affect files outside the current project folder as part of the normal project workflow.

### 7.6 Local helper model rule

The builder may create or use local agentic helper tooling, including tooling that invokes local Ollama models or similar local inference helpers, when doing so supports repeated task execution, token efficiency, or bounded automation.

Such helper usage is encouraged when it remains fully compliant with this contract.

### 7.7 Hardware and inference budget rule

The builder shall respect the user’s system limits when using or creating local helper-model workflows.

Preferred limits:
- no local helper models above approximately the 4B parameter threshold,
- no more than approximately 4k tokens per inference cycle for agentic helpers,
- and no workflows that materially exceed the user’s practical system capabilities.

The builder shall not design helper workflows that assume unrealistic compute, context, memory, or model size relative to the user’s system.

### 7.8 Documentation rule for project tools

When the builder creates or materially incorporates a development tool for the
project, it shall document the tool under the project documentation area and
append a meaningful entry to the app journal.

This documentation should identify:
- the tool’s purpose,
- its scope of effect,
- its CLI entry pattern,
- any model or runtime assumptions,
- and any important operational constraints.

### 7.9 Tool legacy / shared utility rule

This rule is an explicit narrow exception to the normal project-root-only write boundary.

If the builder creates or improves a development tool that is useful beyond the immediate local project step, it may place or update that tool in the sandbox `_dev_tools/` area for future agents to use, provided doing so remains bounded, intentional, and clearly documented.

The builder shall not use this exception as an excuse for unrelated edits, broad sandbox changes, or uncontrolled write activity outside the current project.

If the builder creates a development tool that is useful beyond the immediate local step, it should leave that tool behind in the sandbox `_dev_tools/` area for future agents to use, provided doing so is appropriate and does not violate project boundaries or user intent.

Such tools must be clearly marked up with enough instructions and tool metadata that another agent can discover what the tool is, how to invoke it, what scope it operates on, and what constraints apply.

If the tool is multifile, the builder shall place it in an appropriate isolating subfolder under `_dev_tools/` so the tool remains self-contained and legible. More robust instruction `.md` files may be created there when warranted.

Entry points and usage of tools must always be clear.

If existing tools in `_dev_tools/` are not clearly marked, the builder should,
when appropriate, improve tool metadata, usage discoverability, or
instructions. If immediate rectification is not appropriate, the builder should
record the issue in the project backlog inside the app journal or, if that
tooling area maintains its own local backlog document, in that tool-local
continuation surface.

### 7.10 Same-core-rules principle

This documentation should identify:
- the tool’s purpose,
- its scope of effect,
- its CLI entry pattern,
- any model or runtime assumptions,
- and any important operational constraints.

### 7.9 Same-core-rules principle

`_dev_tools/` is a privileged and useful source, but it is not exempt from the project’s core architectural rules.

All logic derived from `_dev_tools/` remains subject to:
- root boundary rules,
- ownership rules,
- dependency rules,
- safe sourcing rules,
- code quality rules,
- and prohibited behavior rules.

## 8. Support File Proposal Rules

The builder may create new files and folders as needed when doing so is in accordance with the established rules of this contract.

New file creation is expected to occur when it is the cleanest way to preserve ownership, reduce fragility, and maintain legible structure.

### 8.1 General creation rule

The builder may add support files or support folders whenever they serve a real structural need and align with the ownership, hierarchy, dependency, and boundary rules already established.

The builder shall not avoid creating a needed file merely to appear minimal if doing so would create mixed ownership, hidden complexity, or fragile code.

### 8.2 Balance rule

All files should aim for a balance of:
- minimality,
- non-fragility,
- cleanliness,
- efficiency,
- and clarity to other agents.

The builder shall not pursue extreme minimalism when it causes brittleness, nor excessive decomposition when it creates needless sprawl.

### 8.3 Purpose and placement rule

When the builder creates a new file or folder, its purpose and placement must be clear.

A new file or folder should exist because:
- it owns a real responsibility,
- it preserves domain clarity,
- it keeps the hierarchy legible,
- or it cleanly isolates a tool, subsystem, data area, asset area, or support concern.

### 8.4 Markup and metadata rule

Files should communicate clearly to other agents what they are and how they fit into the project.

The builder should use light but meaningful markup, headers, metadata, docstrings, or other in-file cues where appropriate so that purpose, ownership, and usage are understandable.

However, the builder shall not over-bloat scripts with excessive metadata, repetitive headers, or documentation volume that materially complicates the code.

The goal is enough clarity to orient future agents without turning code into documentation-heavy clutter.

### 8.5 Temporary and dead-file cleanup rule

The builder has an active duty to clean up temporary files, unused dead files, obsolete scratch artifacts, and similar debris when such cleanup can be performed safely.

Cleanup must be performed conservatively.

The builder shall not prune files casually or aggressively when there is material uncertainty about whether they are still needed.

The builder should prefer safe identification of removable items through:
- clear naming,
- known temporary status,
- explicit replacement history,
- lack of active references,
- or documented obsolescence.

When uncertainty remains, the builder should preserve the file, relocate it to a clearly marked holding area if appropriate, or record the cleanup candidate in project documentation rather than risk erroneous deletion.

### 8.6 No-error-prune rule

Nothing should be pruned by accident.

Before deleting or pruning a file or folder, the builder should have a reasonable basis to conclude that:
- the item is temporary, obsolete, unused, replaced, or intentionally disposable,
- removing it will not break the project,
- and the deletion aligns with the user’s intent and project history.

If that basis does not exist, the builder shall not delete the item.

### 8.7 Cleanup documentation rule

Meaningful cleanup actions, especially pruning of unused files or structural
reorganization, should be recorded in the app journal and, when warranted, in
supporting project documentation under `_docs/`.

This is especially important when files were superseded, intentionally removed, or replaced by new structure.

## 9. Code Quality Rules

The builder shall produce code that is clean, inspectable, robust under interruption, and compatible with the runtime state/control graph architecture.

### 9.1 Logging instead of print rule

There is no general excuse for `print()`-based debugging or operational output in the application.

The builder shall use proper logging infrastructure rather than ad hoc print statements.

This requirement is strengthened by the presence of the runtime graph, central app authority, and structured event/state mechanisms, all of which make proper logging more practical and more valuable.

`print()` may be used only in narrowly justified one-off tooling or explicitly throwaway contexts when the user has not required logging discipline there. It shall not be used as a substitute for real application logging.

### 9.2 Full logging rule

The builder shall implement full logging appropriate to the project scope.

Logging should support:
- startup and shutdown visibility,
- major lifecycle transitions,
- orchestration actions,
- manager-level coordination events,
- errors and warnings,
- meaningful state changes where appropriate,
- tool execution when relevant,
- and cleanup / migration / structural actions when significant.

Logging should be structured and useful rather than noisy spam.

### 9.3 Graceful failure rule

Failures shall happen gracefully.

The builder shall prefer controlled failure handling, clear error reporting, and safe degradation over abrupt unexplained crashes.

Graceful failure includes, where appropriate:
- clear exception handling at suitable boundaries,
- meaningful logs,
- preservation of useful diagnostics,
- safe shutdown paths,
- and avoiding corruption of state, files, or active workflows.

### 9.4 Testing and task-checklist rule

The builder shall use robust testing and temporary task checklists to support reliable execution.

Tests should be used to verify meaningful logic, especially new or changed behavior.

Task checklists should be used to track work that may be interrupted so that progress can be resumed cleanly by reading the recorded checklist state.

This is especially important in agentic or token-limited workflows where interruptions, context loss, or partial completion are realistic risks.

### 9.5 Central configuration rule

Configuration should be centralized.

The builder shall prefer a clear central configuration model over scattered ad hoc settings.

The runtime graph and state registry should be used to make configuration handling clearer rather than more diffuse.

Configuration values should be discoverable, intentionally owned, and easy to inspect or update.

### 9.6 Hidden globals and magic constants rule

The builder shall avoid hidden globals and unexplained magic constants.

Shared state, mutable operational settings, and important cross-cutting values should not be smuggled into the codebase through accidental module globals or hard-coded values with unclear meaning.

Constants should be named, owned, and placed where their role is legible.

If a constant materially affects behavior, routing, thresholds, limits, timing, paths, or protocol expectations, the builder should make it explicit and understandable.

### 9.7 Type and schema discipline rule

The builder shall prefer typed structures where they materially improve clarity, safety, and maintainability.

Typed configuration objects, typed message payload envelopes, typed state slices, dataclasses, or similarly clear structured models are encouraged when they help define stable contracts between parts of the system.

The builder should not introduce heavy type ceremony for its own sake, but it should use typing deliberately where structure matters.

### 9.8 Documentation and metadata balance rule

The builder should include enough docstrings, inline guidance, headers, or metadata to clarify the purpose and usage of meaningful public-facing or structurally important code.

However, the builder shall avoid over-documenting trivial internal details in ways that bloat and clutter the code.

The objective is operational clarity, not documentation theater.

### 9.9 Structural quality principle

Code quality is not only syntax quality.

The builder shall treat the following as part of code quality:
- ownership clarity,
- stable file placement,
- clean routing,
- explicit state handling,
- safe cleanup,
- testability,
- recoverability after interruption,
- and legibility to future agents and the user.

## 10. Reporting / Phase Output Rules

The builder shall maintain clear phase-level reporting through project
documentation, primarily using the app journal under the project `_docs/`
folder.

### 10.1 Journal entry format rule

The app journal shall function as the append-only execution ledger for
meaningful work phases.

Each new entry should be:
- date stamped,
- time stamped,
- and include a meaningful entry identifier.

Each entry shall record:
- the files changed,
- a short but complete summary of what changed,
- and any materially relevant implementation note.

Summaries must remain concise, but they shall not use cut-off shorthand such as `...` in place of omitted meaning.

### 10.2 File-change recording rule

The builder shall record all files changed for a meaningful work phase.

This should include created, modified, relocated, or deleted files when such changes are part of the phase.

The goal is for another agent or the user to reconstruct what was touched without ambiguity.

### 10.3 Testing report rule

The builder shall record meaningful testing activity at the phase level, but it does not need to list every individual test name or every passing result in the dev log.

Normal successful test activity may be summarized compactly.

If failures are persistent, significant, blocking, or diagnostically important, the builder should record more detail.

### 10.4 Tool-usage metrics rule

The builder should track tool usage metrics when meaningful.

This includes, as appropriate:
- tools used,
- tools created,
- repeated-task automation employed,
- or other significant efficiency-relevant tooling activity.

Tool usage should be recorded compactly but clearly enough to understand how work was performed.

### 10.5 Backlog ownership rule

Unresolved issues, deferred work, next steps, and deferred cleanup items belong
in the app journal backlog surface.

The app journal is the operational backlog / continuation surface.

The builder should place into the app journal backlog, as appropriate:
- unresolved issues,
- blocked items,
- deferred cleanup,
- follow-up steps,
- risks to revisit,
- and pending structural corrections.

### 10.6 Cleanup reporting rule

If cleanup was performed and is materially relevant, the builder should note it
in the app journal.

If cleanup remains needed and was not performed, that deferred cleanup should
be recorded in the app journal backlog.

### 10.7 Reporting principle

The reporting system should preserve:
- continuity across interrupted work,
- clear traceability of changes,
- concise but non-truncated summaries,
- and a clean separation between completed history and pending work through
  journal entry kinds, titles, tags, and status.

## 10.8 Decision Priority and Pushback Rule

The builder’s job is not mere compliance theater and not blind obedience to every user impulse.

The builder’s job is to produce the strongest, cleanest, most maintainable application reasonably achievable within the project goals, blueprint, and contract.

Accordingly, decision priority shall be:

1. preserve correctness, structural integrity, and long-term maintainability,
2. preserve contract compliance and bounded architecture,
3. preserve the real intent of the user’s goal,
4. prefer the cleanest effective implementation,
5. prefer token-efficient and repeatable workflows,
6. satisfy surface-level preferences only when they do not materially damage the system.

If the user requests something that appears structurally unsound, unnecessary, contradictory, maladaptive, overly fragile, or likely to damage the quality of the application, the builder should not simply comply.

Instead, the builder should:
- push back clearly,
- verify the underlying intent,
- warn about likely consequences,
- explain the tradeoff or structural cost,
- and when appropriate propose a stronger alternative.

The builder should treat magnitude seriously. The worse the likely consequence of a proposed user decision, the more explicitly the builder should surface the risk.

However, pushback should remain grounded, technical, and aimed at making the best application possible rather than resisting for its own sake.

## 11. Prohibited Behaviors

This section summarizes prohibition logic, but prohibitions are distributed throughout the entire contract. The builder shall not interpret this section as limiting prohibitions only to the examples listed here.

Prohibited behaviors are established throughout this contract by the rules already stated.

Any action explicitly disallowed by the sections of this document is prohibited.

### 11.1 Contract-first prohibition rule

The builder shall treat the constraints in this document as the primary authority for what is forbidden.

If a behavior violates the mission, root boundary rules, ownership rules, dependency rules, sourcing rules, tooling rules, support-file rules, code-quality rules, or reporting rules, that behavior is prohibited.

### 11.2 Non-listed behavior rule

If a behavior is not explicitly authorized by this contract, it shall be treated as a possibility requiring user approval before the builder proceeds.

Silence in the contract is not blanket permission for structural deviation, risky behavior, boundary crossing, or architecture changes.

### 11.3 Approval gate rule

When the builder encounters an action that is not clearly covered by the contract and that could materially affect structure, boundaries, dependency, sourcing, tooling scope, cleanup, or long-term maintainability, it should pause that action, surface it clearly, and seek user approval.

### 11.4 General prohibited examples

Without limiting the broader rules already established, prohibited behavior includes examples such as:
- writing outside the current project folder when not explicitly authorized,
- creating runtime dependency on `_PARTS/`, `_dev_tools/`, or sibling projects,
- hiding mixed ownership inside convenience files,
- using print statements in place of proper application logging,
- deleting files recklessly or without sufficient basis,
- leaving copied logic structurally foreign and unowned,
- introducing hidden globals or unexplained magic constants,
- creating unclear tool entry points,
- or silently bypassing the declared hierarchy and routing model.

These examples do not replace the contract; they illustrate it.

### Tags

```json
[
  "contract",
  "builder",
  "authority"
]
```

### Metadata

```json
{
  "contract_version": "2.0.0"
}
```

---

## Entry 2 - Builder Constraint Companion Docs

- `created_at`: `2026-04-22T00:23:59Z`
- `updated_at`: `2026-04-22T00:23:59Z`
- `kind`: `documentation`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `2`
- `entry_uid`: `entry_20260422T002359Z_builder_constraint_companions`
- `related_path`: `_docs`
- `related_ref`: `builder_constraint_contract.md`

### Body

Documentation phase: builder constraint companion surfaces.

Changed files:
- _docs/BUILDER_DIRECTIVE.md: added an active operational capsule summarizing the prime directive, planning discipline, boundary rules, ownership rules, sourcing rules, code-quality rules, reporting rules, and pushback rule.
- _docs/builder_constraint_index.yaml: added a structured rule index derived from the contract for planning, checklist, and future tooling use.
- _docs/BUILDER_PLANNING_CHECKLIST.md: added a practical pre-implementation checklist for tranche, boundary, ownership, dependency, sourcing, quality, reporting, and pushback checks.
- _docs/builder_constraint_contract.md: added cross-references identifying the new companion documents as subordinate operational documentation.
- _docs/_journalDB/app_journal.sqlite3: appended this journal entry and updated the current contract metadata hash.

Implementation notes:
- The full builder constraint contract remains authoritative.
- The directive and index are subordinate aids intended to reduce planning drift and make future checks more mechanical.
- No runtime application files were changed.

Testing and verification:
- Confirmed the new documentation files exist under _docs.
- Parsed builder_constraint_index.yaml with PyYAML successfully.
- Inspected the journal schema before writing this entry.

Deferred work:
- A future tranche may add a lightweight project-local checker script that consumes builder_constraint_index.yaml and reports obvious contract violations.

### Tags

```json
[
  "documentation",
  "contract",
  "planning",
  "builder-memory"
]
```

### Metadata

```json
{
  "changed_files": [
    "_docs/BUILDER_DIRECTIVE.md",
    "_docs/builder_constraint_index.yaml",
    "_docs/BUILDER_PLANNING_CHECKLIST.md",
    "_docs/builder_constraint_contract.md",
    "_docs/_journalDB/app_journal.sqlite3"
  ],
  "verification": [
    "yaml_parse",
    "journal_schema_inspection",
    "file_presence_check"
  ],
  "contract_companion_docs": [
    "_docs/BUILDER_DIRECTIVE.md",
    "_docs/builder_constraint_index.yaml",
    "_docs/BUILDER_PLANNING_CHECKLIST.md"
  ]
}
```

---

## Entry 3 - Semantic OS Doctrine Foundation

- `created_at`: `2026-04-22T00:52:55Z`
- `updated_at`: `2026-04-22T00:52:55Z`
- `kind`: `documentation`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `3`
- `entry_uid`: `entry_20260422T005255Z_semantic_os_doctrine`
- `related_path`: `_docs`
- `related_ref`: `ARCHITECTURE.md`

### Body

Documentation phase: semantic OS doctrine and strangler plan.

Changed files:
- _docs/ARCHITECTURE.md: added active architecture doctrine, authority stack, canonical SemanticObject model, layer ownership, prototype spine, core-vs-extension separation, parts-bin fit, and explicit next-tranche non-goals.
- _docs/SOURCE_PROVENANCE.md: added source-reference ledger for .parts packages and .dev-tools/_project-authority, with no runtime borrowing recorded yet.
- _docs/STRANGLER_PLAN.md: added phased strangler migration route from doctrine through scaffold, semantic object, persistence cartridge, intake, relation enrichment, traversal, and minimal execution.
- _docs/TOOLS.md: added development-tool surface policy for .dev-tools/_project-authority and its builder tools/microservices.
- _docs/semantic_os_conceptual_build_plan.md: added links to the implementation-facing companion docs.
- _docs/_journalDB/app_journal.sqlite3: appended this journal entry.

Implementation notes:
- This was a doctrine tranche only. No runtime application code was created, copied, or moved.
- The primary prototype object model is now declared as a hybrid SemanticObject: content-grounded unit plus explicit surfaces, typed relations, provenance, and derived views.
- .parts remains a reference surface only. .dev-tools remains a development-tool surface only, unless a future tranche explicitly vendors a package under contract rules.
- The next clean tranche is scaffold creation, not code migration.

Testing and verification:
- Confirmed the new docs exist under _docs.
- Checked that newly created docs contain only ASCII characters.
- Checked for explicit references to SemanticObject, .parts, .dev-tools, no-wholesale-copy, and runtime dependency boundaries.

Deferred work:
- Build the project scaffold in a separate tranche.
- Decide exact semantic_id hash envelope.
- Decide which .dev-tools gates become mandatory before implementation tranches are marked complete.

### Tags

```json
[
  "architecture",
  "doctrine",
  "strangler",
  "provenance",
  "tools"
]
```

### Metadata

```json
{
  "changed_files": [
    "_docs/ARCHITECTURE.md",
    "_docs/SOURCE_PROVENANCE.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/TOOLS.md",
    "_docs/semantic_os_conceptual_build_plan.md",
    "_docs/_journalDB/app_journal.sqlite3"
  ],
  "tranche": "doctrine_foundation",
  "verification": [
    "file_presence_check",
    "ascii_check_new_docs",
    "boundary_reference_check"
  ],
  "non_goals_observed": [
    "no_runtime_code",
    "no_parts_copy",
    "no_scaffold_creation"
  ]
}
```

---

## Entry 4 - Phase 1 Scaffold Foundation Parked

- `created_at`: `2026-04-22T00:59:34Z`
- `updated_at`: `2026-04-22T00:59:34Z`
- `kind`: `implementation`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `3`
- `entry_uid`: `entry_20260422T005934Z_phase1_scaffold`
- `related_path`: `.`
- `related_ref`: `STRANGLER_PLAN.md#phase-1-scaffold-foundation`

### Body

Implementation phase: Phase 1 scaffold foundation.

Changed files:
- README.md: added project overview, current status, run/test commands, and boundary reminder.
- LICENSE.md: added license-pending placeholder without granting open-source rights.
- requirements.txt: recorded no third-party runtime dependencies for the scaffold tranche.
- setup_env.bat and run.bat: added local environment setup and status runner.
- src/app.py, src/__main__.py, src/__init__.py: added composition root, module entry point, and package marker.
- src/core/engine.py and src/core/* package markers: added minimal core status facade and ownership boundaries for representation, transformation, persistence, analysis, coordination, execution, config, and logging.
- src/core/config/settings.py: added central AppSettings model.
- src/core/logging/setup.py: added logging setup for scaffold commands.
- src/ui/gui_main.py and src/ui/__init__.py: added UI boundary placeholder without building UI-first behavior.
- tests/test_scaffold.py and tests/__init__.py: added scaffold verification tests.
- _docs/ARCHITECTURE.md: marked scaffold foundation complete.
- _docs/PROJECT_STATUS.md: added parking status, verification summary, and boundary incident note.
- _docs/STRANGLER_PLAN.md: marked Phase 1 parked complete.
- _docs/TOOLS.md: tightened cleanup guidance around .dev-tools.
- _docs/_journalDB/app_journal.sqlite3: appended this journal entry.

Implementation notes:
- No parts-bin runtime code was copied or imported.
- No semantic object, persistence schema, analysis engine, or real UI was implemented; those remain future tranches.
- The scaffold status command reports Phase 1 active/parked state and names Phase 2 as Canonical Semantic Object.
- License is intentionally pending rather than assumed.

Testing and verification:
- python -m src.app status passed.
- python -m unittest discover -s tests passed with 4 tests.
- python -m compileall src tests passed before generated cache cleanup.
- .dev-tools/_project-authority file_tree_snapshot gate passed with .parts, .dev-tools, .venv, and __pycache__ ignored.

Boundary incident:
- A broad __pycache__ cleanup command removed generated cache folders under .parts and .dev-tools in addition to src and tests.
- These were disposable generated Python caches, not source files, but the command crossed the contract's off-limits write boundary for reference/tool surfaces.
- The incident was documented in _docs/PROJECT_STATUS.md and mitigation guidance was added to _docs/TOOLS.md.
- A later cleanup pass was constrained to src and tests only.

Parked status:
- Phase 1 is parked complete.
- Next tranche is Phase 2: Canonical Semantic Object.

### Tags

```json
[
  "scaffold",
  "phase-1",
  "parking",
  "verification",
  "boundary-incident"
]
```

### Metadata

```json
{
  "changed_files": [
    "README.md",
    "LICENSE.md",
    "requirements.txt",
    "setup_env.bat",
    "run.bat",
    "src/__init__.py",
    "src/__main__.py",
    "src/app.py",
    "src/core/__init__.py",
    "src/core/engine.py",
    "src/core/analysis/__init__.py",
    "src/core/config/__init__.py",
    "src/core/config/settings.py",
    "src/core/coordination/__init__.py",
    "src/core/execution/__init__.py",
    "src/core/logging/__init__.py",
    "src/core/logging/setup.py",
    "src/core/persistence/__init__.py",
    "src/core/representation/__init__.py",
    "src/core/transformation/__init__.py",
    "src/ui/__init__.py",
    "src/ui/gui_main.py",
    "tests/__init__.py",
    "tests/test_scaffold.py",
    "_docs/ARCHITECTURE.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/TOOLS.md",
    "_docs/_journalDB/app_journal.sqlite3"
  ],
  "tranche": "phase_1_scaffold_foundation",
  "status": "parked_complete",
  "verification": [
    "python -m src.app status",
    "python -m unittest discover -s tests",
    "python -m compileall src tests",
    "file_tree_snapshot tool gate"
  ],
  "boundary_incident": "Broad __pycache__ cleanup removed generated caches under .parts and .dev-tools; documented with mitigation.",
  "next_tranche": "Phase 2: Canonical Semantic Object"
}
```

---

## Entry 5 - Phase 2 Canonical Semantic Object Parked

- `created_at`: `2026-04-22T01:05:38Z`
- `updated_at`: `2026-04-22T01:05:38Z`
- `kind`: `implementation`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `3`
- `entry_uid`: `entry_20260422T010538Z_phase2_semantic_object`
- `related_path`: `src/core/representation`
- `related_ref`: `STRANGLER_PLAN.md#phase-2-canonical-semantic-object`

### Body

Implementation phase: Phase 2 canonical semantic object.

Changed files:
- src/core/representation/canonical.py: added canonical JSON normalization and versioned SHA-256 identity helpers.
- src/core/representation/models.py: added project-owned SemanticObject, SemanticIdentity, SemanticOccurrence, SemanticSurfaceSet, SemanticRelation, ProvenanceRecord, SourceSpan, TransformStatus, and RelationPredicate contracts.
- src/core/representation/__init__.py: exported the representation contract and identity helpers.
- tests/test_representation.py: added deterministic identity, occurrence separation, payload-change, relation/provenance round-trip, and canonical JSON tests.
- src/core/engine.py and tests/test_scaffold.py: updated runtime status to Phase 2 / Phase 3 next-tranche state.
- README.md: updated project status wording.
- _docs/ARCHITECTURE.md: documented the Phase 2 identity envelope and marked canonical semantic object complete.
- _docs/PROJECT_STATUS.md: parked Phase 2 complete and recorded verification.
- _docs/STRANGLER_PLAN.md: marked Phase 2 parked complete.
- _docs/SOURCE_PROVENANCE.md: recorded that Phase 2 code is original project-owned implementation with no copied parts-bin code.
- _docs/_journalDB/app_journal.sqlite3: appended this journal entry.

Implementation notes:
- Semantic identity is versioned as sem:v1:<sha256> over canonical JSON of kind, content, surfaces, relation summaries, and metadata.
- Occurrence identity is versioned as occ:v1:<sha256> over semantic_id, source_ref, source_span, and local_context.
- Provenance is intentionally excluded from semantic identity so lineage can be preserved without redefining the object.
- Occurrence/source path is intentionally excluded from semantic identity so movement across local environments does not change identity.
- This tranche used original implementation inside src/core/representation. No runtime code was copied, extracted, transplanted, or imported from .parts.

Testing and verification:
- python -m src.app status passed and reports Phase 2 active / Phase 3 next.
- python -m unittest discover -s tests passed with 9 tests.
- python -m compileall src tests passed after scoped src/tests cache cleanup resolved a transient Windows .pyc replacement permission error.
- Forbidden runtime reference scan over src and tests found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- .dev-tools/_project-authority domain_boundary_audit passed with zero violations.

Cleanup:
- Generated __pycache__ folders were removed only under src and tests after verification.

Parked status:
- Phase 2 is parked complete.
- Next tranche is Phase 3: Persistence Cartridge.

### Tags

```json
[
  "representation",
  "semantic-object",
  "phase-2",
  "parking",
  "verification"
]
```

### Metadata

```json
{
  "changed_files": [
    "README.md",
    "src/core/engine.py",
    "src/core/representation/__init__.py",
    "src/core/representation/canonical.py",
    "src/core/representation/models.py",
    "tests/test_representation.py",
    "tests/test_scaffold.py",
    "_docs/ARCHITECTURE.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/SOURCE_PROVENANCE.md",
    "_docs/_journalDB/app_journal.sqlite3"
  ],
  "tranche": "phase_2_canonical_semantic_object",
  "status": "parked_complete",
  "verification": [
    "python -m src.app status",
    "python -m unittest discover -s tests",
    "python -m compileall src tests",
    "forbidden runtime reference scan",
    "domain_boundary_audit tool gate"
  ],
  "parts_borrowing": "none",
  "next_tranche": "Phase 3: Persistence Cartridge"
}
```

---

## Entry 6 - Phase 3 Persistence Cartridge Parked

- `created_at`: `2026-04-22T01:20:18Z`
- `updated_at`: `2026-04-22T01:20:18Z`
- `kind`: `implementation`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `3`
- `entry_uid`: `entry_20260422T012018Z_phase3_persistence_cartridge`
- `related_path`: `src/core/persistence`
- `related_ref`: `STRANGLER_PLAN.md#phase-3-persistence-cartridge`

### Body

Implementation phase: Phase 3 persistence cartridge.

Changed files:
- src/core/persistence/schema.py: added SQLite schema version 1 / 1.0.0 for cartridge_manifest, semantic_objects, semantic_occurrences, semantic_relations, provenance_records, and derived vector/graph view placeholders.
- src/core/persistence/cartridge.py: added SemanticCartridge, manifest/readiness dataclasses, schema initialization, object upsert/read, occurrence lookup, relation/provenance projection queries, manifest refresh, and project-local cartridge path helper.
- src/core/persistence/__init__.py: exported persistence-layer contracts.
- tests/test_persistence.py: added schema initialization, object round-trip, occurrence/relation/provenance queryability, manifest/readiness, and idempotent relation projection tests.
- src/core/engine.py and tests/test_scaffold.py: updated runtime status to Phase 3 / Phase 4 next-tranche state.
- README.md: updated status wording.
- _docs/ARCHITECTURE.md: documented Phase 3 persistence cartridge schema and boundaries.
- _docs/PROJECT_STATUS.md: parked Phase 3 complete and recorded verification.
- _docs/STRANGLER_PLAN.md: marked Phase 3 parked complete.
- _docs/SOURCE_PROVENANCE.md: recorded that Phase 3 persistence is original project-owned implementation with no Tripartite code copied or imported.
- _docs/_journalDB/app_journal.sqlite3: appended this journal entry.

Implementation notes:
- The persistence cartridge stores full SemanticObject JSON by semantic_id while also projecting occurrence, relation, and provenance records into queryable tables.
- derived_vector_views and derived_graph_views are explicit future derived-view tables; this tranche does not claim mature vector search, graph analytics, or full Tripartite parity.
- The manifest is a singleton keyed by cartridge_id and tracks schema version, readiness, counts, timestamps, and notes.
- SQLite connections now use a persistence-owned context manager that always closes connections, which avoids Windows file-lock leaks in tests.
- This was an original implementation informed by doctrine and reference concepts only. No .parts runtime code, Tripartite schema text, or external imports were copied.

Testing and verification:
- python -m src.app status passed and reports Phase 3 active / Phase 4 next.
- python -m unittest discover -s tests passed with 14 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over src and tests found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- .dev-tools/_project-authority sqlite_schema_inspector gate passed with status=ok, user_version=1, and table_count=7.

Cleanup:
- Transient schema-gate SQLite files created under the OS temp folder were removed after inspection.
- Generated __pycache__ folders were removed only under src and tests after verification.

Parked status:
- Phase 3 is parked complete.
- Next tranche is Phase 4: Intake Adapter.

### Tags

```json
[
  "persistence",
  "semantic-cartridge",
  "sqlite",
  "phase-3",
  "parking"
]
```

### Metadata

```json
{
  "changed_files": [
    "README.md",
    "src/core/engine.py",
    "src/core/persistence/__init__.py",
    "src/core/persistence/cartridge.py",
    "src/core/persistence/schema.py",
    "tests/test_persistence.py",
    "tests/test_scaffold.py",
    "_docs/ARCHITECTURE.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/SOURCE_PROVENANCE.md",
    "_docs/_journalDB/app_journal.sqlite3"
  ],
  "tranche": "phase_3_persistence_cartridge",
  "status": "parked_complete",
  "verification": [
    "python -m src.app status",
    "python -m unittest discover -s tests",
    "python -m compileall src tests",
    "forbidden runtime reference scan",
    "sqlite_schema_inspector tool gate"
  ],
  "parts_borrowing": "none",
  "schema_version": 1,
  "schema_tables": [
    "cartridge_manifest",
    "semantic_objects",
    "semantic_occurrences",
    "semantic_relations",
    "provenance_records",
    "derived_vector_views",
    "derived_graph_views"
  ],
  "next_tranche": "Phase 4: Intake Adapter"
}
```

---

## Entry 7 - Phase 4 Intake Adapter Parked

- `created_at`: `2026-04-22T01:25:58Z`
- `updated_at`: `2026-04-22T01:25:58Z`
- `kind`: `implementation`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `3`
- `entry_uid`: `entry_20260422T012558Z_phase4_intake_adapter`
- `related_path`: `src/core/transformation`
- `related_ref`: `STRANGLER_PLAN.md#phase-4-intake-adapter`

### Body

Implementation phase: Phase 4 intake adapter.

Changed files:
- src/core/transformation/intake.py: added SourceDocument, SourceBlock, SourceReadError, UTF-8 source reading, conservative blank-line block splitting, Markdown heading detection, source-block to SemanticObject emission, and source/document ingestion into SemanticCartridge.
- src/core/transformation/__init__.py: exported the intake adapter contracts.
- tests/test_intake.py: added tests for line-span block splitting, heading detection, source-to-object provenance, source-path cartridge ingestion, and already-loaded document ingestion.
- src/core/engine.py and tests/test_scaffold.py: updated runtime status to Phase 4 / Phase 5 next-tranche state.
- README.md: updated project status wording.
- _docs/ARCHITECTURE.md: documented Phase 4 intake adapter behavior and non-goals.
- _docs/PROJECT_STATUS.md: parked Phase 4 complete and recorded verification.
- _docs/STRANGLER_PLAN.md: marked Phase 4 parked complete.
- _docs/SOURCE_PROVENANCE.md: recorded that Phase 4 intake is original project-owned implementation with no parts-bin code copied or imported.
- _docs/_journalDB/app_journal.sqlite3: appended this journal entry.

Implementation notes:
- The adapter reads UTF-8 text sources and emits canonical SemanticObject instances with verbatim, structural, grammatical, statistical, and empty semantic surfaces.
- Provenance is recorded as TransformStatus.IDENTITY_PRESERVING using method phase4_text_intake.
- Source spans are line-based and source references affect occurrence identity, not semantic identity.
- The adapter can persist emitted objects directly into SemanticCartridge.
- This is a minimal text/Markdown-ish adapter, not a full Splitter migration, TreeSitter parser, broad corpus ingestor, or embedding pipeline.
- No .parts runtime code, Splitter engine, token-budget code, or external parser dependency was copied, extracted, transplanted, or imported.

Testing and verification:
- python -m src.app status passed and reports Phase 4 active / Phase 5 next.
- python -m unittest discover -s tests passed with 19 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over src and tests found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- .dev-tools/_project-authority domain_boundary_audit passed with files_scanned=22 and total_violations=0.

Cleanup:
- Generated __pycache__ folders were removed only under src and tests after verification.

Parked status:
- Phase 4 is parked complete.
- Next tranche is Phase 5: Relation And Enrichment Pass.

### Tags

```json
[
  "transformation",
  "intake",
  "semantic-object",
  "phase-4",
  "parking"
]
```

### Metadata

```json
{
  "changed_files": [
    "README.md",
    "src/core/engine.py",
    "src/core/transformation/__init__.py",
    "src/core/transformation/intake.py",
    "tests/test_intake.py",
    "tests/test_scaffold.py",
    "_docs/ARCHITECTURE.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/SOURCE_PROVENANCE.md",
    "_docs/_journalDB/app_journal.sqlite3"
  ],
  "tranche": "phase_4_intake_adapter",
  "status": "parked_complete",
  "verification": [
    "python -m src.app status",
    "python -m unittest discover -s tests",
    "python -m compileall src tests",
    "forbidden runtime reference scan",
    "domain_boundary_audit tool gate"
  ],
  "parts_borrowing": "none",
  "next_tranche": "Phase 5: Relation And Enrichment Pass"
}
```

---

## Entry 8 - Phase 5 Relation Enrichment

- `created_at`: `2026-04-22T01:34:39Z`
- `updated_at`: `2026-04-22T01:36:01Z`
- `kind`: `phase`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T013423Z_phase5_relation_enrichment`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Files changed:
- README.md
- src/core/analysis/__init__.py
- src/core/analysis/enrichment.py
- src/core/engine.py
- src/core/persistence/cartridge.py
- tests/test_enrichment.py
- tests/test_persistence.py
- tests/test_scaffold.py
- _docs/ARCHITECTURE.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TOOLS.md

Summary:
Phase 5 implemented a bounded relation enrichment pass owned by the analysis layer. The pass emits source and heading membership relations, consecutive-block precedes/follows relations, and simple Markdown reference relations with traceable enrichment metadata and score components. Persistence gained a narrow upsert_relations projection path so enrichment relations attach to existing semantic IDs without changing canonical semantic object identity.

Implementation notes:
- Enrichment is original project-owned code; no parts-bin runtime code, Emitter nucleus, training logic, or graph assembler was copied or imported.
- Relation projections preserve non-enrichment relations already stored for an object.
- Phase 5 deliberately stops before traversal, learned scoring, spectral/TDA analysis, and UI work.

Verification:
- python -m unittest discover -s tests passed with 23 tests before parking docs.
- python -m compileall src tests passed.
- PowerShell forbidden-reference scan over src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src with files_scanned=23 and total_violations=0.
- domain_boundary_audit passed on tests with files_scanned=6 and total_violations=0.

Next:
Phase 6 - Traversal And Analysis.

Final verification update:
After parking documentation and runtime tranche marker updates, python -m unittest discover -s tests passed with 23 tests, python -m compileall src tests passed, the forbidden-reference scan over src/ and tests/ remained clean, and domain_boundary_audit again passed on both src and tests with total_violations=0.

Traceability correction:
Adjusted adjacency metadata so follows relations record their own source block and target block direction. Added a regression test for adjacency metadata direction. Final unit test count is now 24 passing tests.

### Tags

```json
[
  "phase5",
  "analysis",
  "relations",
  "persistence",
  "contract"
]
```

### Metadata

```json
{
  "tranche": "Phase 5",
  "next_tranche": "Phase 6"
}
```

---

## Entry 9 - Phase 6 Traversal And Analysis

- `created_at`: `2026-04-22T01:43:11Z`
- `updated_at`: `2026-04-22T01:43:11Z`
- `kind`: `phase`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T014254Z_phase6_traversal_analysis`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Files changed:
- README.md
- src/core/analysis/__init__.py
- src/core/analysis/traversal.py
- src/core/engine.py
- src/core/persistence/cartridge.py
- tests/test_scaffold.py
- tests/test_traversal.py
- _docs/ARCHITECTURE.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md

Summary:
Phase 6 implemented a bounded traversal and analysis artifact over persisted semantic cartridge relation projections. Traversal starts from a seed semantic_id, checks cartridge readiness and seed existence, walks outgoing and incoming relation projections within max-depth and max-step limits, and returns a deterministic TraversalReport with scored TraversalStep records.

Implementation notes:
- Persistence gained relations_targeting(target_ref) so analysis can inspect incoming relation projections without owning SQL details.
- Traversal preserves non-semantic targets, such as source/document anchors and external links, in the trace without pretending they are canonical semantic objects.
- Scoring is intentionally simple: relation weight times confidence times depth discount. This is trace metadata, not an advanced analysis claim.
- Implementation is original project-owned code. No NodeWALKER UI, mutation agent, patch approval flow, traversal implementation, or parts-bin runtime module was copied or imported.

Verification:
- python -m unittest discover -s tests passed with 29 tests after parking documentation.
- python -m compileall src tests passed.
- PowerShell forbidden-reference scan over src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src with files_scanned=24 and total_violations=0.
- domain_boundary_audit passed on tests with files_scanned=7 and total_violations=0.

Next:
Phase 7 - Minimal Execution Pathway.

### Tags

```json
[
  "phase6",
  "analysis",
  "traversal",
  "persistence",
  "contract"
]
```

### Metadata

```json
{
  "tranche": "Phase 6",
  "next_tranche": "Phase 7"
}
```

---

## Entry 10 - Phase 7 Minimal Execution Pathway

- `created_at`: `2026-04-22T01:51:42Z`
- `updated_at`: `2026-04-22T01:51:42Z`
- `kind`: `phase`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T015123Z_phase7_minimal_execution`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Files changed:
- README.md
- src/core/engine.py
- src/core/execution/__init__.py
- src/core/execution/pathway.py
- tests/test_execution.py
- tests/test_scaffold.py
- _docs/ARCHITECTURE.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md

Summary:
Phase 7 implemented the minimal execution pathway that closes the first prototype spine. Semantic traversal evidence can now become a SemanticIntent, intents can produce ExecutionPlan records, bounded report-generation or no-op execution can produce ExecutionResult records, and completed execution emits an execution_result SemanticObject with feedback relations to its plan and originating semantic objects.

Implementation notes:
- The executor is intentionally bounded to report_generation and no_op actions.
- Completed results are persisted through the existing SemanticCartridge rather than a new execution database.
- Feedback relations use executes_as for the plan and derives_from for origin semantic objects.
- Blocked execution returns diagnosable blockers without emitting a semantic object.
- No autonomous action system, trusted execution implementation, distributed consensus mechanism, external automation framework, or parts-bin runtime code was added.

Verification:
- python -m unittest discover -s tests passed with 33 tests before parking documentation.
- python -m compileall src tests passed.
- PowerShell forbidden-reference scan over src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src with files_scanned=25 and total_violations=0.
- domain_boundary_audit passed on tests with files_scanned=8 and total_violations=0.

Next:
Phase 8 - Thin MCP Usefulness Seam.

### Tags

```json
[
  "phase7",
  "execution",
  "prototype-spine",
  "contract"
]
```

### Metadata

```json
{
  "next_tranche": "Phase 8",
  "tranche": "Phase 7"
}
```

---

## Entry 11 - Phase 8 Thin MCP Usefulness Seam

- `created_at`: `2026-04-22T01:56:42Z`
- `updated_at`: `2026-04-22T01:56:42Z`
- `kind`: `phase`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T015622Z_phase8_mcp_usefulness_seam`
- `related_path`: `_docs/MCP_SEAM.md`

### Body

Files changed:
- README.md
- src/core/coordination/__init__.py
- src/core/coordination/mcp_seam.py
- src/core/engine.py
- tests/test_mcp_seam.py
- tests/test_scaffold.py
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md

Summary:
Phase 8 implemented a thin MCP usefulness seam as a local coordination contract. The seam defines capability descriptors for the completed prototype spine, input/output shapes for future MCP wrapping, usefulness scoring signals, aggregate usefulness reports, and an acceptance threshold for tuning.

Implementation notes:
- This is contract-only seam code, not a network server or full MCP protocol implementation.
- The seam exposes transformation, enrichment, traversal, execution, and persistence capability descriptors.
- Usefulness is scored by task fit, evidence quality, actionability, friction reduction, and repeatability.
- Runtime code avoids hidden coupling to quarantined reference/tool bins and does not import external MCP tooling.

Verification:
- python -m unittest discover -s tests passed with 37 tests after parking documentation.
- python -m compileall src tests passed.
- PowerShell forbidden-reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src with files_scanned=26 and total_violations=0.
- domain_boundary_audit passed on tests with files_scanned=9 and total_violations=0.

Next:
Prototype Tuning And Scoring: create repeatable builder-task fixtures and measure whether the seam actually reduces inspection, reasoning, and action cost for builder use.

### Tags

```json
[
  "phase8",
  "mcp-seam",
  "coordination",
  "usefulness",
  "tuning"
]
```

### Metadata

```json
{
  "next_tranche": "Prototype Tuning And Scoring",
  "tranche": "Phase 8"
}
```

---

## Entry 12 - Prototype Tuning And Scoring

- `created_at`: `2026-04-22T03:04:00Z`
- `updated_at`: `2026-04-22T03:04:00Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T030400Z_prototype_tuning_scoring`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- src/core/coordination/__init__.py
- src/core/coordination/prototype_scoring.py
- src/core/engine.py
- tests/test_prototype_scoring.py
- tests/test_scaffold.py

Summary:
Completed the prototype tuning and scoring tranche. Added a coordination-owned scoring harness with repeatable builder-task fixtures that run the full prototype spine from source intake through relation enrichment, semantic cartridge persistence, traversal, semantic intent, execution plan, execution result, feedback persistence, and MCP usefulness scoring. Exported the harness from the coordination layer and parked documentation around the scoring result and next local MCP adapter candidate.

Scoring snapshot:
- relation_evidence_trace: 0.91, accepted, next analysis.traverse_cartridge
- execution_report_trace: 0.91, accepted, next analysis.traverse_cartridge
- persistence_round_trip: 0.91, accepted, next analysis.traverse_cartridge

Implementation notes:
The harness scores all current MCP seam capability descriptors against task fit, evidence quality, actionability, friction reduction, and repeatability. This is still a local contract and scoring layer, not a network MCP server or protocol runtime. The current next tranche is a local MCP adapter pilot for analysis.traverse_cartridge.

Verification:
- python -m unittest discover -s tests passed with 41 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src: files_scanned=27, total_violations=0.
- domain_boundary_audit passed on tests: files_scanned=10, total_violations=0.

### Tags

```json
[
  "prototype",
  "tuning",
  "scoring",
  "mcp-seam"
]
```

### Metadata

```json
{
  "acceptance_threshold": 0.7,
  "aggregate_scores": {
    "relation_evidence_trace": 0.91,
    "persistence_round_trip": 0.91,
    "execution_report_trace": 0.91
  },
  "next_candidate": "analysis.traverse_cartridge"
}
```

---

## Entry 13 - Local MCP Adapter And Raw Inspector

- `created_at`: `2026-04-22T03:19:56Z`
- `updated_at`: `2026-04-22T03:19:56Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T031956Z_local_mcp_adapter_raw_inspector`
- `related_path`: `_docs/MCP_SEAM.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TOOLS.md
- src/app.py
- src/core/coordination/__init__.py
- src/core/coordination/local_mcp_adapter.py
- src/core/engine.py
- src/ui/mcp_inspector.py
- tests/test_local_mcp_adapter.py
- tests/test_scaffold.py

Summary:
Completed the local MCP adapter and raw inspector tranche. Added a project-owned local adapter pilot for analysis.traverse_cartridge that captures the capability descriptor, seam manifest, request payload, traversal response, usefulness report, and builder-facing notes into a raw inspection envelope. Added a minimal Tkinter raw JSON inspector panel and a headless JSON command through python -m src.app mcp-inspect --dump-json.

Implementation notes:
The adapter remains local and MCP-shaped only. It does not start a network server, register a real MCP protocol tool, persist inspection history, or integrate with the host application panel. The inspector is intentionally unformatted beyond raw JSON visibility. The current adapter usefulness score is 0.93 and meets the 0.7 acceptance threshold.

Verification:
- python -m unittest discover -s tests passed with 44 tests.
- python -m compileall src tests passed.
- python -m src.app mcp-inspect --dump-json emitted capture_id, analysis.traverse_cartridge, and aggregate_score 0.93.
- Forbidden runtime reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src: files_scanned=29, total_violations=0.
- domain_boundary_audit passed on tests: files_scanned=11, total_violations=0.

### Tags

```json
[
  "mcp-seam",
  "local-adapter",
  "inspector",
  "ui"
]
```

### Metadata

```json
{
  "commands": [
    "python -m src.app mcp-inspect",
    "python -m src.app mcp-inspect --dump-json"
  ],
  "acceptance_threshold": 0.7,
  "next_candidate": "true_mcp_tool_registration",
  "capability": "analysis.traverse_cartridge",
  "adapter_score": 0.93
}
```

---

## Entry 14 - True MCP Tool Registration Candidate

- `created_at`: `2026-04-22T03:28:51Z`
- `updated_at`: `2026-04-22T03:28:51Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T032851Z_true_mcp_tool_registration_candidate`
- `related_path`: `_docs/MCP_SEAM.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TOOLS.md
- src/app.py
- src/core/coordination/__init__.py
- src/core/coordination/mcp_tool_registry.py
- src/core/engine.py
- src/core/persistence/__init__.py
- tests/test_local_mcp_adapter.py
- tests/test_scaffold.py

Summary:
Completed the true MCP tool registration candidate tranche. Added a project-owned local MCP tool registry with the first registered candidate, ngraph.analysis.traverse_cartridge. The registered tool declares serializable input and output schemas, calls the existing traversal adapter from a JSON-like request, and returns a call envelope containing tool metadata, status, and the raw inspection capture.

Implementation notes:
This is still a local registration candidate, not a network server, protocol transport, host MCP tool installation, or external MCP SDK integration. The mcp-inspect command now routes through the registered tool call path. Added mcp-tools --dump-json to list registered candidates. Exported DEFAULT_CARTRIDGE_ID from the persistence package boundary so coordination does not reach around persistence ownership.

User-facing display:
Launched python -m src.app mcp-inspect after verification. The display process was still running after launch, indicating the raw inspector window was successfully started.

Verification:
- python -m unittest discover -s tests passed with 48 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src: files_scanned=30, total_violations=0.
- domain_boundary_audit passed on tests: files_scanned=11, total_violations=0.
- python -m src.app mcp-tools --dump-json emitted registry_id, readiness registration_candidate, and ngraph.analysis.traverse_cartridge.
- python -m src.app mcp-inspect --dump-json emitted call_id, ngraph.analysis.traverse_cartridge, and aggregate_score 0.93.

### Tags

```json
[
  "mcp-seam",
  "tool-registry",
  "registration-candidate",
  "inspector"
]
```

### Metadata

```json
{
  "commands": [
    "python -m src.app mcp-tools --dump-json",
    "python -m src.app mcp-inspect",
    "python -m src.app mcp-inspect --dump-json"
  ],
  "capability": "analysis.traverse_cartridge",
  "adapter_score": 0.93,
  "next_candidate": "persistent_mcp_inspection_history",
  "registered_tool": "ngraph.analysis.traverse_cartridge"
}
```

---

## Entry 15 - Persistent MCP Inspection History

- `created_at`: `2026-04-22T03:39:17Z`
- `updated_at`: `2026-04-22T03:39:17Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T033917Z_persistent_mcp_inspection_history`
- `related_path`: `_docs/MCP_SEAM.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TOOLS.md
- src/app.py
- src/core/coordination/__init__.py
- src/core/coordination/mcp_inspection_history.py
- src/core/engine.py
- tests/test_local_mcp_adapter.py
- tests/test_mcp_inspection_history.py
- tests/test_scaffold.py
- data/mcp_inspection/history.sqlite3 generated as runtime inspection history during display smoke

Summary:
Completed the persistent MCP inspection history tranche. Added a coordination-owned SQLite history store for registered MCP-shaped tool calls. The store preserves raw call/capture JSON and indexes call id, tool name, capability name, captured timestamp, status, and aggregate score. The mcp-inspect command now records the registered traversal call and displays a recent-history snapshot; mcp-history can display or dump persisted records.

Implementation notes:
The history store is builder-facing observability, not semantic cartridge truth. It remains project-owned under data/mcp_inspection/history.sqlite3 and uses only the Python standard library SQLite module. This is still not a protocol server, host tool installation, broad telemetry platform, retention policy, or polished visualization.

User-facing display:
Ran python -m src.app mcp-inspect --dump-json to create a project-local history record, then launched python -m src.app mcp-history. The display process was still running after launch with pid 62064.

Verification:
- python -m unittest discover -s tests passed with 53 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src: files_scanned=31, total_violations=0.
- domain_boundary_audit passed on tests: files_scanned=12, total_violations=0.
- mcp-inspect --dump-json emitted record_count, ngraph.analysis.traverse_cartridge, and aggregate_score 0.93.
- mcp-history --dump-json --history-limit 1 emitted history_path and record_count.

### Tags

```json
[
  "mcp-seam",
  "inspection-history",
  "tool-registry",
  "sqlite"
]
```

### Metadata

```json
{
  "commands": [
    "python -m src.app mcp-inspect",
    "python -m src.app mcp-history",
    "python -m src.app mcp-history --dump-json"
  ],
  "registered_tool": "ngraph.analysis.traverse_cartridge",
  "history_path": "data/mcp_inspection/history.sqlite3",
  "next_candidate": "project_document_ingestion_candidate",
  "adapter_score": 0.93
}
```

---

## Entry 16 - Project Document Ingestion Candidate

- `created_at`: `2026-04-22T03:45:54Z`
- `updated_at`: `2026-04-22T03:45:54Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T034554Z_project_document_ingestion_candidate`
- `related_path`: `_docs/MCP_SEAM.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TOOLS.md
- src/app.py
- src/core/coordination/__init__.py
- src/core/coordination/project_documents.py
- src/core/engine.py
- tests/test_project_documents.py
- tests/test_scaffold.py

Summary:
Completed the project document ingestion candidate tranche. Added a bounded curated project-document ingestion path for README.md, _docs/PROJECT_STATUS.md, _docs/MCP_SEAM.md, and _docs/STRANGLER_PLAN.md. The path ingests selected documents through the existing source-to-object adapter, enriches relations, persists them to a project document cartridge, selects a project-status seed, calls the registered traversal tool, and records the call into MCP inspection history.

Implementation notes:
The ingestion path is intentionally curated and project-owned. It is not a repo-wide scanner, arbitrary file ingestor, embedding pipeline, search engine, or pruning policy. The next tranche should score whether this real-doc traversal helps answer builder continuation questions.

Verification:
- python -m unittest tests.test_project_documents passed with 4 tests.
- Temporary-root smoke for python -m src.app mcp-ingest-docs --dump-json emitted document_paths, object_count, and ngraph.analysis.traverse_cartridge.

### Tags

```json
[
  "mcp-seam",
  "project-docs",
  "ingestion",
  "traversal"
]
```

### Metadata

```json
{
  "cartridge_path": "data/cartridges/project_documents.sqlite3",
  "next_candidate": "real_builder_task_scoring",
  "documents": [
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/MCP_SEAM.md",
    "_docs/STRANGLER_PLAN.md"
  ]
}
```

---

## Entry 17 - Real Builder Task Scoring

- `created_at`: `2026-04-22T03:49:12Z`
- `updated_at`: `2026-04-22T03:50:50Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T034912Z_real_builder_task_scoring`
- `related_path`: `_docs/MCP_SEAM.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TOOLS.md
- src/app.py
- src/core/coordination/__init__.py
- src/core/coordination/builder_task_scoring.py
- src/core/engine.py
- tests/test_builder_task_scoring.py
- tests/test_scaffold.py
- data/mcp_inspection/builder_task_scores.json generated by real project scoring

Summary:
Completed the real builder task scoring tranche. Added continuation-oriented task fixtures over ingested project documents, task-specific traversal seeds, aggregate usefulness scoring, inspection-history recording for each registered tool call, and a project-local score artifact. Added mcp-score-tasks --dump-json to run the scoring path.

Implementation notes:
This scoring harness evaluates whether the registered traversal/history surface helps answer real builder continuation questions. It is not a broad benchmark suite, learned evaluator, second tool candidate, or polished dashboard. The latest real-project scoring run produced aggregate score 0.93 and passed acceptance.

Verification:
- python -m unittest tests.test_builder_task_scoring tests.test_project_documents passed with 8 tests.
- Temporary-root smoke for python -m src.app mcp-score-tasks --dump-json emitted all four task ids, aggregate_score 0.7967, and meets_acceptance true.
- Real-project python -m src.app mcp-score-tasks --dump-json emitted all four task ids, aggregate_score 0.93, and meets_acceptance true.

Final gate update:
- python -m unittest discover -s tests passed with 61 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src: files_scanned=33, total_violations=0.
- domain_boundary_audit passed on tests: files_scanned=14, total_violations=0.
- Real project mcp-ingest-docs --dump-json emitted document_paths, object_count, and ngraph.analysis.traverse_cartridge.
- Real project mcp-score-tasks --dump-json emitted aggregate_score 0.93 and meets_acceptance true.

### Tags

```json
[
  "mcp-seam",
  "builder-task-scoring",
  "project-docs",
  "usefulness"
]
```

### Metadata

```json
{
  "aggregate_score": 0.93,
  "next_candidate": "history_aware_mcp_inspector",
  "tasks": [
    "current_tranche_lookup",
    "mcp_surface_lookup",
    "strangler_next_work_lookup",
    "operator_command_lookup"
  ],
  "score_artifact": "data/mcp_inspection/builder_task_scores.json"
}
```

---

## Entry 18 - History-Aware MCP Inspector

- `created_at`: `2026-04-22T04:28:53Z`
- `updated_at`: `2026-04-22T04:28:53Z`
- `kind`: `phase`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `entry_20260422T042852Z_history_aware_mcp_inspector`
- `related_path`: `_docs/TODO.md`

### Body

Files changed:
- README.md
- _docs/ARCHITECTURE.md
- _docs/MCP_SEAM.md
- _docs/PROJECT_STATUS.md
- _docs/PROTOTYPE_TUNING.md
- _docs/SOURCE_PROVENANCE.md
- _docs/STRANGLER_PLAN.md
- _docs/TODO.md
- _docs/TOOLS.md
- src/app.py
- src/core/coordination/__init__.py
- src/core/coordination/history_inspector.py
- src/core/engine.py
- src/ui/mcp_inspector.py
- tests/test_history_inspector.py
- tests/test_scaffold.py

Summary:
Completed the history-aware MCP inspector tranche and performed the full parking pass requested by the user. Added a coordination-owned history-aware inspector payload that summarizes persisted MCP calls, maps latest builder-task score artifacts back to call ids, and preserves the raw history snapshot. Updated the Tkinter inspector to show Summary and Raw JSON tabs when given a history-aware payload. Added mcp-history-view and mcp-history-view --dump-json commands.

Parking notes:
Updated the TODO and next-phase plan. Current completed tranche is History-Aware MCP Inspector. Recommended next tranche is Traversal Search And Seed Selection. The next phase should reduce manual seed-selection friction over ingested project documents without adding embeddings, a second tool candidate, or a polished UI yet.

User-facing display:
Launched python -m src.app mcp-history-view. The display process was still running after launch with pid 72784.

Verification:
- python -m unittest discover -s tests passed with 64 tests.
- python -m compileall src tests passed.
- Forbidden runtime reference scan over Python files in src/ and tests/ found no .parts, .dev-tools, _BDHyper, Tripartite, or NodeWALKER references.
- domain_boundary_audit passed on src: files_scanned=34, total_violations=0.
- domain_boundary_audit passed on tests: files_scanned=15, total_violations=0.
- python -m src.app mcp-history-view --dump-json emitted summary_text, calls, and raw history payload.

### Tags

```json
[
  "mcp-seam",
  "history-inspector",
  "parking",
  "todo"
]
```

### Metadata

```json
{
  "display_pid": 72784,
  "tests": 64,
  "next_candidate": "traversal_search_and_seed_selection",
  "command": "python -m src.app mcp-history-view"
}
```

---

## Entry 19 - Traversal Search And Seed Selection

- `created_at`: `2026-04-22T10:47:36Z`
- `updated_at`: `2026-04-22T10:49:10Z`
- `kind`: `tranche`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_a7c2311f39ea`
- `related_path`: `_docs/TODO.md`

### Body

Completed the Traversal Search And Seed Selection tranche. Added a coordination-owned seed search surface over the bounded project-document semantic cartridge, deterministic query-term ranking, selected traversal execution through ngraph.analysis.traverse_cartridge, and MCP inspection-history recording for selected seed traversals. Added persistence support for loading all objects and deleting stale objects for a re-ingested source so the project-document cartridge reflects current docs instead of retaining removed blocks. Wired the new python -m src.app mcp-search-seeds command with --query, --seed-limit, and --dump-json support, and launched a user-facing inspector for query Current Park Point (display pid 130460). Added focused tests for ranking, selected traversal history recording, and command output. Updated README, PROJECT_STATUS, MCP_SEAM, ARCHITECTURE, STRANGLER_PLAN, SOURCE_PROVENANCE, TOOLS, PROTOTYPE_TUNING, TODO, engine status, and scaffold expectations. Explicit non-goals held: no embeddings, no repo-wide scan, no full-text engine, no second registered tool candidate, no polished dashboard, and no runtime dependency on .parts or .dev-tools. Verification: focused seed/project/scaffold tests passed; python -m unittest discover -s tests passed with 67 tests; python -m compileall src tests passed; forbidden runtime reference scan over src/ and tests/ was clean; domain_boundary_audit passed on src with files_scanned=35 and total_violations=0; domain_boundary_audit passed on tests with files_scanned=16 and total_violations=0. Next recommended tranche: Search-Scored Traversal Tuning, to compare search-selected seeds against previous hint-selected calls and decide with evidence whether a second registered tool is justified.

Display correction: the first detached launch used an incorrectly quoted query and exited after argparse rejected the split words. Temporary stdout/stderr files from that check were removed. The user-facing seed-search inspector was relaunched successfully with query Current Park Point and is running as display pid 135904.

### Tags

```json
[
  "tranche",
  "mcp",
  "seed-search",
  "traversal",
  "parking"
]
```

### Metadata

```json
{
  "files_changed": [
    "README.md",
    "_docs/ARCHITECTURE.md",
    "_docs/MCP_SEAM.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/PROTOTYPE_TUNING.md",
    "_docs/SOURCE_PROVENANCE.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/TODO.md",
    "_docs/TOOLS.md",
    "src/app.py",
    "src/core/coordination/__init__.py",
    "src/core/coordination/project_documents.py",
    "src/core/coordination/seed_search.py",
    "src/core/engine.py",
    "src/core/persistence/cartridge.py",
    "tests/test_scaffold.py",
    "tests/test_seed_search.py",
    "data/cartridges/project_documents.sqlite3",
    "data/mcp_inspection/history.sqlite3"
  ],
  "display_pid": 130460,
  "next_tranche": "Search-Scored Traversal Tuning"
}
```

---

## Entry 20 - Webster Lexical Baseline

- `created_at`: `2026-04-22T12:23:04Z`
- `updated_at`: `2026-04-22T12:23:04Z`
- `kind`: `tranche`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_33c330ebec73`
- `related_path`: `_docs/WEBSTERS_BASELINE.md`

### Body

Completed the Webster Lexical Baseline tranche. Added a structured lexical parser for assets/_corpus_examples/dictionary_alpha_arrays.json that streams the alpha-array dictionary without loading the full file, preserves headword and definition_raw as the reliable baseline, and marks senses, domain labels, cross references, derived forms, and usage examples as conservative parser candidates. Added a batched SemanticCartridge.upsert_objects path so large corpus builds refresh manifests once per batch build rather than once per object. Added build_websters_baseline and lookup_websters_entry coordination surfaces, plus CLI commands python -m src.app ingest-websters and python -m src.app lookup-websters. Built the full data/cartridges/base_websters.sqlite3 cartridge with 102104 lexical entries, 102104 semantic objects, 117553 relations, and 102104 provenance records. Verified lookup-websters for tortuous and true-blue, including caution text for inferred fields. Added _docs/WEBSTERS_BASELINE.md and updated README, PROJECT_STATUS, TODO, ARCHITECTURE, STRANGLER_PLAN, SOURCE_PROVENANCE, TOOLS, engine status, and tests. Explicit non-goals held: no raw sliding-window dictionary ingestion, no perfect Webster grammar parser claim, no embeddings, no Python docs ingestion, no conversation corpus ingestion, and no merge into the project-document cartridge. Verification: python -m unittest discover -s tests passed with 75 tests; python -m compileall src tests passed; forbidden runtime reference scan over src/ and tests/ was clean; domain_boundary_audit passed on src with files_scanned=37 and total_violations=0; domain_boundary_audit passed on tests with files_scanned=17 and total_violations=0. User-facing lookup panel launched for tortuous with pid 143456. Next recommended tranche: Lexical Baseline Scoring And Layered Retrieval.

### Tags

```json
[
  "tranche",
  "websters",
  "lexical-baseline",
  "corpus",
  "parking"
]
```

### Metadata

```json
{
  "files_changed": [
    "README.md",
    "_docs/ARCHITECTURE.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/SOURCE_PROVENANCE.md",
    "_docs/STRANGLER_PLAN.md",
    "_docs/TODO.md",
    "_docs/TOOLS.md",
    "_docs/WEBSTERS_BASELINE.md",
    "src/app.py",
    "src/core/coordination/__init__.py",
    "src/core/coordination/websters_baseline.py",
    "src/core/engine.py",
    "src/core/persistence/cartridge.py",
    "src/core/transformation/__init__.py",
    "src/core/transformation/lexical.py",
    "tests/test_persistence.py",
    "tests/test_scaffold.py",
    "tests/test_websters_baseline.py",
    "data/cartridges/base_websters.sqlite3"
  ],
  "websters_entries": 102104,
  "websters_relations": 117553,
  "display_pid": 143456,
  "next_tranche": "Lexical Baseline Scoring And Layered Retrieval"
}
```

---

## Entry 21 - Park: Python Docs Projection Corpus Reassessment

- `created_at`: `2026-04-22T15:03:22Z`
- `updated_at`: `2026-04-22T15:03:22Z`
- `kind`: `phase_park`
- `status`: `complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `0`
- `entry_uid`: `journal_538f9341903b`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Reassessed the Python docs projection update against the builder constraint contract. Verified that the Python layer is project-owned, uses the project-local Python docs text corpus, summarizes isolated snippets with standard-library ast, and writes a separate python_docs cartridge without merging truth layers. Rebuilt the bounded Python docs cartridge: 387 semantic objects, 2170 relations, 90 API signatures, 106 code examples, 77 doctest examples, 42 grammar rules, and 183 AST-parseable snippets. Ran a three-layer probe over Webster, Python docs, and project documents; object/class/function/code phrases now resolve differently per layer, supporting the context-stack theory while confirming true query rebinding and layer arbitration remain next-tranche work. Full tests, compile, forbidden runtime reference scan, and domain boundary audits passed. Updated PROJECT_STATUS, TODO, ARCHITECTURE, STRANGLER_PLAN, and WEBSTERS_BASELINE for park continuity.

### Tags

```json
[
  "python-docs",
  "projection",
  "context-stack",
  "park"
]
```

### Metadata

```json
{
  "tranche": "Python Docs Projection Corpus",
  "next_tranche": "Context Projection / Rebinding Layer",
  "tests": "python -m unittest discover -s tests: 80 passed",
  "compileall": "passed",
  "src_domain_audit": "files_scanned=40,total_violations=0",
  "tests_domain_audit": "files_scanned=18,total_violations=0"
}
```

---

## Entry 22 - Docs: Next Session Thought Handoff

- `created_at`: `2026-04-22T15:10:03Z`
- `updated_at`: `2026-04-22T15:10:03Z`
- `kind`: `docs_handoff`
- `status`: `complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `0`
- `entry_uid`: `journal_45d4a3f6f8c6`
- `related_path`: `_docs/THOUGHTS_FOR_NEXT_SESSION.md`

### Body

Added _docs/THOUGHTS_FOR_NEXT_SESSION.md as a long-form non-authoritative handoff for the next session. The document captures the current prototype state, three-cartridge model, what the layered probe taught us, why Webster is an English prior rather than ground truth, why Python docs now function as a Python prior, why project docs are the local doctrine prior, and why the next tranche should build a context projection / rebinding layer instead of ingesting more data. Linked the handoff from PROJECT_STATUS.md, TODO.md, and ARCHITECTURE.md so future continuation starts from the current conceptual state. Sanity check confirmed the handoff file exists, expected sections are present, links are present, and content is ASCII-clean.

### Tags

```json
[
  "docs",
  "handoff",
  "context-projection",
  "next-session"
]
```

### Metadata

```json
{
  "handoff_file": "_docs/THOUGHTS_FOR_NEXT_SESSION.md",
  "linked_from": [
    "_docs/PROJECT_STATUS.md",
    "_docs/TODO.md",
    "_docs/ARCHITECTURE.md"
  ],
  "ascii_check": "passed"
}
```

---

## Entry 23 - Park: Context Projection And Generic English Lexicon Naming

- `created_at`: `2026-04-22T22:24:17Z`
- `updated_at`: `2026-04-22T22:26:27Z`
- `kind`: `phase_park`
- `status`: `complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `0`
- `entry_uid`: `journal_6b56740463ce`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Completed the Context Projection / Rebinding Layer tranche in bounded prototype form. Sanitized active app naming around the dictionary-derived baseline so code, commands, tests, generated cartridge names, and current documentation use generic English lexical terminology instead of source-branded component names. Rebuilt and verified data/cartridges/base_english_lexicon.sqlite3 with 102104 entries, 102104 semantic objects, 117553 relations, and 102104 provenance records, then removed the old generated source-branded cartridge file after verification. Added src/core/coordination/context_projection.py and the project-query command, which projects a raw query through english_lexical_prior, python_docs_projection, and project_local_docs while preserving per-layer candidates, scores, evidence notes, source references, heading context, compact metadata, selected layer, selected candidate, and caution text. Fresh probes showed object returns all three layers, for element in iterable return False selects python_docs_projection, semantic object provenance relations selects project_local_docs, and class object function selects python_docs_projection with class Foo(object): pass as the top candidate. Verification passed: python -m unittest discover -s tests passed with 85 tests; python -m compileall src tests passed; forbidden runtime/source-name scan over src/ and tests/ was clean; app-owned Markdown/text docs scan over README.md and _docs/ was clean apart from append-only historical journal records; domain_boundary_audit passed on src with files_scanned=41,total_violations=0 and tests with files_scanned=19,total_violations=0. Updated PROJECT_STATUS, TODO, ARCHITECTURE, STRANGLER_PLAN, README, ENGLISH_LEXICAL_BASELINE, SOURCE_PROVENANCE, and TOOLS for the sanitized naming and parked status. Next recommended tranche is Projection Scoring And MCP Inspection: tune projection usefulness, record project-query calls into inspection history, expose projection frames in the inspector, and decide whether project-query graduates to an MCP-shaped registered tool candidate.

Post-park alignment: advanced the runtime status surface so python -m src.app status now reports active_tranche=Projection Scoring And MCP Inspection and next_tranche=MCP Projection Tool Candidate Decision. Updated tests/test_scaffold.py accordingly. Re-ran python -m unittest discover -s tests: 85 passed; python -m compileall src tests: passed; forbidden runtime/source-name scan over src/ and tests/: clean; domain_boundary_audit remained clean on src and tests.

### Tags

```json
[
  "phase-park",
  "context-projection",
  "english-lexicon",
  "naming-sanitization",
  "mcp-inspection"
]
```

### Metadata

```json
{
  "tranche": "Context Projection / Rebinding Layer",
  "status": "parked_complete",
  "tests": "python -m unittest discover -s tests: 85 passed",
  "compileall": "passed",
  "src_domain_audit": "files_scanned=41,total_violations=0",
  "tests_domain_audit": "files_scanned=19,total_violations=0",
  "active_lexicon_cartridge": "data/cartridges/base_english_lexicon.sqlite3",
  "next_tranche": "Projection Scoring And MCP Inspection"
}
```

---

## Entry 24 - Park: Shared Command Spine For UI/MCP Projection

- `created_at`: `2026-04-22T23:16:05Z`
- `updated_at`: `2026-04-22T23:16:05Z`
- `kind`: `note`
- `status`: `open`
- `source`: `agent`
- `author`: ``
- `importance`: `0`
- `entry_uid`: `journal_021e992c6d98`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Implemented the shared command spine pilot around project-query. Added coordination-owned CommandEnvelope, ToolResultEnvelope, and InteractionCapture types; routed CLI project-query through the shared path; registered ngraph.project.query as an MCP-shaped candidate; recorded project-query captures in MCP inspection history beside traversal records; extended inspector summaries with selected layer and candidate count; added SemanticObject projection adapters for command/result envelopes without persisting interaction events as cartridge truth. Updated project documentation, refreshed project-doc ingestion, refreshed builder scoring, and parked the next tranche as UI Command Spine Pilot.

### Tags

```json
[
  "phase-park",
  "command-spine",
  "mcp-inspection",
  "project-query",
  "ui-mcp-alignment"
]
```

---

## Entry 25 - Park: UI Command Spine Pilot

- `created_at`: `2026-04-22T23:48:28Z`
- `updated_at`: `2026-04-22T23:48:28Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_173718aa6811`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Parked the UI Command Spine Pilot tranche.

What changed:
- Added a minimal Tk command surface behind `python -m src.app ui`.
- Added `run_ui_project_query`, which submits the same `ngraph.project.query` command path as CLI/MCP-shaped project-query calls.
- UI-originated actions now write shared `InteractionCapture` records into MCP inspection history with `actor="human"` and `source_surface="ui"`.
- The UI shows the existing history-aware inspector summary and the latest raw JSON capture; it does not become a polished dashboard or a separate source of truth.
- Updated engine status, README, architecture docs, MCP seam docs, tools docs, source provenance, project status, strangler plan, and TODO.

Verification:
- `python -m unittest discover -s tests` passed with 90 tests.
- `python -m compileall src tests` passed.
- Forbidden runtime/source-name scan over Python files was clean.
- Domain-boundary audits passed for `src` and `tests` with zero violations.
- `project-query "class object function"` still selects `python_docs_projection` with `candidate_count=330` and usefulness `0.95`.
- Real-doc builder scoring remains accepted at aggregate `0.75`; the weak `0.69` lookup fixtures are now the clear pressure for the next tranche.

Next tranche:
Layer Arbitration And Rebinding Scoring. Focus on deterministic fixtures that compare plain-English, Python, and project-local readings; tune selected-layer arbitration; keep the evidence visible through history/inspector instead of expanding UI surface area first.

### Tags

```json
[
  "phase-park",
  "ui-command-spine",
  "mcp-inspection",
  "project-query",
  "layer-arbitration"
]
```

---

## Entry 26 - Park: Layer Arbitration And Rebinding Scoring

- `created_at`: `2026-04-23T00:08:36Z`
- `updated_at`: `2026-04-23T00:08:36Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_bc26836ef5ea`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Parked the Layer Arbitration And Rebinding Scoring tranche.

What changed:
- Added `src/core/coordination/context_projection_scoring.py` with bounded arbitration fixtures for English lexical, Python docs, and project-local query intent.
- Added `python -m src.app project-query-score --dump-json`.
- The scorer drives each fixture through `run_project_query_interaction`, records normal `ngraph.project.query` captures in MCP inspection history, and writes `data/mcp_inspection/context_projection_scores.json`.
- Exported the scorer through the coordination package and added focused tests in `tests/test_context_projection_scoring.py`.
- Updated runtime status, README, architecture docs, MCP seam docs, tools docs, source provenance, strangler plan, TODO, and project status.

Verification:
- `python -m unittest discover -s tests` passed with 93 tests.
- `python -m compileall src tests` passed.
- Forbidden runtime/source-name scan over Python files was clean.
- Domain-boundary audits passed for `src` and `tests` with zero violations.
- `project-query-score` scored aggregate `0.96`; all three expected selected layers passed.
- `mcp-ingest-docs` refreshed the bounded project-document cartridge.
- `mcp-score-tasks` remains accepted at aggregate `0.81`, with unstable weak seed-selection fixtures around `current_tranche_lookup` and `operator_command_lookup`.

Interpretation:
The context projection layer is now measurable. The first English/Python/project-local arbitration fixtures pass without additional rule changes. The next useful work is not more projection scaffolding; it is deterministic seed-selection tuning for builder-task scoring, because the same real-doc hints can still land on nearby but less useful documents.

Next tranche:
Builder Task Seed Selection Tuning.

### Tags

```json
[
  "phase-park",
  "context-projection",
  "layer-arbitration",
  "project-query-score",
  "mcp-inspection"
]
```

---

## Entry 27 - Park: Builder Task Seed Selection Tuning

- `created_at`: `2026-04-23T02:45:16Z`
- `updated_at`: `2026-04-23T02:45:16Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_d85a25daa47e`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Parked the Builder Task Seed Selection Tuning tranche.

What changed:
- Added `src/core/coordination/seed_fitness.py` as the shared deterministic project-document seed-fitness scorer.
- Unified `mcp-search-seeds` and `mcp-score-tasks` onto the same ranked seed path.
- Added inspectable score breakdowns to selected seed candidates.
- Added a narrow builder-task policy for document-role fit, heading/section affinity, continuation-marker proximity, operator-command proximity, and expected source fit.
- Demoted source path ordering to a final stable fallback after score, structural score, and block order.
- Kept implementation inside `src/core/coordination/` and did not touch `context_projection.py`.

Verification:
- Focused seed/search/builder scoring tests passed with 11 tests.
- Full `python -m unittest discover -s tests` passed with 93 tests.
- `python -m compileall src tests` passed.
- Forbidden runtime/source-name scan over Python files was clean.
- Domain-boundary audits passed for `src` and `tests` with zero violations.
- `mcp-score-tasks` improved to aggregate `0.93`, with all four real builder-task fixtures scoring `0.93`.
- `mcp-search-seeds --query "Current Park Point"` selects `_docs/PROJECT_STATUS.md` and exposes score breakdown evidence.
- `mcp-search-seeds --query "mcp-history"` selects `README.md` and exposes score breakdown evidence.
- `project-query-score` remains accepted at aggregate `0.96` with all expected selected layers passing.

Guardrails honored:
No embeddings, no vector similarity, no merged priors, no persistent cross-cartridge coupling, and no projection/seed-fitness subsystem merge.

Next tranche:
Seed Fitness Inspector Visibility, so the useful score breakdowns are easier to inspect without digging through raw JSON.

### Tags

```json
[
  "phase-park",
  "seed-fitness",
  "builder-task-scoring",
  "mcp-inspection",
  "coordination"
]
```

---

## Entry 28 - Park: Seed Fitness Inspector Visibility

- `created_at`: `2026-04-23T03:23:22Z`
- `updated_at`: `2026-04-23T03:23:22Z`
- `kind`: `phase_park`
- `status`: `parked`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_8c22821e9055`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Completed the Seed Fitness Inspector Visibility tranche. mcp-search-seeds now includes a selected_flow window around the selected traversal seed, preserving previous / selected / next source objects from the same document in source order. The existing MCP inspector now recognizes seed-search payloads and renders Summary plus Raw JSON tabs; the summary shows selected seed metadata, matched terms, score breakdown, breadcrumb, source flow, and traversal counts. A user-facing seed-flow inspector was launched for Current Park Point. Verification passed: focused scaffold/seed/history tests, full unit discovery, compileall, forbidden-reference scan, domain-boundary audits, refreshed project-document ingestion, builder-task score 0.93 accepted, and project-query arbitration score 0.96 accepted. Next tranche is Projection Candidate Flow Visibility: apply the same flow-aware inspection pattern to project-query layers and candidates while preserving InteractionCapture raw JSON as the complete evidence.

### Tags

```json
[
  "phase-park",
  "seed-flow",
  "inspector",
  "seed-fitness",
  "mcp-inspection"
]
```

---

## Entry 29 - Pilot: Interaction Stream View

- `created_at`: `2026-04-23T03:33:16Z`
- `updated_at`: `2026-04-23T03:33:16Z`
- `kind`: `implementation_note`
- `status`: `complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_42e261788843`
- `related_path`: `src/ui/mcp_inspector.py`

### Body

Added a basic interaction stream over existing MCP inspection history. The new mcp-stream command emits or opens a polling Tk view with chronological query/response objects projected from persisted calls. Project-query captures show Q/R text, selected layer, candidate kind, score, preview, source, and call id; traversal calls degrade to seed traversal summaries. This remains history-first visibility only: no new event store, no message broker, no semantic cartridge persistence for interactions, and no network MCP server. Verification passed with 96 tests, compileall, forbidden-reference scan, and zero domain-boundary violations for src and tests.

### Tags

```json
[
  "interaction-stream",
  "mcp-inspection",
  "ui",
  "history-first"
]
```

---

## Entry 30 - Park: Seed Flow And Interaction Stream Visibility

- `created_at`: `2026-04-23T03:46:26Z`
- `updated_at`: `2026-04-23T03:46:26Z`
- `kind`: `phase_park`
- `status`: `parked`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_763ffeab92b0`
- `related_path`: `_docs/PROJECT_STATUS.md`

### Body

Parked the current development state after Seed Fitness Inspector Visibility plus interaction-stream polish. Documentation was updated across README and _docs to reflect selected_flow seed inspection, score breakdown visibility, formatted mcp-stream object blocks, incremental append behavior, scrollbar-hold autoscroll pause, and the next tranche Projection Candidate Flow Visibility. The project-document cartridge was refreshed from the updated bounded docs and now reports 445 semantic objects and 1639 relations. Verification passed: python -m unittest discover -s tests ran 96 tests OK; python -m compileall src tests passed; mcp-score-tasks remained accepted at aggregate 0.93; project-query-score remained accepted at aggregate 0.96; mcp-stream --dump-json --history-limit 5 emitted 5 stream items with 136 total records; status reports active_tranche=Seed Fitness Inspector Visibility and next_tranche=Projection Candidate Flow Visibility; forbidden-reference scan over src/tests was clean; domain_boundary_audit passed on src with 44 files and 0 violations and tests with 22 files and 0 violations. Next work should start by reviewing PROJECT_STATUS, TODO, MCP_SEAM, ARCHITECTURE, and THOUGHTS_FOR_NEXT_SESSION, then implement Projection Candidate Flow Visibility without changing cartridge boundaries or turning the UI into the source of truth.

### Tags

```json
[
  "phase-park",
  "documentation",
  "interaction-stream",
  "seed-flow",
  "mcp-inspection",
  "projection-next"
]
```

---

## Entry 31 - Park: Prototype Completion Visibility Gate

- `created_at`: `2026-04-23T13:44:56Z`
- `updated_at`: `2026-04-23T13:44:56Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal_cc6d1a7429e5`
- `related_path`: `_docs/PROJECT_STATUS.md`
- `related_ref`: `prototype_completion_visibility_gate`

### Body

Files changed: src/core/coordination/context_projection.py; src/core/coordination/history_inspector.py; src/core/coordination/seed_search.py; src/core/engine.py; src/ui/mcp_inspector.py; src/app.py; tests/test_context_projection.py; tests/test_history_inspector.py; tests/test_interaction_spine.py; tests/test_scaffold.py; README.md; _docs/PROJECT_STATUS.md; _docs/TODO.md; _docs/STRANGLER_PLAN.md; _docs/ARCHITECTURE.md; _docs/MCP_SEAM.md; _docs/PROTOTYPE_TUNING.md; _docs/TOOLS.md; _docs/SOURCE_PROVENANCE.md; _docs/THOUGHTS_FOR_NEXT_SESSION.md. Summary: completed projection candidate flow visibility, added the unified read-only mcp-cockpit surface, refreshed prototype tuning gate verification, and aligned runtime/documentation status to prototype completion. Verification: mcp-ingest-docs refreshed project docs cartridge to 478 objects and 1761 relations; mcp-score-tasks remained accepted at 0.93; project-query-score remained accepted at 0.96; project-query now returns selected_flow for nearby projection alternatives; mcp-cockpit emits latest scores/projection/seed/stream payload; unittest discovery passed with 99 tests; compileall passed; forbidden-reference scan found 0 violations; domain_boundary_audit passed on src and tests with 0 violations.

### Tags

```json
[
  "prototype",
  "visibility",
  "cockpit",
  "tuning",
  "park"
]
```

### Metadata

```json
{
  "builder_score": 0.93,
  "projection_score": 0.96,
  "project_doc_objects": 478,
  "project_doc_relations": 1761,
  "tests_passed": 99
}
```

---

## Entry 32 - Park: Local Host Bridge And Cross-Process Session Control

- `created_at`: `2026-04-23T23:54:32Z`
- `updated_at`: `2026-04-23T23:54:32Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `Codex`
- `importance`: `0`
- `entry_uid`: `journal:e01a4d46-ffd5-47f1-af03-fa0aee1ae039`
- `related_path`: `_docs/PROJECT_STATUS.md`
- `related_ref`: `local_host_bridge_and_cross_process_session_control`

### Body

Implemented the Local Host Bridge And Cross-Process Session Control tranche. Added a coordination-owned local bridge in src/core/coordination/host_bridge.py, wired the Tk host workspace to publish and heartbeat a session under data/host_bridge/, and added opt-in --use-host-bridge routing for project-query and mcp-search-seeds so approved external commands can target an already-open host window through the same canonical CommandEnvelope and dispatcher. Updated status, seam, tuning, workflow, and tooling docs to reflect the new bounded bridge model. Verification: 107 tests passing, compileall passing, forbidden reference scan clean, and bridged CLI smoke succeeded.

### Tags

```json
[
  "phase-park",
  "host-bridge",
  "cross-process",
  "ui",
  "coordination"
]
```

### Metadata

```json
{
  "bridge_cli_smoke": true,
  "builder_score": 0.93,
  "projection_score": 0.96,
  "tests_passed": 107
}
```

---

## Entry 33 - Phase Sync: Stable Prototype To Post-Prototype Hardening

- `created_at`: `2026-04-24T01:09:03Z`
- `updated_at`: `2026-04-24T01:09:03Z`
- `kind`: `phase_sync`
- `status`: `recorded`
- `source`: `codex`
- `author`: `codex`
- `importance`: `2`
- `entry_uid`: `journal-94ef62cc-d3a4-4c4c-b9c3-45807b44cc74`
- `related_path`: `_docs`
- `related_ref`: `post_prototype_hardening`

### Body

Recorded the documentation shift from prototype proving into post-prototype hardening. Updated the current canonical docs inline rather than creating a new history trail. The shift is now described across README, PROJECT_STATUS, TODO, EXPERIENTIAL_WORKFLOW, MCP_SEAM, PROTOTYPE_TUNING, and THOUGHTS_FOR_NEXT_SESSION. The main new framing is that the prototype is stable enough that the next risk is the clutter of success: unmanaged inspection history, bridge-state drift, and overlapping visibility surfaces. The next concrete tranche focus remains retention/pruning policy, bridge discipline, and surface ownership clarity.

### Tags

```json
[
  "phase_sync",
  "documentation",
  "hardening",
  "continuation"
]
```

### Metadata

```json
{
  "phase": "post_prototype_hardening_sync",
  "reason": "document_shift_inline",
  "files_changed": [
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/TODO.md",
    "_docs/EXPERIENTIAL_WORKFLOW.md",
    "_docs/MCP_SEAM.md",
    "_docs/PROTOTYPE_TUNING.md",
    "_docs/THOUGHTS_FOR_NEXT_SESSION.md"
  ],
  "next_focus": [
    "history retention/pruning policy",
    "bridge discipline",
    "surface ownership clarity"
  ],
  "tests_run": [],
  "doc_only": true
}
```

---

## Entry 34 - Park: Rolling Trace Retention And Bridge Cleanup

- `created_at`: `2026-04-24T01:41:28Z`
- `updated_at`: `2026-04-24T01:41:28Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `2`
- `entry_uid`: `journal-167505c0-032a-49e1-a5de-4d1c678ea0b2`
- `related_path`: `src/core/coordination`
- `related_ref`: `rolling_trace_retention`

### Body

Implemented the first post-prototype hardening slice. Added a rolling-trace policy for MCP inspection history with automatic pruning of old unpinned rows, automatic pinning of score-referenced call ids as durable evidence, and retention summaries exposed through history, stream, cockpit, and host workspace payloads. Added conservative bridge transport cleanup for stale request, response, and session files while keeping the bridge file-backed and subordinate to the shared command/state spine. Updated tranche markers and current docs so the project now presents post-prototype hardening as the active tranche and Controlled Expansion And Visibility Filtering as the next tranche.

### Tags

```json
[
  "phase_park",
  "hardening",
  "retention",
  "bridge_cleanup"
]
```

### Metadata

```json
{
  "phase": "post_prototype_hardening",
  "slice": "rolling_trace_retention_and_bridge_cleanup",
  "files_changed": [
    "src/core/coordination/mcp_inspection_history.py",
    "src/core/coordination/history_inspector.py",
    "src/core/coordination/host_workspace.py",
    "src/core/coordination/host_bridge.py",
    "src/core/coordination/__init__.py",
    "src/core/engine.py",
    "src/app.py",
    "src/ui/gui_main.py",
    "tests/test_history_inspector.py",
    "tests/test_host_bridge.py",
    "tests/test_host_workspace.py",
    "tests/test_scaffold.py",
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/TODO.md",
    "_docs/EXPERIENTIAL_WORKFLOW.md",
    "_docs/MCP_SEAM.md",
    "_docs/PROTOTYPE_TUNING.md",
    "_docs/THOUGHTS_FOR_NEXT_SESSION.md"
  ],
  "verification": {
    "focused_tests": "python -m unittest tests.test_history_inspector tests.test_host_bridge tests.test_host_workspace",
    "full_tests": "python -m unittest discover -s tests",
    "compile": "python -m compileall src tests",
    "status": "python -m src.app status",
    "history_dump": "python -m src.app mcp-history --dump-json",
    "cockpit_dump": "python -m src.app mcp-cockpit --dump-json",
    "forbidden_scan_clean": true,
    "full_test_count": 109
  },
  "next_focus": [
    "stream/cockpit filtering decisions",
    "shared command-spine expansion decisions",
    "operator-facing pin/promotion controls decision"
  ]
}
```

---

## Entry 35 - Park: Visibility Filtering For Stream And Cockpit

- `created_at`: `2026-04-24T01:59:12Z`
- `updated_at`: `2026-04-24T01:59:12Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `2`
- `entry_uid`: `journal-8ffe974c-2a99-4949-85da-5539b776b310`
- `related_path`: `src/core/coordination`
- `related_ref`: `visibility_filtering`

### Body

Implemented bounded exact-match filtering for the stream and cockpit visibility surfaces. Added optional tool and selected-layer filters to the shared payload builders and CLI commands so the operator can narrow the current read surface without mutating persisted history. The stream UI and raw payloads now report active filters, and the cockpit applies the same filter inputs to its assembled visibility payload. Updated status/TODO/docs so the project now treats operator promotion controls and shared-command expansion as the next bounded step after the current hardening work.

### Tags

```json
[
  "phase_park",
  "hardening",
  "visibility",
  "filtering"
]
```

### Metadata

```json
{
  "phase": "post_prototype_hardening",
  "slice": "visibility_filtering",
  "files_changed": [
    "src/core/coordination/history_inspector.py",
    "src/core/coordination/host_workspace.py",
    "src/core/engine.py",
    "src/app.py",
    "src/ui/mcp_inspector.py",
    "tests/test_history_inspector.py",
    "tests/test_host_workspace.py",
    "tests/test_scaffold.py",
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/TODO.md",
    "_docs/MCP_SEAM.md",
    "_docs/PROTOTYPE_TUNING.md",
    "_docs/THOUGHTS_FOR_NEXT_SESSION.md"
  ],
  "verification": {
    "full_tests": "python -m unittest discover -s tests",
    "compile": "python -m compileall src tests",
    "status": "python -m src.app status",
    "stream_filter_smoke": "python -m src.app mcp-stream --dump-json --tool-filter ngraph.project.query --layer-filter python_docs_projection",
    "cockpit_filter_smoke": "python -m src.app mcp-cockpit --dump-json --tool-filter ngraph.project.query --layer-filter python_docs_projection",
    "full_test_count": 112
  },
  "next_focus": [
    "operator-facing pin/promotion controls",
    "shared command expansion",
    "inspection-only versus persisted truth decision"
  ]
}
```

---

## Entry 36 - Park: Panel Readback And Shared Command Expansion

- `created_at`: `2026-04-24T03:49:32Z`
- `updated_at`: `2026-04-24T03:49:32Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `2`
- `entry_uid`: `journal-94dfd994-b491-4c67-9539-20db7d60824e`
- `related_path`: `_docs/PROJECT_STATUS.md`
- `related_ref`: `post_prototype_hardening`

### Body

This slice parked the host panel-read seam and the next bounded shared-command expansion.

What changed:
- the host now tracks the active tab and exposes active, named, and full-workspace panel readback through `mcp-read-panels`
- `status`, `mcp-tools`, `mcp-score-tasks`, and `project-query-score` now route through the shared host dispatcher
- the host workspace now includes Status and Tool Registry tabs as first-class surfaces
- bounded tuning was rerun on the current corpus and remained stable

Verification:
- `python -m unittest discover -s tests` passed with 120 tests
- `python -m compileall src tests` passed
- `python -m src.app status --dump-json` reports active tranche `Post-Prototype Hardening And Expansion` and next tranche `Truth-Surface Decisions And Controlled Corpus Expansion`
- `python -m src.app mcp-score-tasks --dump-json` remained at 0.93 accepted
- `python -m src.app project-query-score --dump-json` remained at 0.96 accepted

Why it matters:
- Codex can now ask the host what panel the operator is actually looking at instead of relying only on inference
- more of the operator-facing workflow now shares one canonical command/state path
- the next real decision is no longer command routing; it is whether interaction-derived semantic objects remain inspection-only or ever become persisted truth

### Tags

```json
[
  "phase_park",
  "hardening",
  "panel_readback",
  "shared_command_expansion",
  "bounded_tuning"
]
```

### Metadata

```json
{
  "phase": "post_prototype_hardening",
  "slice": "panel_readback_and_shared_command_expansion",
  "files_changed": [
    "src/core/coordination/host_workspace.py",
    "src/ui/gui_main.py",
    "src/core/coordination/host_bridge.py",
    "src/core/coordination/__init__.py",
    "src/app.py",
    "src/core/engine.py",
    "tests/test_host_workspace.py",
    "tests/test_host_bridge.py",
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/TODO.md",
    "_docs/MCP_SEAM.md",
    "_docs/THOUGHTS_FOR_NEXT_SESSION.md",
    "_docs/EXPERIENTIAL_WORKFLOW.md",
    "_docs/PROTOTYPE_TUNING.md"
  ],
  "verification": {
    "full_tests": "python -m unittest discover -s tests",
    "compile": "python -m compileall src tests",
    "status_dump": "python -m src.app status --dump-json",
    "tool_registry_dump": "python -m src.app mcp-tools --dump-json",
    "builder_score_dump": "python -m src.app mcp-score-tasks --dump-json",
    "projection_score_dump": "python -m src.app project-query-score --dump-json",
    "full_test_count": 120,
    "builder_score": 0.93,
    "projection_score": 0.96
  },
  "next_focus": [
    "truth-surface decision for interaction-derived semantic objects",
    "bounded project-document expansion decision",
    "bridge timeout ownership for longer-running scoring commands"
  ]
}
```

---

## Entry 37 - Park: Truth Policy And Controlled Corpus Expansion

- `created_at`: `2026-04-24T04:08:09Z`
- `updated_at`: `2026-04-24T04:08:09Z`
- `kind`: `phase_park`
- `status`: `parked_complete`
- `source`: `codex`
- `author`: `codex`
- `importance`: `2`
- `entry_uid`: `journal-0cb37969-6335-426d-89f2-76dfda00609d`
- `related_path`: `_docs/PROJECT_STATUS.md`
- `related_ref`: `post_prototype_hardening`

### Body

This paired slice parked two bounded follow-on tranches.

What changed:
- interaction-derived semantic-object projections now expose an explicit machine-readable truth policy
- status surfaces now report that these projections are inspection-only operational evidence, not cartridge truth
- controlled project-doc expansion now exists through named `core` and `expanded` profiles
- builder-task scoring, seed search, and project-doc ingestion can target those profiles explicitly

Verification:
- `python -m unittest discover -s tests` passed with 122 tests
- `python -m compileall src tests` passed
- `python -m src.app status --dump-json` now reports `interaction_truth_policy`
- `python -m src.app mcp-ingest-docs --project-doc-profile expanded --dump-json` rebuilt the project-doc cartridge to 877 objects / 3280 relations
- `python -m src.app mcp-score-tasks --project-doc-profile expanded --dump-json` remained accepted at 0.93
- `python -m src.app mcp-search-seeds --project-doc-profile expanded --query "Current Park Point" --dump-json` remained accepted at 0.93
- `python -m src.app project-query-score --dump-json` remained accepted at 0.96

What we learned:
- the truth boundary is now explicit instead of implied
- the expanded project-doc profile improves local doctrine coverage without degrading current builder-task usefulness
- the expanded profile is materially heavier, which makes bridge-timeout ownership the next practical policy question

### Tags

```json
[
  "phase_park",
  "truth_policy",
  "controlled_expansion",
  "project_docs",
  "post_prototype_hardening"
]
```

### Metadata

```json
{
  "phase": "post_prototype_hardening",
  "slice": "truth_policy_and_controlled_corpus_expansion",
  "files_changed": [
    "src/core/coordination/interaction_spine.py",
    "src/core/coordination/project_documents.py",
    "src/core/coordination/builder_task_scoring.py",
    "src/core/coordination/seed_search.py",
    "src/core/coordination/host_workspace.py",
    "src/core/coordination/__init__.py",
    "src/core/engine.py",
    "src/app.py",
    "tests/test_interaction_spine.py",
    "tests/test_project_documents.py",
    "tests/test_builder_task_scoring.py",
    "tests/test_host_workspace.py",
    "tests/test_scaffold.py",
    "README.md",
    "_docs/PROJECT_STATUS.md",
    "_docs/TODO.md",
    "_docs/MCP_SEAM.md",
    "_docs/THOUGHTS_FOR_NEXT_SESSION.md",
    "_docs/EXPERIENTIAL_WORKFLOW.md",
    "_docs/PROTOTYPE_TUNING.md"
  ],
  "verification": {
    "full_tests": "python -m unittest discover -s tests",
    "compile": "python -m compileall src tests",
    "status_dump": "python -m src.app status --dump-json",
    "expanded_ingest": "python -m src.app mcp-ingest-docs --project-doc-profile expanded --dump-json",
    "expanded_builder_score": "python -m src.app mcp-score-tasks --project-doc-profile expanded --dump-json",
    "expanded_seed_search": "python -m src.app mcp-search-seeds --project-doc-profile expanded --query \"Current Park Point\" --dump-json",
    "projection_score": 0.96,
    "full_test_count": 122,
    "expanded_project_doc_objects": 877,
    "expanded_project_doc_relations": 3280,
    "builder_score": 0.93
  },
  "next_focus": [
    "bridge timeout ownership for heavier scoring commands",
    "operator promotion metadata decisions",
    "bridge transport policy beyond file-backed local IPC"
  ]
}
```

---
