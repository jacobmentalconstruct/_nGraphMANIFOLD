"""History-aware MCP inspector tests."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.app import main
from src.core.coordination import (
    DEFAULT_MCP_ROLLING_TRACE_LIMIT,
    McpInspectionHistoryStore,
    build_default_registered_tool_call,
    build_history_aware_inspector_payload,
    build_interaction_stream_payload,
    build_visibility_cockpit_payload,
    default_builder_task_score_path,
    default_context_projection_score_path,
    promote_history_call,
    prune_default_history_trace,
)
from src.ui.mcp_inspector import _summary_text


class HistoryAwareInspectorTests(unittest.TestCase):
    def test_history_aware_payload_summarizes_recent_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            result = build_default_registered_tool_call(root / "tool.sqlite3")
            McpInspectionHistoryStore(history_path).record_call(result.to_dict())

            payload = build_history_aware_inspector_payload(
                root,
                history_path=history_path,
                limit=5,
            )

        self.assertEqual(payload.record_count, 1)
        self.assertEqual(len(payload.calls), 1)
        self.assertGreater(payload.calls[0].step_count, 0)
        self.assertIn("Recent calls", payload.to_summary_text())
        self.assertIn("raw", payload.to_dict())
        self.assertIn("rolling trace:", payload.to_summary_text())

    def test_history_aware_payload_maps_score_artifact_task_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            result = build_default_registered_tool_call(root / "tool.sqlite3")
            call = result.to_dict()
            McpInspectionHistoryStore(history_path).record_call(call)
            score_path = default_builder_task_score_path(root)
            score_path.parent.mkdir(parents=True, exist_ok=True)
            score_path.write_text(
                json.dumps(
                    {
                        "meets_acceptance": True,
                        "usefulness_report": {"aggregate_score": 0.93},
                        "scores": [
                            {
                                "call_id": call["call_id"],
                                "fixture": {"task_id": "current_tranche_lookup"},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = build_history_aware_inspector_payload(
                root,
                history_path=history_path,
            )

        self.assertEqual(payload.calls[0].task_id, "current_tranche_lookup")
        self.assertIn("latest builder score: 0.93", payload.to_summary_text())

    def test_mcp_history_view_dump_json_emits_summary_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["mcp-inspect", "--dump-json"])
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-history-view", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertIn("summary_text", payload)
        self.assertIn("calls", payload)
        self.assertIn("raw", payload)

    def test_seed_search_payload_summary_shows_flow_and_breakdown(self) -> None:
        payload = {
            "search": {
                "query": "Current Park Point",
                "candidate_count": 2,
                "selected_seed": {
                    "source_ref": "_docs/PROJECT_STATUS.md",
                    "kind": "heading",
                    "score": 21.19,
                    "matched_terms": ["current", "park", "point"],
                    "heading_trail": ["Current Park Point"],
                    "score_breakdown": {
                        "exact_content": 5.0,
                        "document_role_fit": 3.0,
                    },
                },
                "selected_flow": {
                    "breadcrumb": ["_docs/PROJECT_STATUS.md", "Current Park Point", "block 2"],
                    "objects": [
                        {
                            "role": "previous",
                            "block_index": 1,
                            "kind": "heading",
                            "heading_trail": [],
                            "content_preview": "Project Status",
                        },
                        {
                            "role": "selected",
                            "block_index": 2,
                            "kind": "heading",
                            "heading_trail": ["Current Park Point"],
                            "content_preview": "Current Park Point",
                        },
                    ],
                },
            },
            "tool_call": {
                "tool": {"tool_name": "ngraph.analysis.traverse_cartridge"},
                "capture": {"response": {"traversal_report": {"steps": [1, 2], "blockers": []}}},
            },
        }

        summary = _summary_text(payload)

        self.assertIn("nGraphMANIFOLD Seed Flow", summary)
        self.assertIn("Score Breakdown", summary)
        self.assertIn("document_role_fit: 3.0", summary)
        self.assertIn(">> selected block 2", summary)

    def test_interaction_stream_payload_shows_query_response_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            call = {
                "call_id": "interaction:v1:test",
                "tool": {
                    "tool_name": "ngraph.project.query",
                    "capability_name": "coordination.project_context_query",
                },
                "status": "ok",
                "capture": {
                    "captured_at": "2026-04-23T03:30:00Z",
                    "command": {
                        "payload": {"query": "class object function"},
                    },
                    "response": {
                        "projection_frame": {
                            "selected_layer": "python_docs_projection",
                            "selected_candidate": {
                                "kind": "python_code_example",
                                "score": 17.78,
                                "source_ref": "reference/compound_stmts.txt",
                                "content_preview": "class Foo(object): pass",
                            },
                            "selected_flow": {
                                "objects": [
                                    {
                                        "role": "selected",
                                        "rank": 1,
                                        "kind": "python_code_example",
                                        "score": 17.78,
                                        "content_preview": "class Foo(object): pass",
                                    },
                                    {
                                        "role": "alternative",
                                        "rank": 2,
                                        "kind": "python_api_signature",
                                        "score": 10.5,
                                        "content_preview": "issubclass(class, classinfo)",
                                    },
                                ]
                            },
                        }
                    },
                    "usefulness_report": {"aggregate_score": 0.95},
                },
            }
            McpInspectionHistoryStore(history_path).record_call(call)

            payload = build_interaction_stream_payload(root, history_path=history_path)

        self.assertEqual(len(payload.items), 1)
        self.assertEqual(payload.items[0].query, "class object function")
        self.assertIn("python_docs_projection", payload.items[0].response)
        self.assertEqual(len(payload.items[0].projection_flow), 2)
        self.assertIn("Q: class object function", payload.to_stream_text())
        self.assertIn("R: python_docs_projection", payload.to_stream_text())

    def test_interaction_stream_payload_applies_tool_and_layer_filters(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            query_call = {
                "call_id": "interaction:v1:query",
                "tool": {
                    "tool_name": "ngraph.project.query",
                    "capability_name": "coordination.project_context_query",
                },
                "status": "ok",
                "capture": {
                    "captured_at": "2026-04-23T03:30:00Z",
                    "command": {"payload": {"query": "class object function"}},
                    "response": {"projection_frame": {"selected_layer": "python_docs_projection", "selected_candidate": {}}},
                    "usefulness_report": {"aggregate_score": 0.95},
                },
            }
            traversal_call = {
                "call_id": "interaction:v1:traverse",
                "tool": {
                    "tool_name": "ngraph.analysis.traverse_cartridge",
                    "capability_name": "analysis.traverse_cartridge",
                },
                "status": "ok",
                "capture": {
                    "captured_at": "2026-04-23T03:31:00Z",
                    "request": {"seed_semantic_id": "sem:v1:test"},
                    "response": {"traversal_report": {"steps": [1], "blockers": []}},
                    "usefulness_report": {"aggregate_score": 0.91},
                },
            }
            store = McpInspectionHistoryStore(history_path)
            store.record_call(query_call)
            store.record_call(traversal_call)

            payload = build_interaction_stream_payload(
                root,
                history_path=history_path,
                tool_filter="ngraph.project.query",
                layer_filter="python_docs_projection",
            )

        self.assertEqual(len(payload.items), 1)
        self.assertEqual(payload.items[0].tool_name, "ngraph.project.query")
        self.assertEqual(payload.raw["filters"]["tool"], "ngraph.project.query")
        self.assertEqual(payload.raw["filters"]["layer"], "python_docs_projection")

    def test_mcp_stream_dump_json_emits_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["mcp-inspect", "--dump-json"])
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-stream", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertIn("items", payload)
        self.assertGreaterEqual(len(payload["items"]), 1)

    def test_project_query_payload_summary_shows_projection_flow(self) -> None:
        payload = {
            "capture": {
                "command": {"payload": {"query": "class object function"}},
                "response": {
                    "projection_frame": {
                        "selected_layer": "python_docs_projection",
                        "context_stack": [
                            "english_lexical_prior",
                            "python_docs_projection",
                            "project_local_docs",
                        ],
                        "selected_candidate": {
                            "kind": "python_code_example",
                            "score": 17.78,
                            "source_ref": "reference/compound_stmts.txt",
                            "matched_terms": ["class", "object"],
                            "evidence": ["python_example", "python_context_fit"],
                            "heading_trail": ["Class definitions"],
                        },
                        "selected_flow": {
                            "breadcrumb": ["python_docs_projection", "Class definitions", "rank 1"],
                            "objects": [
                                {
                                    "role": "selected",
                                    "rank": 1,
                                    "kind": "python_code_example",
                                    "score": 17.78,
                                    "content_preview": "class Foo(object): pass",
                                },
                                {
                                    "role": "alternative",
                                    "rank": 2,
                                    "kind": "python_api_signature",
                                    "score": 10.5,
                                    "content_preview": "issubclass(class, classinfo)",
                                },
                            ],
                        },
                        "projections": [
                            {"layer": {"name": "english_lexical_prior"}, "layer_score": 10.0, "candidate_count": 5},
                            {"layer": {"name": "python_docs_projection"}, "layer_score": 20.0, "candidate_count": 8},
                        ],
                    }
                },
            }
        }

        summary = _summary_text(payload)

        self.assertIn("nGraphMANIFOLD Projection Flow", summary)
        self.assertIn("selected_layer: python_docs_projection", summary)
        self.assertIn("Projection Flow:", summary)
        self.assertIn("alternative rank 2", summary)

    def test_visibility_cockpit_payload_combines_scores_and_latest_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            call = {
                "call_id": "interaction:v1:test",
                "tool": {
                    "tool_name": "ngraph.project.query",
                    "capability_name": "coordination.project_context_query",
                },
                "status": "ok",
                "capture": {
                    "captured_at": "2026-04-23T04:00:00Z",
                    "command": {"payload": {"query": "class object function"}},
                    "response": {
                        "projection_frame": {
                            "selected_layer": "python_docs_projection",
                            "selected_candidate": {
                                "kind": "python_code_example",
                                "score": 17.78,
                                "source_ref": "reference/compound_stmts.txt",
                                "content_preview": "class Foo(object): pass",
                            },
                            "selected_flow": {
                                "objects": [
                                    {
                                        "role": "selected",
                                        "rank": 1,
                                        "kind": "python_code_example",
                                        "score": 17.78,
                                        "content_preview": "class Foo(object): pass",
                                    }
                                ]
                            },
                            "projections": [
                                {
                                    "layer": {"name": "python_docs_projection"},
                                    "layer_score": 20.0,
                                    "candidate_count": 8,
                                }
                            ],
                        }
                    },
                    "usefulness_report": {"aggregate_score": 0.95},
                    "result": {"evidence_summary": {"selected_layer": "python_docs_projection", "candidate_count": 8}},
                },
            }
            McpInspectionHistoryStore(history_path).record_call(call)
            builder_score_path = default_builder_task_score_path(root)
            builder_score_path.parent.mkdir(parents=True, exist_ok=True)
            builder_score_path.write_text(
                json.dumps(
                    {
                        "meets_acceptance": True,
                        "usefulness_report": {"aggregate_score": 0.93},
                        "scores": [
                            {
                                "fixture": {"task_id": "current_tranche_lookup", "question": "current tranche"},
                                "seed_semantic_id": "sem:v1:missing",
                                "seed_source_ref": "_docs/PROJECT_STATUS.md",
                                "traversal_step_count": 7,
                                "blocker_count": 0,
                                "call_id": "mcptoolcall:v1:seed",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            projection_score_path = default_context_projection_score_path(root)
            projection_score_path.parent.mkdir(parents=True, exist_ok=True)
            projection_score_path.write_text(
                json.dumps(
                    {
                        "meets_acceptance": True,
                        "usefulness_report": {"aggregate_score": 0.96},
                    }
                ),
                encoding="utf-8",
            )

            payload = build_visibility_cockpit_payload(root, history_path=history_path)

        self.assertEqual(payload.latest_projection["selected_layer"], "python_docs_projection")
        self.assertEqual(payload.latest_builder_score["usefulness_report"]["aggregate_score"], 0.93)
        self.assertEqual(payload.latest_projection_score["usefulness_report"]["aggregate_score"], 0.96)
        self.assertEqual(len(payload.stream.items), 1)
        self.assertEqual(
            payload.raw["history_snapshot"]["retention"]["rolling_trace_limit"],
            DEFAULT_MCP_ROLLING_TRACE_LIMIT,
        )

    def test_visibility_cockpit_payload_applies_filters(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            call = {
                "call_id": "interaction:v1:test",
                "tool": {
                    "tool_name": "ngraph.project.query",
                    "capability_name": "coordination.project_context_query",
                },
                "status": "ok",
                "capture": {
                    "captured_at": "2026-04-23T04:00:00Z",
                    "command": {"payload": {"query": "class object function"}},
                    "response": {"projection_frame": {"selected_layer": "python_docs_projection", "selected_candidate": {}, "selected_flow": {"objects": []}, "projections": []}},
                    "usefulness_report": {"aggregate_score": 0.95},
                    "result": {"evidence_summary": {"selected_layer": "python_docs_projection", "candidate_count": 1}},
                },
            }
            McpInspectionHistoryStore(history_path).record_call(call)

            payload = build_visibility_cockpit_payload(
                root,
                history_path=history_path,
                tool_filter="ngraph.project.query",
                layer_filter="python_docs_projection",
            )

        self.assertEqual(len(payload.stream.items), 1)
        self.assertEqual(payload.latest_projection["selected_layer"], "python_docs_projection")
        self.assertEqual(payload.raw["filters"]["tool"], "ngraph.project.query")

    def test_mcp_cockpit_dump_json_emits_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["mcp-inspect", "--dump-json"])
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-cockpit", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertIn("stream", payload)
        self.assertIn("latest_projection", payload)

    def test_prune_default_history_trace_keeps_pinned_records_and_recent_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            builder_score_path = default_builder_task_score_path(root)
            builder_score_path.parent.mkdir(parents=True, exist_ok=True)
            call_ids: list[str] = []
            store = McpInspectionHistoryStore(history_path)
            for index in range(5):
                call = {
                    "call_id": f"call-{index}",
                    "tool": {
                        "tool_name": "ngraph.project.query",
                        "capability_name": "coordination.project_context_query",
                    },
                    "status": "ok",
                    "capture": {
                        "captured_at": f"2026-04-23T04:00:0{index}Z",
                        "command": {"payload": {"query": f"query {index}"}},
                        "response": {"projection_frame": {}},
                        "usefulness_report": {"aggregate_score": 0.9},
                    },
                }
                store.record_call(call)
                call_ids.append(call["call_id"])
            builder_score_path.write_text(
                json.dumps(
                    {
                        "meets_acceptance": True,
                        "usefulness_report": {"aggregate_score": 0.93},
                        "scores": [{"call_id": call_ids[0], "fixture": {"task_id": "keep_oldest"}}],
                    }
                ),
                encoding="utf-8",
            )

            report = prune_default_history_trace(root, history_path, rolling_trace_limit=2)
            snapshot = store.snapshot(limit=10, rolling_trace_limit=2)
            remaining_ids = [record.call_id for record in snapshot.records]

        self.assertEqual(report["pruned_count"], 2)
        self.assertIn(call_ids[0], remaining_ids)
        self.assertEqual(snapshot.retention.rolling_trace_limit, 2)
        self.assertEqual(snapshot.retention.active_reasoning_count, 2)
        self.assertEqual(snapshot.retention.durable_evidence_count, 1)

    def test_promote_history_call_defaults_to_latest_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            store = McpInspectionHistoryStore(history_path)
            for index in range(2):
                store.record_call(
                    {
                        "call_id": f"call-{index}",
                        "tool": {
                            "tool_name": "ngraph.project.query",
                            "capability_name": "coordination.project_context_query",
                        },
                        "status": "ok",
                        "capture": {
                            "captured_at": f"2026-04-23T04:00:0{index}Z",
                            "command": {"payload": {"query": f"query {index}"}},
                            "response": {"projection_frame": {}},
                            "usefulness_report": {"aggregate_score": 0.9},
                        },
                    }
                )

            payload = promote_history_call(root, history_path)

        self.assertEqual(payload["call_id"], "call-1")
        self.assertTrue(payload["record"]["pinned"])

    def test_promote_history_call_persists_operator_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            store = McpInspectionHistoryStore(history_path)
            store.record_call(
                {
                    "call_id": "call-meta",
                    "tool": {
                        "tool_name": "ngraph.project.query",
                        "capability_name": "coordination.project_context_query",
                    },
                    "status": "ok",
                    "capture": {
                        "captured_at": "2026-04-23T04:00:00Z",
                        "command": {"payload": {"query": "query"}},
                        "response": {"projection_frame": {}},
                        "usefulness_report": {"aggregate_score": 0.9},
                    },
                }
            )

            payload = promote_history_call(
                root,
                history_path,
                call_id="call-meta",
                label="keeper",
                reason="milestone",
                note="use this later",
            )
            history_payload = build_history_aware_inspector_payload(root, history_path=history_path)
            stream_payload = build_interaction_stream_payload(root, history_path=history_path)

        self.assertEqual(payload["record"]["operator_metadata"]["label"], "keeper")
        self.assertEqual(payload["record"]["operator_metadata"]["reason"], "milestone")
        self.assertEqual(payload["record"]["operator_metadata"]["note"], "use this later")
        self.assertEqual(history_payload.calls[0].operator_label, "keeper")
        self.assertEqual(history_payload.calls[0].operator_reason, "milestone")
        self.assertIn("operator=keeper/milestone", history_payload.to_summary_text())
        self.assertEqual(stream_payload.items[0].operator_note, "use this later")
        self.assertIn("operator=keeper / milestone", stream_payload.to_stream_text())
        self.assertIn("note=use this later", stream_payload.to_stream_text())

    def test_promote_history_call_refuses_to_demote_score_locked_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            history_path = root / "history.sqlite3"
            builder_score_path = default_builder_task_score_path(root)
            builder_score_path.parent.mkdir(parents=True, exist_ok=True)
            store = McpInspectionHistoryStore(history_path)
            store.record_call(
                {
                    "call_id": "locked-call",
                    "tool": {
                        "tool_name": "ngraph.project.query",
                        "capability_name": "coordination.project_context_query",
                    },
                    "status": "ok",
                    "capture": {
                        "captured_at": "2026-04-23T04:00:00Z",
                        "command": {"payload": {"query": "query"}},
                        "response": {"projection_frame": {}},
                        "usefulness_report": {"aggregate_score": 0.9},
                    },
                }
            )
            builder_score_path.write_text(
                json.dumps(
                    {
                        "meets_acceptance": True,
                        "usefulness_report": {"aggregate_score": 0.93},
                        "scores": [{"call_id": "locked-call", "fixture": {"task_id": "locked"}}],
                    }
                ),
                encoding="utf-8",
            )
            promote_history_call(root, history_path, call_id="locked-call", pinned=True)

            with self.assertRaises(ValueError):
                promote_history_call(root, history_path, call_id="locked-call", pinned=False)

    def test_mcp_promote_call_dump_json_emits_promotion_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            history_path = Path(temp) / "data" / "mcp_inspection" / "history.sqlite3"
            McpInspectionHistoryStore(history_path).record_call(
                {
                    "call_id": "call-promote",
                    "tool": {
                        "tool_name": "ngraph.project.query",
                        "capability_name": "coordination.project_context_query",
                    },
                    "status": "ok",
                    "capture": {
                        "captured_at": "2026-04-23T04:00:00Z",
                        "command": {"payload": {"query": "query"}},
                        "response": {"projection_frame": {}},
                        "usefulness_report": {"aggregate_score": 0.9},
                    },
                }
            )
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-promote-call", "--dump-json", "--call-id", "call-promote"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["call_id"], "call-promote")
        self.assertTrue(payload["record"]["pinned"])

    def test_mcp_promote_call_dump_json_emits_operator_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            history_path = Path(temp) / "data" / "mcp_inspection" / "history.sqlite3"
            McpInspectionHistoryStore(history_path).record_call(
                {
                    "call_id": "call-meta",
                    "tool": {
                        "tool_name": "ngraph.project.query",
                        "capability_name": "coordination.project_context_query",
                    },
                    "status": "ok",
                    "capture": {
                        "captured_at": "2026-04-23T04:00:00Z",
                        "command": {"payload": {"query": "query"}},
                        "response": {"projection_frame": {}},
                        "usefulness_report": {"aggregate_score": 0.9},
                    },
                }
            )
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "mcp-promote-call",
                            "--dump-json",
                            "--call-id",
                            "call-meta",
                            "--label",
                            "keeper",
                            "--reason",
                            "reviewed",
                            "--note",
                            "keep this handy",
                        ]
                    )
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["record"]["operator_metadata"]["label"], "keeper")
        self.assertEqual(payload["record"]["operator_metadata"]["reason"], "reviewed")
        self.assertEqual(payload["record"]["operator_metadata"]["note"], "keep this handy")


if __name__ == "__main__":
    unittest.main()
