"""Transformation layer boundary and source intake adapters."""

from .intake import (
    SourceBlock,
    SourceDocument,
    SourceReadError,
    ingest_documents_to_cartridge,
    ingest_source_to_cartridge,
    markdown_heading_text,
    read_text_source,
    semantic_objects_from_source,
    split_text_blocks,
)
from .lexical import (
    ENGLISH_LEXICON_CORPUS_REF,
    ENGLISH_LEXICON_PARSE_VERSION,
    LexicalEntry,
    LexicalSense,
    iter_dictionary_alpha_entries,
    lexical_entry_to_semantic_object,
    normalize_headword,
    parse_dictionary_entry,
)
from .python_ast import (
    PYTHON_AST_PROJECTION_VERSION,
    PythonAstSummary,
    summarize_python_ast,
)
from .python_docs import (
    PYTHON_DOCS_EXTRACTION_VERSION,
    PythonDocsRecord,
    extract_python_docs_file,
    iter_python_docs_records,
)

__all__ = [
    "PYTHON_AST_PROJECTION_VERSION",
    "PYTHON_DOCS_EXTRACTION_VERSION",
    "ENGLISH_LEXICON_CORPUS_REF",
    "ENGLISH_LEXICON_PARSE_VERSION",
    "LexicalEntry",
    "LexicalSense",
    "PythonAstSummary",
    "PythonDocsRecord",
    "SourceBlock",
    "SourceDocument",
    "SourceReadError",
    "extract_python_docs_file",
    "ingest_documents_to_cartridge",
    "ingest_source_to_cartridge",
    "iter_dictionary_alpha_entries",
    "iter_python_docs_records",
    "lexical_entry_to_semantic_object",
    "markdown_heading_text",
    "normalize_headword",
    "parse_dictionary_entry",
    "read_text_source",
    "semantic_objects_from_source",
    "summarize_python_ast",
    "split_text_blocks",
]
