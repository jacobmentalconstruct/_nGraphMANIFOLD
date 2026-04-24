"""Shared host workspace tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.config import AppSettings
from src.core.coordination import (
    HOST_BUILDER_SCORE_TOOL_NAME,
    HOST_COCKPIT_TOOL_NAME,
    HOST_HISTORY_VIEW_TOOL_NAME,
    HOST_PANEL_ORDER,
    HOST_PROJECTION_SCORE_TOOL_NAME,
    HOST_PROMOTE_CALL_TOOL_NAME,
    HOST_READ_PANELS_TOOL_NAME,
    HOST_SEED_SEARCH_TOOL_NAME,
    HOST_STATUS_TOOL_NAME,
    HOST_STREAM_TOOL_NAME,
    HOST_TOOLS_TOOL_NAME,
    PROJECT_QUERY_TOOL_NAME,
    build_english_lexicon_baseline,
    build_host_workspace_snapshot,
    build_python_docs_corpus,
    create_host_command_envelope,
    default_host_state,
    default_mcp_inspection_history_path,
    dispatch_host_command,
    ingest_project_documents,
)


class HostWorkspaceTests(unittest.TestCase):
    def _write_dictionary(self, root: Path) -> None:
        source = root / "assets" / "_corpus_examples" / "dictionary_alpha_arrays.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '[{"object":"A thing presented to the senses or mind.",'
            '"class":"A group ranked together.",'
            '"function":"The act of performing a duty."}]',
            encoding="utf-8",
        )

    def _write_python_docs(self, root: Path) -> None:
        docs = root / "assets" / "_corpus_examples" / "python-3.11.15-docs-text"
        (docs / "library").mkdir(parents=True, exist_ok=True)
        (docs / "reference").mkdir(parents=True, exist_ok=True)
        (docs / "tutorial").mkdir(parents=True, exist_ok=True)
        (docs / "library" / "functions.txt").write_text(
            "Built-in Functions\n******************\n\nissubclass(class, classinfo)\n",
            encoding="utf-8",
        )
        (docs / "reference" / "compound_stmts.txt").write_text(
            "Compound statements\n*******************\n\nClass definitions\n=================\n\n"
            "   class Foo(object):\n       pass\n",
            encoding="utf-8",
        )
        (docs / "reference" / "simple_stmts.txt").write_text(
            "Simple statements\n*****************\n\nreturn_stmt ::= \"return\" [expression_list]\n",
            encoding="utf-8",
        )
        (docs / "tutorial" / "controlflow.txt").write_text(
            "More Control Flow Tools\n***********************\n\n"
            "   >>> for i in range(3):\n   ...     print(i)\n",
            encoding="utf-8",
        )

    def _write_project_docs(self, root: Path) -> None:
        (root / "_docs").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# nGraphMANIFOLD\n\nSemantic substrate.\n", encoding="utf-8")
        (root / "_docs" / "PROJECT_STATUS.md").write_text(
            "# Project Status\n\nCurrent Park Point.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "MCP_SEAM.md").write_text(
            "# MCP Seam\n\nShared host state spine.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nProjection flow visibility.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "TODO.md").write_text(
            "# TODO\n\nKeep interaction envelopes inspection-only.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "EXPERIENTIAL_WORKFLOW.md").write_text(
            "# Experiential Workflow\n\nThe host can report the active panel.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "PROTOTYPE_TUNING.md").write_text(
            "# Prototype Tuning\n\nBuilder and projection scores remain accepted.\n",
            encoding="utf-8",
        )

    def _build_layers(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)

    def test_dispatcher_normalizes_cli_and_ui_project_query(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            history_path = default_mcp_inspection_history_path(root)
            state = default_host_state(root)
            cli_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="cli",
                ),
                state=state,
                history_path=history_path,
            )
            ui_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
                history_path=history_path,
            )

        self.assertEqual(cli_result.command.tool_name, ui_result.command.tool_name)
        self.assertEqual(
            cli_result.payload["capture"]["response"]["projection_frame"]["selected_layer"],
            "python_docs_projection",
        )
        self.assertEqual(
            ui_result.payload["capture"]["response"]["projection_frame"]["selected_layer"],
            "python_docs_projection",
        )

    def test_project_query_updates_host_snapshot_projection_and_cache(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )

        snapshot = result.snapshot
        self.assertIsNotNone(snapshot.active_projection)
        self.assertEqual(snapshot.active_projection["selected_layer"], "python_docs_projection")
        self.assertIsNotNone(snapshot.active_projection["selected_flow"])
        self.assertGreaterEqual(len(snapshot.stream_items), 1)
        self.assertIn("project_query", snapshot.raw_payload_cache)
        self.assertIn("active_interaction", snapshot.raw_payload_cache)
        self.assertIn("rolling_trace_limit", snapshot.retention)

    def test_seed_search_updates_host_snapshot_seed_flow(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_SEED_SEARCH_TOOL_NAME,
                    payload={"query": "Current Park Point", "seed_limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )

        snapshot = result.snapshot
        self.assertIsNotNone(snapshot.active_seed)
        self.assertIsNotNone(snapshot.active_seed["selected_flow"])
        self.assertIn("traversal_report", snapshot.active_seed)
        self.assertIn("seed_search", snapshot.raw_payload_cache)

    def test_workspace_snapshot_assembles_stream_projection_seed_scores_and_raw(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_SEED_SEARCH_TOOL_NAME,
                    payload={"query": "Current Park Point", "seed_limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_HISTORY_VIEW_TOOL_NAME,
                    payload={"history_limit": 6},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            snapshot = build_host_workspace_snapshot(
                root,
                history_path=default_mcp_inspection_history_path(root),
                raw_payload_cache=state.raw_payload_cache,
                active_call_id=state.active_call_id,
                active_tool_name=state.active_tool_name,
            )

        self.assertGreaterEqual(len(snapshot.stream_items), 1)
        self.assertIsNotNone(snapshot.active_projection)
        self.assertIsNotNone(snapshot.active_seed)
        self.assertIn("history", snapshot.raw)
        self.assertIn("stream", snapshot.raw)
        self.assertIn("cockpit", snapshot.raw)
        self.assertIn("retention_policy", snapshot.raw)
        self.assertEqual(snapshot.active_tab, "stream")
        self.assertEqual(tuple(snapshot.panels.keys()), HOST_PANEL_ORDER)

    def test_stream_and_cockpit_dispatch_accept_filters(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            stream_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_STREAM_TOOL_NAME,
                    payload={
                        "history_limit": 6,
                        "tool_filter": "ngraph.project.query",
                        "layer_filter": "python_docs_projection",
                    },
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            cockpit_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_COCKPIT_TOOL_NAME,
                    payload={
                        "history_limit": 6,
                        "tool_filter": "ngraph.project.query",
                        "layer_filter": "python_docs_projection",
                    },
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )

        self.assertEqual(stream_result.payload["raw"]["filters"]["tool"], "ngraph.project.query")
        self.assertEqual(stream_result.payload["raw"]["filters"]["layer"], "python_docs_projection")
        self.assertEqual(cockpit_result.payload["raw"]["filters"]["tool"], "ngraph.project.query")

    def test_status_tools_and_score_dispatches_update_host_state(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            status_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_STATUS_TOOL_NAME,
                    payload={},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            tools_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_TOOLS_TOOL_NAME,
                    payload={},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            builder_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_BUILDER_SCORE_TOOL_NAME,
                    payload={"history_limit": 6},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            projection_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_PROJECTION_SCORE_TOOL_NAME,
                    payload={"history_limit": 6},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )

        self.assertEqual(status_result.payload["active_tranche"], "Post-Prototype Hardening And Expansion")
        self.assertEqual(
            status_result.payload["interaction_truth_policy"]["persistence_policy"],
            "inspection_only",
        )
        self.assertEqual(
            status_result.payload["bridge_timeout_policy"]["global_default_timeout_ms"],
            5000,
        )
        self.assertEqual(
            status_result.payload["bridge_timeout_policy"]["tool_policies"][HOST_BUILDER_SCORE_TOOL_NAME]["runtime_class"],
            "heavy",
        )
        self.assertIn("tools", tools_result.payload)
        self.assertTrue(builder_result.payload["meets_acceptance"])
        self.assertIn("meets_acceptance", projection_result.payload)
        self.assertIn("scores", projection_result.payload)
        self.assertIn("status", projection_result.snapshot.panels)
        self.assertIn("tools", projection_result.snapshot.panels)
        self.assertIn("builder_score", projection_result.snapshot.raw_payload_cache)
        self.assertIn("projection_score", projection_result.snapshot.raw_payload_cache)

    def test_read_panels_dispatch_returns_active_named_and_all_views(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            state.set_active_tab("projection")
            active_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_READ_PANELS_TOOL_NAME,
                    payload={"mode": "active"},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            named_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_READ_PANELS_TOOL_NAME,
                    payload={"mode": "panel", "panel_name": "scores"},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            all_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_READ_PANELS_TOOL_NAME,
                    payload={"mode": "all"},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )

        self.assertEqual(active_result.payload["mode"], "active")
        self.assertEqual(active_result.payload["active_tab"], "projection")
        self.assertEqual(active_result.payload["panel"]["name"], "projection")
        self.assertIn("Active Projection", active_result.payload["panel"]["text"])
        self.assertEqual(named_result.payload["panel"]["name"], "scores")
        self.assertIn("Score Summaries", named_result.payload["panel"]["text"])
        self.assertEqual(tuple(all_result.payload["panels"].keys()), HOST_PANEL_ORDER)
        self.assertIn("panel_read", all_result.snapshot.raw_payload_cache)

    def test_promote_call_dispatch_updates_active_record_and_payload(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            query_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )
            call_id = str(query_result.payload["call_id"])

            promote_result = dispatch_host_command(
                root,
                create_host_command_envelope(
                    tool_name=HOST_PROMOTE_CALL_TOOL_NAME,
                    payload={
                        "call_id": call_id,
                        "pinned": True,
                        "label": "keeper",
                        "reason": "checkpoint",
                        "note": "Preserve this query result.",
                    },
                    actor="human",
                    source_surface="ui",
                ),
                state=state,
            )

        self.assertEqual(promote_result.payload["call_id"], call_id)
        self.assertTrue(promote_result.payload["record"]["pinned"])
        self.assertEqual(promote_result.payload["record"]["operator_metadata"]["label"], "keeper")
        self.assertEqual(promote_result.payload["record"]["operator_metadata"]["reason"], "checkpoint")
        self.assertEqual(promote_result.payload["record"]["operator_metadata"]["note"], "Preserve this query result.")
        self.assertEqual(promote_result.snapshot.active_interaction["call_id"], call_id)
        self.assertIn("promotion", promote_result.snapshot.raw_payload_cache)
        self.assertEqual(promote_result.snapshot.recent_calls[0].operator_label, "keeper")
        self.assertIn("operator=keeper/checkpoint", promote_result.snapshot.panels["history"]["text"])


if __name__ == "__main__":
    unittest.main()
