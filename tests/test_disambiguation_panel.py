"""Live-substrate disambiguation panel.

This is not a unit test on synthesized data. It is a falsifier panel that
runs against the actual built cartridges in this project's data directory
and asserts the layer that should win for each query, based on a
pre-decision recorded before the test was first run.

The panel exists to convert a known scoring bias from a conversation-only
diagnostic into a project artifact that survives session resets. It is
expected to fail today. The next tranche's pass/fail target is making it
pass.

If the real cartridges have not been built, the panel skips. To build them:

    python -m src.app ingest-lexicon --reset --dump-json
    python -m src.app ingest-python-docs --reset --dump-json
    python -m src.app mcp-ingest-docs --dump-json
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.core.coordination import project_context_query

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CARTRIDGE_ROOT = PROJECT_ROOT / "data" / "cartridges"
REQUIRED_CARTRIDGES = (
    CARTRIDGE_ROOT / "base_english_lexicon.sqlite3",
    CARTRIDGE_ROOT / "python_docs.sqlite3",
    CARTRIDGE_ROOT / "project_documents.sqlite3",
)

# Pre-decided expectations. Each entry: (query, expected_layer, rationale).
# These were committed to before the panel was first executed. Do not
# adjust them to match observed behavior - that defeats the falsifier.
DISAMBIGUATION_PANEL: tuple[tuple[str, str, str], ...] = (
    (
        "object",
        "project_local_docs",
        "Inside this project, 'object' is the canonical SemanticObject.",
    ),
    (
        "class object function",
        "python_docs_projection",
        "Three Python keywords together; the Python frame should win.",
    ),
    (
        "for element in iterable return False",
        "python_docs_projection",
        "Verbatim Python code shape; matches the all()/any() body.",
    ),
    (
        "semantic object provenance relations",
        "project_local_docs",
        "Project-local doctrine vocabulary.",
    ),
    (
        "contract",
        "project_local_docs",
        "The builder constraint contract is the dominant project meaning.",
    ),
    (
        "tranche",
        "project_local_docs",
        "Bounded work slice in this project; financial term in English.",
    ),
    (
        "bridge",
        "project_local_docs",
        "host_bridge is a project module and recurring architectural concern.",
    ),
    (
        "return",
        "python_docs_projection",
        "Return statement is the dominant code-shaped meaning.",
    ),
    (
        "orbit",
        "english_lexical_prior",
        "Control case: no project-local meaning; English should win.",
    ),
    (
        "iterable",
        "python_docs_projection",
        "Python protocol term; project mentions are incidental.",
    ),
)


class DisambiguationPanelTests(unittest.TestCase):
    """Falsifier panel against the live cartridges.

    Failure here is the point. The first time this panel passes, the
    substrate has earned the disambiguation claim its docs make.
    """

    @classmethod
    def setUpClass(cls) -> None:
        missing = [p.name for p in REQUIRED_CARTRIDGES if not p.exists()]
        if missing:
            raise unittest.SkipTest(
                "Disambiguation panel requires the live cartridges; "
                f"missing: {', '.join(missing)}"
            )

    def test_disambiguation_panel(self) -> None:
        for query, expected, rationale in DISAMBIGUATION_PANEL:
            with self.subTest(query=query, expected=expected):
                result = project_context_query(PROJECT_ROOT, query)
                actual = result.frame.selected_layer
                self.assertEqual(
                    actual,
                    expected,
                    msg=(
                        f"Disambiguation regression for {query!r}: "
                        f"expected layer {expected!r}, got {actual!r}. "
                        f"Rationale: {rationale}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
