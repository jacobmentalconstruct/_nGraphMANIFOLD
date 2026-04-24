# Experiential Workflow

_Status: active collaboration doctrine and designer handoff surface_

This document explains how we are actually using the contract, journal, logs,
onboarding, tooling, and scoring surfaces to build `nGraphMANIFOLD` across many
conversations, many park/resume cycles, and potentially many agents.

It is not the governing law. The governing law remains
`_docs/builder_constraint_contract.md`.

Think of this file as the "what it feels like to use the system" explanation.
It is meant to help a developer, designer, or new agent understand how the
pieces work together in lived practice.

## One-Sentence Summary

We are not using the project as a blank chat prompt every turn. We are using a
constrained build regimen where the contract sets the laws, the journal holds
durable builder memory, the status/TODO docs mark the current park point, the
tooling helps us inspect and patch safely, and the scoring harness tells us
whether our experiments are actually making the prototype more useful.

## What This Workflow Is Trying To Prevent

Without a regimen like this, long-running agent-assisted development drifts.
Each new conversation tends to:

- forget the last real stopping point
- over-trust the latest idea
- treat unfinished prototypes as if they are finished systems
- silently blur reference code, runtime code, and design memory
- skip verification because the discussion "sounds right"

This workflow exists to stop that.

It creates a stable project-side memory and constraint field so the work can
continue coherently even when:

- the conversation changes
- the active agent changes
- the user returns later
- the plan evolves
- experiments succeed, fail, or get deferred

## The Surfaces And What Each One Does

### 1. The Builder Constraint Contract: the constitution

File:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\builder_constraint_contract.md`

Role:

- defines the build laws
- fixes the trust boundary
- keeps runtime separate from references/tools
- enforces tranche discipline
- forces explicit non-goals
- requires documentation and reporting
- gives the builder permission to push back when a request would harm the app

Experientially, this is the thing that keeps us from "just doing whatever works
locally." It is what turns the project from a vibe-driven conversation into a
governed build.

### 2. The Builder Directive: the fast rehydration capsule

File:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\BUILDER_DIRECTIVE.md`

Role:

- compressed operational summary of the contract
- fast reminder before substantial work
- quick way to re-enter the project without rereading the full constitution

Experientially, this is the short "get your head straight before touching
anything" document.

### 3. The App Journal: durable builder memory

Files:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\_AppJOURNAL\`
- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\_journalDB\app_journal.sqlite3`

Role:

- canonical ledger of meaningful work phases
- records parks, pilots, decisions, tranche completions, and deferrals
- preserves continuity across sessions and agent resets
- gives us a queryable operational memory surface instead of loose markdown

What it is not:

- not runtime application data
- not a substitute for the contract
- not a junk drawer for every passing thought

Experientially, the journal is how the project remembers what happened after
the conversation window moves on. It is where "we finished this tranche, these
were the important files, this is what we proved, this is what remains" gets
stored in a durable way.

Recent journal titles show the actual rhythm we have been using:

- `Park: Shared Command Spine For UI/MCP Projection`
- `Park: UI Command Spine Pilot`
- `Park: Layer Arbitration And Rebinding Scoring`
- `Park: Builder Task Seed Selection Tuning`
- `Park: Seed Fitness Inspector Visibility`
- `Park: Seed Flow And Interaction Stream Visibility`
- `Park: Prototype Completion Visibility Gate`

That is the lived cadence: bounded tranche, verification, documentation, park.

### 4. Project Status: the current park marker

File:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\PROJECT_STATUS.md`

Role:

- quick continuation marker
- current tranche
- current park point
- in-scope work
- explicit non-goals
- next likely move
- current score snapshot

Experientially, this is the first "where exactly are we right now?" surface.
If the journal is the durable ledger, `PROJECT_STATUS.md` is the live bookmark.

### 5. TODO: the human-readable continuation checklist

File:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\TODO.md`

Role:

- current next tranche
- completed recent work
- backlog and deferred decisions
- what not to accidentally turn into scope creep

Experientially, this keeps the next step visible without requiring someone to
reconstruct priorities from raw journal entries.

### 6. Architecture, strangler plan, and blueprint docs: the structural map

Files:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\ARCHITECTURE.md`
- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\STRANGLER_PLAN.md`
- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_docs\semantic_os_conceptual_build_plan.md`

Role:

- explain what the app is supposed to become
- preserve major architectural intent
- prevent local convenience from replacing the actual target shape

Experientially, these docs let us ask, "does this next tranche move us toward
the real system, or are we just making the prototype busier?"

### 7. Onboarding surfaces: the session reset kit

Relevant file:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\.dev-tools\_project-authority\runtime\src\lib\builtin_templates\ANY_NEW_CONVO_READ_THIS_FIRST.md`

Role:

- tells a fresh conversation what to read first
- encodes the pickup loop
- keeps a new agent from charging into implementation with no shared context

Experientially, onboarding is how a "new mind" joins the work without starting
from zero.

### 8. Dev logs and logs: coarse external traces

Examples:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_logs\_nGraphMANIFOLD_filedump.txt`
- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\_logs\_nGraphMANIFOLD_project_folder_tree.txt`
- vendored toolbox dev logs under `.dev-tools`

Role:

- snapshots
- exports
- coarse file/system traces
- package/tool development history

What they are not:

- not the canonical builder memory
- not the live park marker
- not the constitutional source of truth

Experientially, logs help us inspect, audit, and export. They support the
workflow, but they do not define it.

### 9. The dev-tools: the toolbox, not the runtime

Root:

- `C:\Users\jacob\Documents\_AppDesign\_LivePROJECTS\_nGraphMANIFOLD\.dev-tools\`

Role:

- scanning
- auditing
- patching support
- journal tooling
- authority packaging
- vendable packages

Critical rule:

- `.dev-tools` may help us work on the project
- `.dev-tools` must not become an undeclared runtime dependency of the app

Experientially, this is one of the most important trust boundaries in the whole
workflow. The toolbox helps build the app, but the app must stand on its own.

## The Actual Session Loop We Use

This is the real collaboration loop we have been using.

### Step 1: Rehydrate

At the start of a meaningful session, we read enough of the project-side memory
to recover the active constraint field:

- contract
- directive
- project status
- TODO
- architecture/plan docs
- recent journal entries when needed

This is why the work can continue coherently even when the literal chat memory
is imperfect. The project stores its own continuity.

### Step 2: Name the tranche

Before substantial changes, we identify:

- current tranche
- what is in scope
- what is explicitly out of scope
- likely ownership domains
- how the work will be verified

This keeps us from quietly turning one good idea into three accidental
refactors.

When a tranche closes, we also notice whether the project has shifted phases.
That matters now. `nGraphMANIFOLD` has moved from prototype proving into
post-prototype hardening:

```text
before:
  prove the bounded prototype exists
  prove the host can be unified locally

now:
  keep the working prototype legible, bounded, and vendorable
```

Once that shift happens, the main risk becomes the clutter of success:

- too much history
- too many overlapping surfaces
- too little retention discipline
- too much accidental operational ambiguity

The first hardening slice now turns that into implementation discipline:

- the recent interaction trace is bounded
- durable score-linked evidence is intentionally pinned
- stale bridge transport files are cleaned
- the visibility surfaces expose the split instead of hiding it
- operator controls can now deliberately promote or demote the active
  interaction record, with score-linked evidence protected from casual demotion
- durable evidence can now also carry bounded operator authorship:
  label, reason, and note stored in history so later sessions can recover why
  a record mattered without turning that annotation into cartridge truth
- bridge/profile discipline is now also explicit enough to stop hand-waving:
  the bridge remains file-backed for now, and the `core` / `expanded` doc
  profiles are only meaningful because switching profiles now truly changes the
  cartridge contents instead of carrying stale docs forward

### Step 3: Build under the contract

During implementation, the contract and architecture keep us honest:

- write inside the project root
- keep ownership boundaries clean
- re-home anything inspired by references
- avoid hidden coupling to `.parts` or `.dev-tools`
- prefer conservative integration over "clever" shortcuts

### Step 4: Inspect what we just changed

We do not trust only the story of the change. We inspect it:

- source flow
- projection flow
- history records
- seed selection
- host workspace visibility
- raw JSON when needed

This matters because the app is not just code; it is behavior plus evidence.

When the host workspace is open, we can now also inspect a more unified
experience by targeting that already-open host from another process through the
local bridge. That means the visible workspace can react to external
`project-query` or `mcp-search-seeds` calls instead of making the human infer
what would have happened in the live session.

And now one more useful thing is true: the host can report back what the human
is currently looking at. Through `mcp-read-panels`, the builder can ask for:

- the active panel
- one named panel
- the full visible panel registry

That makes the shared-visible workflow less speculative. The collaboration no
longer has to rely only on "I think you are on the cockpit tab." The host can
say.

The workflow now also has a clearer truth boundary than before. Interaction
captures can be projected into semantic-object form for inspection, but that
does not make them cartridge truth. The current policy is explicit:

- cartridges remain runtime semantic truth
- interaction projections remain inspection adapters
- history and score artifacts remain operational evidence surfaces

### Step 5: Test and score the experiment

This is a big part of the workflow.

The regimen does not only help us build. It helps us evaluate whether the build
is becoming more useful.

We use repeatable commands and scoring artifacts to test experimental tranches:

- `python -m unittest discover -s tests`
- `python -m compileall src tests`
- `python -m src.app mcp-score-tasks --dump-json`
- `python -m src.app project-query-score --dump-json`
- `python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json`
- `python -m src.app project-query --query "class object function" --dump-json`
- `python -m src.app mcp-stream`
- `python -m src.app mcp-cockpit`
- `python -m src.app ui`

These do different jobs:

- tests verify correctness and regression safety
- audits verify boundary discipline
- score runs verify usefulness against repeatable fixtures
- visibility surfaces let us see the experiment happen, not just read a score

This is one of the strongest parts of the workflow: experiments are not only
"ideas we liked." They are things we can run, inspect, and score.

Concrete current examples:

- builder-task score: `0.93`, accepted
- projection arbitration score: `0.96`, accepted

And now, one more useful thing can be tested experientially:

- whether the live host session stays legible when an external command is
  bridged into it instead of being run on an isolated side path

That means the workflow supports a real loop:

```text
idea
  -> bounded tranche
  -> implementation
  -> visible inspection
  -> test
  -> score
  -> decision to keep, revise, or defer
```

In the hardening phase, this same loop becomes:

```text
propose a bounded experiment
  -> run fixtures and real-project scores
  -> inspect stream / cockpit / history / host workspace
  -> decide whether it is useful, legible, and contract-safe
  -> either keep it and park it, or reject/defer it
```

That is how scoring and visibility work together. The score prevents us from
mistaking novelty for progress, and the visibility surfaces let us inspect why
the result feels trustworthy or weak.

### Step 6: Update the docs so reality stays externalized

Once the tranche settles, we update the docs that future sessions will depend
on:

- `PROJECT_STATUS.md`
- `TODO.md`
- architecture/plan docs when needed
- tuning/provenance/tool docs when affected
- reflective notes when a session teaches us something important

This prevents the next session from having to infer project truth from code
diffs alone.

In the current hardening shift, the docs have one more job: they must explain
the phase change without creating a second historical trail. That means:

- the app journal records what changed and why
- `PROJECT_STATUS.md` says where the project is now
- `TODO.md` shows the operational transition and next step
- seam/tuning/workflow docs explain how to interpret the new phase

### Step 7: Park cleanly

At the end of a meaningful tranche, we leave a proper park:

- journal entry
- current status updated
- next tranche named
- risks or deferrals recorded
- verification noted

When a tranche teaches us something important, the park should now also try to
preserve a compact lessons-learned shape in the journal metadata:

- key decisions
- lessons learned
- evidence used
- rejected alternatives

This is still tranche memory, not micro-telemetry. The purpose is to make the
next session wiser, not noisier.

That is why the project can survive pauses without feeling abandoned.

## Why This Works Across Many Conversations And Agents

The key insight is that continuity does not live only inside the model. It also
lives in the project.

The workflow externalizes continuity into:

- contract surfaces
- journal entries
- status/TODO docs
- score artifacts
- inspection history
- bounded architectural docs

So a new conversation or a different agent does not have to "remember
everything." It has to rehydrate the same project-side truth.

That is why, from the human side, the collaboration can feel surprisingly
persistent even though inference happens in separate turns and sessions.

## Why It Keeps The Human And The Builder Together

It keeps us together because different surfaces solve different kinds of drift:

- the contract prevents structural drift
- the journal prevents historical drift
- the status/TODO docs prevent next-step drift
- the architecture docs prevent target-state drift
- the scores prevent "sounds good" drift
- the visibility tools prevent hidden-behavior drift

In plain language:

- the contract says what we are allowed to do
- the journal says what we actually did
- the park docs say where we are now
- the scores say whether the experiment helped
- the UI/inspector/stream/cockpit show what the system is doing

Now that the prototype is stable, this matters even more. If the surfaces start
overlapping without clear ownership, operator trust drops. Hardening is partly
about making each surface say one honest thing clearly.

That now includes a presentation rule:

- one main host workspace is the normal visible surface
- detached windows are for intentional side inspection, not the default rhythm

## The Difference Between Memory, Logs, And Runtime Truth

This distinction is important.

### Builder memory

Stored in the app journal and project docs.

Purpose:

- continuity
- doctrine
- work history
- phase handoff

### Logs and exports

Stored in `_logs/` and package/tool-specific outputs.

Purpose:

- trace
- diagnostics
- export
- audit support

### Runtime truth

Stored in the app's own runtime surfaces such as cartridges, inspection
history, and score artifacts.

Purpose:

- current application behavior
- query/projection evidence
- seed selection
- usefulness scoring

The workflow stays healthy because we do not casually blur these together.

## Journal Signal

The app journal is strongest when each meaningful park preserves the same
high-signal ingredients:

- what changed
- why it changed
- notable implementation or design decisions
- verification
- next focus
- compact lessons learned when a tranche revealed something worth carrying

The new rule is not "log everything." The new rule is:

```text
preserve the smallest durable explanation that would help a later builder avoid
having to relearn the same lesson from scratch
```

For external review, `_docs/DEV-LOG.md` is now generated as a readable mirror
of that append-only ledger. It remains a mirror only; the journal DB stays
authoritative.

## What A New Developer Or Agent Should Actually Do

If someone new joins the project, the practical pickup loop is:

1. Read the contract.
2. Read the directive.
3. Read `PROJECT_STATUS.md`.
4. Read `TODO.md`.
5. Read the relevant architecture/plan docs.
6. Read recent app-journal entries for the last few tranches.
7. Confirm the current tranche and explicit non-goals.
8. Only then propose or implement changes.

If the work is experimental, also:

1. identify how the experiment will be observed
2. identify how it will be scored
3. identify what a pass/fail result would mean
4. park the result even if the experiment is only partially successful

## What The Microsite Should Communicate

If this gets translated into a human onboarding microsite, the important story
is not "here are some tools."

The important story is:

1. this is a governed build workflow, not open-ended prompting
2. the contract sets the laws
3. the journal preserves memory across sessions
4. status/TODO keep the next move visible
5. tooling helps inspect and patch safely
6. scoring turns experiments into measurable progress
7. the live host can now be targeted locally without promoting transport into
   the architecture too early
8. every meaningful tranche ends with a clean park

If the microsite can make a developer feel that rhythm, it will be teaching the
real method.

## Short Version

The workflow works because it gives long-running agent collaboration five things
at once:

- laws
- memory
- visibility
- measurement
- parking discipline

That is how we have been able to keep building the same app across many
conversations without it dissolving into disconnected cleverness.
