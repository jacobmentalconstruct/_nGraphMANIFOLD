"""Structured lexical intake for dictionary-style corpora."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from src.core.representation import (
    ProvenanceRecord,
    RelationPredicate,
    SemanticObject,
    SemanticRelation,
    SemanticSurfaceSet,
    SourceSpan,
    TransformStatus,
)

ENGLISH_LEXICON_PARSE_VERSION = "v1"
ENGLISH_LEXICON_CORPUS_REF = "corpus:english_lexicon"

ENTRY_LINE_RE = re.compile(r'^\s*"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"\s*,?\s*$')
SENSE_MARKER_RE = re.compile(r"(?:^|\s)(\d+)\.\s+")
DOMAIN_LABEL_RE = re.compile(r"\(([A-Z][A-Za-z ,&-]{1,36})\.?\)")
CROSS_REFERENCE_RE = re.compile(r"\bSee\s+([^.;]+)")
DERIVED_FORM_RE = re.compile(r"--\s*([^.;]+)")
EXAMPLE_RE = re.compile(r"\bas,\s+([^.;]+[.;])")
QUOTED_EXAMPLE_RE = re.compile(r'"([^"]{8,240}[.!?])"')
CITED_EXAMPLE_RE = re.compile(
    r"((?:[A-Z][^.!?]{12,240}[.!?]))\s+"
    r"(Macaulay|Tennyson|Chaucer|Shak|Shakespeare|Milton|Spenser|Dryden|Bacon|Coleridge|Lowell|Southey|Holder)\."
)
PART_OF_SPEECH_RE = re.compile(r"\b(v\. t\.|v\. i\.|n\.|a\.|adv\.|prep\.|conj\.|interj\.|pl\.)\b")


@dataclass(frozen=True)
class LexicalSense:
    """One parsed definition sense from a lexical entry."""

    number: int | None
    definition: str
    domain_labels: tuple[str, ...] = ()
    usage_examples: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "number": self.number,
            "definition": self.definition,
            "domain_labels": list(self.domain_labels),
            "usage_examples": list(self.usage_examples),
        }


@dataclass(frozen=True)
class LexicalEntry:
    """Structured dictionary entry with raw text preserved."""

    headword: str
    normalized_headword: str
    definition_raw: str
    senses: tuple[LexicalSense, ...]
    domain_labels: tuple[str, ...]
    part_of_speech_hints: tuple[str, ...]
    cross_references: tuple[str, ...]
    derived_forms: tuple[str, ...]
    source_ref: str
    line_number: int
    parser_version: str = ENGLISH_LEXICON_PARSE_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "headword": self.headword,
            "normalized_headword": self.normalized_headword,
            "definition_raw": self.definition_raw,
            "senses": [sense.to_dict() for sense in self.senses],
            "domain_labels": list(self.domain_labels),
            "part_of_speech_hints": list(self.part_of_speech_hints),
            "cross_references": list(self.cross_references),
            "derived_forms": list(self.derived_forms),
            "source_ref": self.source_ref,
            "line_number": self.line_number,
            "parser_version": self.parser_version,
        }


def iter_dictionary_alpha_entries(path: Path | str) -> Iterator[LexicalEntry]:
    """Stream entries from dictionary_alpha_arrays.json without loading the file."""
    source_path = Path(path)
    source_ref = source_path.as_posix()
    with source_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            match = ENTRY_LINE_RE.match(line)
            if match is None:
                continue
            headword = json.loads(f'"{match.group(1)}"')
            definition = json.loads(f'"{match.group(2)}"')
            yield parse_dictionary_entry(headword, definition, source_ref, line_number)


def parse_dictionary_entry(
    headword: str,
    definition_raw: str,
    source_ref: str = "memory://english_lexicon",
    line_number: int = 1,
) -> LexicalEntry:
    """Parse one dictionary key/value pair into a conservative lexical record."""
    normalized = normalize_headword(headword)
    senses = tuple(_parse_senses(definition_raw))
    domain_labels = _unique(DOMAIN_LABEL_RE.findall(definition_raw))
    part_of_speech_hints = _unique(PART_OF_SPEECH_RE.findall(definition_raw))
    cross_references = _unique(item.strip() for item in CROSS_REFERENCE_RE.findall(definition_raw))
    derived_forms = _unique(item.strip() for item in DERIVED_FORM_RE.findall(definition_raw))
    return LexicalEntry(
        headword=headword,
        normalized_headword=normalized,
        definition_raw=definition_raw,
        senses=senses,
        domain_labels=domain_labels,
        part_of_speech_hints=part_of_speech_hints,
        cross_references=cross_references,
        derived_forms=derived_forms,
        source_ref=source_ref,
        line_number=line_number,
    )


def lexical_entry_to_semantic_object(entry: LexicalEntry) -> SemanticObject:
    """Create a semantic object that preserves one structured dictionary entry."""
    surfaces = SemanticSurfaceSet(
        verbatim={
            "headword": entry.headword,
            "definition_raw": entry.definition_raw,
        },
        structural={
            "corpus": ENGLISH_LEXICON_CORPUS_REF,
            "source_ref": entry.source_ref,
            "line_number": entry.line_number,
            "parser_version": entry.parser_version,
        },
        grammatical={
            "part_of_speech_hints": list(entry.part_of_speech_hints),
            "domain_labels": list(entry.domain_labels),
        },
        statistical={
            "definition_char_count": len(entry.definition_raw),
            "definition_token_count": len(entry.definition_raw.split()),
            "sense_count": len(entry.senses),
            "usage_example_count": sum(len(sense.usage_examples) for sense in entry.senses),
            "cross_reference_count": len(entry.cross_references),
            "derived_form_count": len(entry.derived_forms),
        },
        semantic={
            "normalized_headword": entry.normalized_headword,
            "senses": [sense.to_dict() for sense in entry.senses],
            "cross_references": list(entry.cross_references),
            "derived_forms": list(entry.derived_forms),
        },
    )
    relations = [SemanticRelation(predicate=RelationPredicate.MEMBER_OF, target_ref=ENGLISH_LEXICON_CORPUS_REF)]
    for reference in entry.cross_references:
        relations.append(
            SemanticRelation(
                predicate=RelationPredicate.REFERENCES,
                target_ref=f"lexical:{normalize_headword(reference)}",
                confidence=0.65,
                metadata={"basis": "dictionary_cross_reference_text", "raw_reference": reference},
            )
        )
    provenance = ProvenanceRecord(
        source_ref=entry.source_ref,
        transform_status=TransformStatus.REVERSIBLY_MAPPABLE,
        method="dictionary_alpha_json_structured_parse",
        confidence=0.95,
        metadata={"parser_version": entry.parser_version},
    )
    return SemanticObject.create(
        kind="lexical_entry",
        content=f"{entry.headword}: {entry.definition_raw}",
        surfaces=surfaces,
        relations=tuple(relations),
        provenance=(provenance,),
        source_ref=entry.source_ref,
        source_span=SourceSpan(start=entry.line_number, end=entry.line_number, unit="line"),
        local_context={
            "corpus": ENGLISH_LEXICON_CORPUS_REF,
            "headword": entry.headword,
            "normalized_headword": entry.normalized_headword,
        },
        metadata={
            "corpus": ENGLISH_LEXICON_CORPUS_REF,
            "headword": entry.headword,
            "normalized_headword": entry.normalized_headword,
            "parser_version": entry.parser_version,
        },
    )


def normalize_headword(headword: str) -> str:
    """Return the lookup-normalized form for a dictionary headword."""
    return " ".join(headword.strip().lower().split())


def _parse_senses(definition_raw: str) -> list[LexicalSense]:
    matches = list(SENSE_MARKER_RE.finditer(definition_raw))
    if not matches:
        text = definition_raw.strip()
        return [
            LexicalSense(
                number=None,
                definition=text,
                domain_labels=_unique(DOMAIN_LABEL_RE.findall(text)),
                usage_examples=_extract_usage_examples(text),
            )
        ]
    senses: list[LexicalSense] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(definition_raw)
        text = definition_raw[start:end].strip()
        if text:
            senses.append(
                LexicalSense(
                    number=int(match.group(1)),
                    definition=text,
                    domain_labels=_unique(DOMAIN_LABEL_RE.findall(text)),
                    usage_examples=_extract_usage_examples(text),
                )
            )
    return senses


def _extract_usage_examples(text: str) -> tuple[str, ...]:
    examples: list[str] = []
    examples.extend(EXAMPLE_RE.findall(text))
    examples.extend(QUOTED_EXAMPLE_RE.findall(text))
    examples.extend(match.group(1).strip() for match in CITED_EXAMPLE_RE.finditer(text))
    return _unique(examples)


def _unique(values: object) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen[text] = None
    return tuple(seen)
