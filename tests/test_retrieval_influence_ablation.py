"""Retrieval influence ablation fixture tests."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from src.app import main
from src.core.coordination import (
    RETRIEVAL_INFLUENCE_ABLATION_VERSION,
    default_retrieval_influence_ablation_path,
    run_retrieval_influence_ablation,
    save_retrieval_influence_ablation_run,
)
from src.core.coordination.retrieval_outside_eval import RetrievalEvalQuery


class FakeSentenceTransformer:
    """Small deterministic stand-in for tests."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(
        self,
        texts: list[str] | tuple[str, ...],
        *,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        del normalize_embeddings, show_progress_bar
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append(
                [
                    float(lowered.count("current") + lowered.count("park")),
                    float(lowered.count("history") + lowered.count("mcp")),
                    float(lowered.count("prototype") + lowered.count("work")),
                    1.0,
                ]
            )
        matrix = np.asarray(vectors, dtype=float)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        return matrix / norms


class RetrievalInfluenceAblationTests(unittest.TestCase):
    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(
            "# nGraphMANIFOLD\n\n"
            "## Run\n\n"
            "Use project-query and mcp-history commands for visible inspection.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\n"
            "## Current Park Point\n\n"
            "Current Park Point records where the project is parked and what comes next.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\n"
            "## Persistent Inspection History\n\n"
            "MCP inspection history keeps saved command evidence visible.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\n"
            "## Immediate Post-Prototype Work\n\n"
            "Immediate Post-Prototype Work describes the next controlled hardening step.\n",
            encoding="utf-8",
        )

    def test_ablation_compares_baseline_deterministic_and_ml_methods(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._write_project_docs(root)
            queries = (
                RetrievalEvalQuery(
                    query_id="park",
                    query="Current Park Point",
                    acceptable_source_suffixes=("PROJECT_STATUS.md",),
                    preferred_heading_terms=("current park point",),
                ),
                RetrievalEvalQuery(
                    query_id="history",
                    query="saved MCP inspection history",
                    acceptable_source_suffixes=("MCP_SEAM.md",),
                    preferred_heading_terms=("persistent inspection history",),
                ),
            )
            with patch("src.core.coordination.project_query_lens_bag.SentenceTransformer", FakeSentenceTransformer):
                run = run_retrieval_influence_ablation(root, queries=queries)
                output_path = save_retrieval_influence_ablation_run(
                    run,
                    default_retrieval_influence_ablation_path(root),
                )

            artifact_exists = output_path.exists()
            manifest_file_exists = (root / "data" / "cartridges" / "baseline_manifest.json").exists()

        self.assertEqual(run.version, RETRIEVAL_INFLUENCE_ABLATION_VERSION)
        self.assertEqual(run.query_count, 2)
        self.assertEqual(run.deterministic_semantic_model_name, "deterministic_ablation:zero_semantic_vector")
        self.assertIn("baseline_metrics", run.to_dict())
        self.assertIn("deterministic_companion_metrics", run.to_dict())
        self.assertIn("ml_companion_metrics", run.to_dict())
        self.assertTrue(artifact_exists)
        self.assertFalse(manifest_file_exists)
        self.assertGreaterEqual(
            run.deterministic_companion_metrics.doc_hit_at_3,
            run.baseline_metrics.doc_hit_at_3,
        )

    def test_ablation_command_emits_json_and_writes_artifact(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._write_project_docs(root)
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with patch("src.core.coordination.project_query_lens_bag.SentenceTransformer", FakeSentenceTransformer):
                    with contextlib.redirect_stdout(stdout):
                        exit_code = main(["project-query-ablation-compare", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

            artifact_exists = default_retrieval_influence_ablation_path(root).exists()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["version"], RETRIEVAL_INFLUENCE_ABLATION_VERSION)
        self.assertIn("baseline_metrics", payload)
        self.assertIn("deterministic_companion_metrics", payload)
        self.assertIn("ml_companion_metrics", payload)
        self.assertIn("interpretation", payload)
        self.assertGreater(payload["elapsed_ms"], 0)
        self.assertTrue(artifact_exists)


if __name__ == "__main__":
    unittest.main()
