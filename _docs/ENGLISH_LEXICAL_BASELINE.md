# English Lexical Baseline

_Status: Prototype baseline built, generic naming sanitized_

This document records the first structured English lexical baseline for
nGraphMANIFOLD. It is subordinate to `builder_constraint_contract.md`.

The app treats this as an English lexical prior, not as a branded project
component and not as final semantic truth.

## Source

Project-owned source:

```text
assets/_corpus_examples/dictionary_alpha_arrays.json
```

The file is treated as a derived dictionary alpha-array:

```text
headword -> definition text
```

The source is reliable for headword and raw definition text. The alpha-array
file does not expose separate explicit fields for example sentence, part of
speech, sense, or domain. Those fields are parser candidates inferred from the
definition text.

## Cartridge

Baseline cartridge:

```text
data/cartridges/base_english_lexicon.sqlite3
```

Latest full build:

- entries seen: `102104`
- semantic objects written: `102104`
- relation count: `117553`
- provenance count: `102104`

## Commands

Build or rebuild the full baseline:

```bat
python -m src.app ingest-lexicon --reset --dump-json
```

Build a bounded sample:

```bat
python -m src.app ingest-lexicon --limit 1000 --reset --dump-json
```

Look up a headword:

```bat
python -m src.app lookup-lexicon --query tortuous --dump-json
```

## Parser Contract

The lexical parser preserves:

- headword
- normalized headword
- raw definition text
- source path
- source line
- parser version

It conservatively infers:

- numbered senses
- domain labels such as `Astrol`
- cross references beginning with `See`
- derived-form tails beginning with `--`
- usage-example candidates from obvious `as, ...`, quoted, or author-cited
  patterns

These inferred fields are useful for prototyping, but they are not authoritative
dictionary schema. Downstream tools must prefer `definition_raw` when certainty
matters.

## Naming Policy

The lexical layer must use generic project terminology:

- English lexical baseline
- English lexical prior
- dictionary alpha-array source
- English lexicon cartridge

It must not name the app component, commands, code modules, or cartridge files
after a particular dictionary source. Sources may still be attributed in source
provenance where legally or historically necessary, but the app architecture
should remain source-replaceable.

## Non-Goals

- no raw sliding-window dictionary ingestion
- no claim of perfect dictionary grammar parsing
- no embeddings
- no merge into the project-document cartridge
- no Python docs or conversation corpus ingestion in this layer
- no replacing project status truth with lexical truth

## Layered Probe Note

2026-04-22 reassessment confirms the English lexical baseline behaves usefully
as a headword and definition anchor for ordinary terms such as `object`,
`function`, and `provenance`. Code-shaped language such as
`for element in iterable return False` produces broad lexical noise and should
be handled by the Python-context layer instead.

This preserves the intended boundary: the English lexicon is a base English
prior, not a final arbiter of meaning.

## Next Work

The context projection layer should score how useful the English lexical
baseline is when layered under Python and project-local interpretation. It
should keep lexical lookup separate from project status lookup and measure
whether English grounding helps or distracts.
