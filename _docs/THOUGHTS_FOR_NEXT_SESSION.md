# Thoughts For Next Session

_Status: Reflective handoff for research and next-session planning_

_Created: 2026-04-22_

This document is not the governing contract. The governing contract remains
`builder_constraint_contract.md`. This file is a thinking surface: a place to
capture what the current prototype appears to be teaching us, what I think is
actually going on, and what the next session should preserve.

If there is a conflict between this document and the contract, the contract
wins. If there is a conflict between this document and implemented behavior,
implemented behavior should be inspected before trusting either memory or
enthusiasm.

## Read This First

The project is not drifting randomly. It feels like a long spiral because we
are turning around the same center from increasing radius: first object shape,
then persistence, then traversal, then MCP usefulness, then project documents,
then English lexical prior, then Python domain prior.

The important realization from the last tranche is this:

```text
We do not want dictionary search plus Python docs search plus project search.

We want a query to become a context-conditioned semantic object before it is
compared, traversed, executed, or exposed through MCP.
```

That is the real next step.

## Current One-Line State

nGraphMANIFOLD currently has a working semantic-object spine, three separated
knowledge/projection cartridges, and enough MCP-shaped inspection machinery to
show what the system sees; the next missing piece is an explicit context
projection and rebinding layer.

## What Exists Now

The current prototype spine is:

```text
source content
  -> SemanticObject
  -> relation enrichment
  -> semantic cartridge persistence
  -> traversal / analysis
  -> traceable execution result
  -> MCP-shaped usefulness seam
  -> raw inspection panel / JSON
  -> persistent inspection history
  -> selected project-document ingestion
  -> seed search
  -> English lexical cartridge
  -> Python docs projection cartridge
```

The spine is modest, but real. It means the app can already:

- turn text into canonical semantic objects
- preserve identity, occurrence, surfaces, relations, and provenance
- persist objects into SQLite cartridges
- enrich relations in a traceable way
- traverse relation projections from a selected seed
- score a local MCP-shaped tool surface for usefulness
- show raw evidence through a visible inspector
- ingest bounded project docs
- score builder tasks over project docs
- build a large English lexical baseline
- build a bounded Python docs/code projection corpus with AST summaries

That is not a semantic operating system yet. It is, however, a real substrate
for testing semantic operating system ideas.

## Current Cartridges

### Project Documents

Path:

```text
data/cartridges/project_documents.sqlite3
```

Purpose:

- project-local doctrine
- status
- plan continuity
- MCP seam documentation
- architecture and strangler plan surfaces

Recent refresh:

- `334` semantic objects
- `1230` relations

Interpretation:

This is the project-local prior. It knows what `SemanticObject`,
`provenance`, `contract`, `MCP seam`, `tranche`, and `current park point` mean
inside this project.

It is not a general knowledge base.

### English Lexical Prior

Path:

```text
data/cartridges/base_english_lexicon.sqlite3
```

Source:

```text
assets/_corpus_examples/dictionary_alpha_arrays.json
```

Recent full build:

- `102104` lexical entries
- `102104` semantic objects
- `117553` relations

Interpretation:

The English lexical baseline is an English lexical prior. It is useful for headwords, raw
definition text, simple lexical anchoring, and some conservative inferred
fields.

It is not ground truth. It is not final meaning. It should not override Python
or project-local contexts.

### Python Docs Projection

Path:

```text
data/cartridges/python_docs.sqlite3
```

Source:

```text
assets/_corpus_examples/python-3.11.15-docs-text
```

Bounded default docs:

```text
library/functions.txt
reference/compound_stmts.txt
reference/simple_stmts.txt
tutorial/controlflow.txt
```

Recent bounded build:

- `387` semantic objects
- `2170` relations
- `90` API signatures
- `106` code examples
- `77` doctest examples
- `42` grammar rules
- `183` AST-parseable snippets

Interpretation:

This is the Python domain prior. It is not just text. It extracts API
signatures, grammar, doctests, examples, and AST summaries. That makes it a
more structured lens than ordinary prose ingestion.

It is still not true rebinding. It is a layer that a rebinding process can use.

## What The Last Experiment Taught Us

The last test was small but important. We queried the same terms across three
separate cartridges without merging them.

### Query: `object`

English lexical layer returned:

- the lexical entry for `object`
- a broad English definition surface
- ordinary language senses such as opposition, thing, target, and object of
  thought/action

Python docs returned:

- `class Foo(object): pass`
- `iter(object)`
- `iter(object, sentinel)`

Project docs returned:

- `Phase 2: Canonical Semantic Object`
- project-local doctrine around the semantic object model

Lesson:

`object` is not one thing. The raw token is underdetermined. It needs a context
stack.

### Query: `class object function`

English lexical layer returned:

- general English `class`
- general English `function`
- general English `object`

Python docs returned:

- `issubclass(class, classinfo)`
- `class Foo(object): pass`
- function-definition examples

Project docs returned weakly:

- mostly the project-local `SemanticObject` material

Lesson:

The Python layer is doing exactly what we hoped: it reweights terms toward
programming structure without needing embeddings.

### Query: `for element in iterable return False`

English lexical layer returned:

- broad lexical noise around common words
- no useful code-level interpretation

Python docs returned:

- `def all(iterable): ... return False ... return True`
- `def any(iterable): ... return True ... return False`

Project docs returned:

- generic project-document blocks containing common words

Lesson:

This is a strong signal that the Python docs layer is not merely duplicating
English lookup. It can anchor code-shaped language to code-shaped examples.

### Query: `semantic object provenance relations`

English lexical layer returned:

- `object`
- `provenance`
- some broad entries containing `relations`

Python docs returned:

- mostly `object` in code/API contexts

Project docs returned:

- `SemanticObject`
- `ProvenanceRecord`
- relation doctrine
- project-local architecture content

Lesson:

The project-doc layer is our local doctrine prior. This matters because the
same terms that look ordinary in English become special once they enter this
project.

## What This Proves

The current system proves a narrower but meaningful claim:

```text
Separate context lenses can produce distinct, useful, inspectable anchors for
the same raw language.
```

That matters.

It means the system is not just accumulating more text. The cartridges can act
as separate semantic priors:

- English lexical baseline: English lexical prior
- Python docs: Python/code prior
- project docs: nGraphMANIFOLD local prior

The distinction between these priors is the thing to protect.

## What This Does Not Prove

The current system does not yet prove:

- full semantic grounding
- actual context-sensitive rebinding
- reliable layer arbitration
- embeddings or vector-space transformation
- symbolic reasoning
- complete Python understanding
- complete project understanding
- a finished MCP tool for contextual query projection
- semantic OS completeness

This is important. The result is encouraging because it points to the right
next mechanism, not because it means the mechanism already exists.

## The Main Conceptual Shift

Earlier we were tempted by this model:

```text
dictionary + corpus = better grounding
```

That is too flat.

The better model is:

```text
raw query
  -> English lexical prior
  -> Python domain prior
  -> project-local prior
  -> projected query object
  -> comparison / traversal / execution
```

The key change is that context is not just more data. Context should act like a
transformation operator.

In simpler language:

```text
The query should be changed by the context before the system decides what it
means.
```

That is the "dipping" idea.

## A Useful Mental Model

Think of each layer as a lens, not a bucket.

When a query enters the system, each layer should answer:

- What does this term or phrase mean in my frame?
- What anchors do I recognize?
- What surface evidence supports that recognition?
- What confidence do I have?
- What should I pass upward?
- What should I warn the next layer not to over-trust?

The higher layers should not simply override lower layers. They should rebind
them.

Example:

```text
English: "object" means a thing, goal, target, or opposition.
Python: "object" means also a root/base class and a runtime entity.
Project: "SemanticObject" means our canonical meaning-bearing unit.
```

The project interpretation does not delete the English one. It constrains it.

## Why This Is Not A Database

The persistence layer uses SQLite, but the app is not essentially a database.

A database stores and retrieves records. nGraphMANIFOLD is trying to preserve
and transform meaning-bearing structure:

- content
- occurrence
- identity
- surfaces
- relations
- provenance
- derived views
- traversal evidence
- execution feedback
- context-conditioned interpretation

SQLite is a storage mechanism. It is not the architecture.

## Why This Is Not Just Search

Search starts from a query and returns matching content.

This project is moving toward something else:

```text
raw phrase
  -> projected semantic object
  -> layer-specific evidence
  -> relation-aware traversal
  -> inspectable meaning/action path
```

Search is allowed to be one mechanism inside that path, but it should not own
the system.

The danger is accidentally building:

```text
dictionary search + docs search + project search
```

The target is:

```text
context-conditioned semantic projection
```

## Why This Is Not Just Embeddings

Embeddings might eventually help, but using them too soon could blur exactly
the edges we just discovered.

Right now the important discovery is that the layers have different meanings.
If we embed everything into one undifferentiated space too early, `object` may
become an averaged compromise:

- a thing
- a grammatical object
- a Python base type
- a project semantic unit

That average is not the target. The target is a controlled stack of
interpretations.

Embeddings should eventually become derived views, not the primary truth.

## Why The Python Docs Layer Matters

The Python docs layer is the first real domain prior.

The English lexical baseline gives us ordinary English. Project docs give us our local doctrine. But
Python docs give us a middle layer where ordinary words are intentionally
rebound:

- `object`
- `class`
- `function`
- `return`
- `for`
- `yield`
- `import`
- `callable`
- `iterator`
- `generator`

This is a good domain for the prototype because Python language has:

- prose
- API signatures
- grammar
- code examples
- doctests
- AST-parsable structure

That means the layer can combine lexical, syntactic, and structural evidence
without needing a full compiler.

## Why AST Summaries Are Important

The AST summaries are modest, but they make the Python layer more than text.

For parseable snippets, the layer can preserve:

- node kinds
- defined names
- referenced names
- imports
- call names
- control-flow forms
- top-level forms
- syntax errors when parsing fails

This is significant because it gives us a structured grammatical surface.

For a query like:

```text
for element in iterable return False
```

the system can eventually notice not only matching words, but also:

- `For`
- `If`
- `Return`
- function definition
- iterable parameter
- boolean return pattern

That is a bridge from text toward computation.

## What The MCP Layer Means Right Now

The MCP seam is still thin, but it is important because it forces the system to
show its work.

Current MCP-shaped usefulness:

- a registered local traversal candidate exists
- calls can be captured
- history can be persisted
- raw payloads can be inspected
- builder-task usefulness can be scored

For the next tranche, the MCP-facing goal should probably be:

```text
Expose the projected query frame and layer evidence.
```

In other words, when I use the tool, I should be able to see:

- raw query
- context stack
- English candidates
- Python candidates
- project-local candidates
- chosen projection
- scoring rationale
- warnings and non-goals

This is likely the most useful user-facing display in the near future.

## The Next Tranche In Plain English

Build a query projection layer.

It should accept:

- a raw query
- an optional context stack
- a set of cartridges to inspect
- a limit per layer

It should produce:

- a projected query frame
- candidates per layer
- evidence and scores
- layer-specific notes
- an explicit "not yet final semantic grounding" caution

It should not yet:

- merge cartridges
- create embeddings
- install a real MCP server
- build a polished UI
- ingest the entire repo
- treat dictionary lookup as ground truth
- pretend it understands everything

## Possible Next Implementation Shape

Likely new file:

```text
src/core/coordination/context_projection.py
```

Likely test file:

```text
tests/test_context_projection.py
```

Possible app command:

```text
python -m src.app project-query --query "object" --dump-json
```

or:

```text
python -m src.app mcp-project-query --query "object" --dump-json
```

I lean toward `mcp-project-query` only if it records inspection history or
returns MCP-shaped evidence. If it is simply a local coordination command,
`project-query` may be cleaner.

Possible data structures:

```text
ContextLayer
LayerCandidate
LayerProjection
QueryProjectionFrame
ContextProjectionResult
```

Possible layer names:

```text
english_english_lexicon_prior
python_docs_projection
project_local_docs
```

Possible scoring dimensions:

- exact phrase overlap
- term coverage
- ordered phrase proximity
- headword match
- API symbol match
- AST feature match
- heading/context match
- rarity or specificity
- broad-definition penalty
- layer fit
- provenance confidence

The first implementation should be deterministic and explainable, even if it
is crude.

## First Good Test Queries

Use these to avoid fooling ourselves:

```text
object
class object function
for element in iterable return False
semantic object provenance relations
return a value from a function
what is the current park point
how does traversal evidence work
```

Expected behavior:

- `object` should show all three layers with different meanings.
- `class object function` should favor Python.
- `for element in iterable return False` should strongly favor Python.
- `semantic object provenance relations` should favor project docs.
- `return a value from a function` should probably combine English and Python.
- `what is the current park point` should favor project docs.
- `how does traversal evidence work` should favor project docs and MCP seam.

## What Would Count As Success Next

The next tranche succeeds if:

- a query projection command exists
- it reads from the three existing cartridges
- it returns candidates per layer
- it gives inspectable scores
- it preserves cartridge separation
- it correctly shows different layer meanings for overloaded terms
- it does not claim final grounding
- tests cover the obvious examples
- docs explain what the layer is and is not

It does not need:

- perfect scoring
- full UI polish
- embeddings
- full-text index
- entire Python docs ingestion
- conversation corpus ingestion

## What To Be Careful About

### Do Not Merge The Cartridges Yet

The separation is a feature.

Merging the English lexicon, Python docs, and project docs too soon would erase the
evidence that different layers mean different things.

### Do Not Let The English Lexicon Dominate

The English lexicon is huge. It can produce a match for many terms. That does not make it
more correct.

Broad lexical matches should probably be penalized unless the query is clearly
asking for ordinary English meaning.

### Do Not Let Python Docs Become A Search Product

The Python docs layer is a projection lens. It should help rebind terms through
Python structure. It should not become "Python docs search" as the main app.

### Do Not Add Embeddings Too Soon

Embeddings may help once layer semantics are explicit. Before then, they risk
blurring the exact distinctions we are trying to preserve.

### Do Not Make The UI The Center

The visible panel is useful because it shows evidence. It should remain a
window into the core, not the owner of the core.

### Do Not Treat The Current Scoring As Truth

The small layered probe was hand-built and useful. It is not a benchmark. The
next tranche should make scoring explicit and testable.

## Important Philosophical Point

The app is trying to make meaning operational.

That means meaning is not only "stored." It is:

- represented
- transformed
- grounded
- reinterpreted
- traversed
- exposed
- eventually acted on

The phrase "semantic operating substrate" is not fluff if we keep building
toward this pattern:

```text
meaning-bearing object
  -> context-conditioned transformation
  -> relation-aware evidence
  -> inspectable action
```

That is the core.

## What I Think Is Really Happening

My read is that the project is discovering a practical architecture for
layered meaning.

The early phases built the skeleton:

- object
- persistence
- relations
- traversal
- execution trace

The MCP work made it visible to builders:

- tool surface
- inspection history
- scoring
- raw evidence panel

The corpus work started creating semantic priors:

- English
- Python
- project-local

Now the obvious pressure is between those priors. That pressure is the good
part. It means the app has enough pieces for ambiguity to become visible.

The next system capability is not "more data." It is controlled ambiguity
resolution.

## A Compact Name For The Current App

If I had to label the app today, I would call it:

```text
a context-projected semantic cartridge workbench
```

Or, more plainly:

```text
a tool for turning documents and code-shaped language into inspectable,
layered semantic objects
```

The future version wants to be more:

```text
a semantic operating substrate for context-conditioned meaning and action
```

But today, the honest label is still workbench/substrate prototype.

## Research Directions For Today

These are useful topics to think about while away from the code.

### Context And Meaning

- frame semantics
- context-dependent meaning
- word sense disambiguation
- semantic frames
- concept lattices
- formal concept analysis
- contextual rewriting
- type-directed interpretation

Useful question:

```text
How do systems decide which meaning of a term is active inside a context?
```

### Layered Knowledge Systems

- knowledge graphs
- ontology alignment
- graph RAG
- hierarchical memory systems
- provenance-aware retrieval
- multi-hop evidence assembly

Useful question:

```text
How can one layer constrain another without deleting its evidence?
```

### Program Understanding

- AST summarization
- static analysis
- symbol tables
- docstring extraction
- executable examples as semantic anchors
- API signature matching

Useful question:

```text
What is the smallest useful Python semantic prior that helps interpret
developer language?
```

### Data Integrity And Identity

- content-addressed storage
- Merkle DAGs
- provenance graphs
- immutable event logs
- derivation lineage

Useful question:

```text
When do we need a Merkle root, and what exactly is it rooting?
```

My current answer: not yet at the binary root stage. We first need stable
semantic-object identity, projection frames, and provenance. A Merkle DAG
becomes more valuable once we know what transformations and cartridge states
need attestable roots.

### Tool Use For Builders

- MCP tool design
- inspectable tool outputs
- agent-facing observability
- raw evidence panels
- scoring usefulness for actual work

Useful question:

```text
What would make this tool immediately useful to Codex during development?
```

My current answer: a context projection tool that shows what it sees, why it
ranked each layer, and which evidence should guide the next action.

## The Core Design Tension

We want the system to become powerful without becoming vague.

The contract helps here. It forces:

- bounded tranches
- explicit non-goals
- provenance
- local ownership
- no hidden `.parts` coupling
- documentation after meaningful work

The conceptual risk is over-expansion. The technical risk is premature
abstraction. The practical risk is building a search app and calling it
semantic.

The way through is:

```text
small explicit object
small explicit relation
small explicit projection
small explicit score
small explicit inspection surface
```

Then repeat.

## Next Session Starter Plan

When returning, I would start like this:

1. Read `builder_constraint_contract.md`.
2. Read `PROJECT_STATUS.md`.
3. Read this document.
4. Inspect `src/core/coordination/python_docs_corpus.py`.
5. Inspect `src/core/coordination/english_lexicon.py`.
6. Inspect `src/core/coordination/seed_search.py`.
7. Implement `context_projection.py` as a deterministic coordination layer.
8. Add tests proving layer separation and scoring.
9. Add a headless JSON command.
10. Only then consider a user-facing panel for projected query evidence.

## Suggested Next Tranche Contract

Name:

```text
Context Projection / Rebinding Layer
```

In scope:

- deterministic query projection frame
- per-layer candidate extraction from existing cartridges
- layer-specific scoring
- evidence/provenance output
- tests with known ambiguous queries
- documentation of what is and is not rebinding

Explicit non-goals:

- no embeddings
- no FTS engine
- no cartridge merge
- no full MCP server
- no new corpus ingestion
- no polished UI
- no autonomous agent behavior
- no Merkle DAG implementation

Done when:

- `python -m src.app <query-command> --query "object" --dump-json` returns
  layer-separated evidence
- code-shaped queries favor Python
- project-doctrine queries favor project docs
- broad English terms still preserve English lexical evidence without dominating
- all tests and audits pass
- docs and journal are parked

## Personal Read On The Spiral

I do not think we are lost.

I think we are in the part of the spiral where the same idea keeps reappearing
at higher resolution:

- First: "What is the object?"
- Then: "Where does the object live?"
- Then: "How does it relate?"
- Then: "Can it be traversed?"
- Then: "Can a builder use it?"
- Then: "What grounds its language?"
- Now: "How does context change what it means?"

That is not orbiting in place. That is converging.

The caution is that convergence can feel like circling because the central
question stays visible the whole time. But the artifacts are becoming more
specific, testable, and useful.

## Final Thought For Later

The best next move is not to ingest more. It is to make the system explain how
the existing layers reinterpret one query.

If the next tranche can show:

```text
"object" as English
"object" as Python
"object" as nGraphMANIFOLD doctrine
```

and then produce a projected query frame that says:

```text
Given this context stack, here is the meaning I will carry forward.
```

then the prototype will have crossed an important threshold.

That would be the first real version of "dipping."

