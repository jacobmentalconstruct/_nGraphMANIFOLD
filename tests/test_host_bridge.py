"""Local host bridge tests."""

from __future__ import annotations

import os
import contextlib
import io
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from src.core.coordination import (
    DEFAULT_HOST_BRIDGE_HEAVY_TIMEOUT_MS,
    DEFAULT_HOST_BRIDGE_MEDIUM_TIMEOUT_MS,
    DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
    HOST_BUILDER_SCORE_TOOL_NAME,
    HOST_COCKPIT_TOOL_NAME,
    HOST_HISTORY_VIEW_TOOL_NAME,
    HOST_PROMOTE_CALL_TOOL_NAME,
    HOST_PROJECTION_SCORE_TOOL_NAME,
    HOST_READ_PANELS_TOOL_NAME,
    HOST_SEED_SEARCH_TOOL_NAME,
    HOST_STATUS_TOOL_NAME,
    HOST_STREAM_TOOL_NAME,
    HOST_TOOLS_TOOL_NAME,
    PROJECT_QUERY_TOOL_NAME,
    HostBridgeError,
    HostBridgeUnavailableError,
    activate_host_bridge_session,
    build_english_lexicon_baseline,
    build_python_docs_corpus,
    cleanup_host_bridge_transport,
    create_host_command_envelope,
    default_host_bridge_supported_tools,
    default_host_state,
    default_host_bridge_root,
    dispatch_command_via_host_bridge,
    enqueue_host_bridge_request,
    ingest_project_documents,
    load_host_bridge_session,
    process_pending_host_bridge_requests,
    resolve_host_bridge_timeout_policy,
    run_host_bridge_maintenance,
    require_live_host_bridge_session,
    wait_for_live_host_bridge_session,
)
from src.app import main


class HostBridgeTests(unittest.TestCase):
    def test_default_supported_tools_cover_host_owned_views(self) -> None:
        supported = set(default_host_bridge_supported_tools())
        self.assertIn(PROJECT_QUERY_TOOL_NAME, supported)
        self.assertIn(HOST_STATUS_TOOL_NAME, supported)
        self.assertIn(HOST_TOOLS_TOOL_NAME, supported)
        self.assertIn(HOST_SEED_SEARCH_TOOL_NAME, supported)
        self.assertIn(HOST_HISTORY_VIEW_TOOL_NAME, supported)
        self.assertIn(HOST_STREAM_TOOL_NAME, supported)
        self.assertIn(HOST_COCKPIT_TOOL_NAME, supported)
        self.assertIn(HOST_BUILDER_SCORE_TOOL_NAME, supported)
        self.assertIn(HOST_PROJECTION_SCORE_TOOL_NAME, supported)
        self.assertIn(HOST_PROMOTE_CALL_TOOL_NAME, supported)
        self.assertIn(HOST_READ_PANELS_TOOL_NAME, supported)

    def test_resolve_host_bridge_timeout_policy_uses_command_defaults_and_override(self) -> None:
        builder_policy = resolve_host_bridge_timeout_policy(HOST_BUILDER_SCORE_TOOL_NAME)
        projection_policy = resolve_host_bridge_timeout_policy(HOST_PROJECTION_SCORE_TOOL_NAME)
        query_policy = resolve_host_bridge_timeout_policy(PROJECT_QUERY_TOOL_NAME)
        override_policy = resolve_host_bridge_timeout_policy(
            HOST_BUILDER_SCORE_TOOL_NAME,
            requested_timeout_ms=42000,
        )

        self.assertEqual(builder_policy["timeout_ms"], DEFAULT_HOST_BRIDGE_HEAVY_TIMEOUT_MS)
        self.assertEqual(builder_policy["timeout_source"], "command_policy_default")
        self.assertEqual(builder_policy["runtime_class"], "heavy")
        self.assertEqual(projection_policy["timeout_ms"], DEFAULT_HOST_BRIDGE_MEDIUM_TIMEOUT_MS)
        self.assertEqual(query_policy["timeout_ms"], DEFAULT_HOST_BRIDGE_TIMEOUT_MS)
        self.assertEqual(query_policy["runtime_class"], "standard")
        self.assertEqual(override_policy["timeout_ms"], 42000)
        self.assertEqual(override_policy["timeout_source"], "caller_override")
        self.assertEqual(builder_policy["global_default_timeout_ms"], DEFAULT_HOST_BRIDGE_TIMEOUT_MS)

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
            "# MCP Seam\n\nShared host bridge.\n",
            encoding="utf-8",
        )
        (root / "_docs" / "STRANGLER_PLAN.md").write_text(
            "# Strangler Plan\n\nProjection flow visibility.\n",
            encoding="utf-8",
        )

    def _build_layers(self, root: Path) -> None:
        self._write_dictionary(root)
        self._write_python_docs(root)
        self._write_project_docs(root)
        build_english_lexicon_baseline(root, reset=True)
        build_python_docs_corpus(root, reset=True)
        ingest_project_documents(root)

    def test_stale_host_bridge_session_is_not_treated_as_live(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            activate_host_bridge_session(root, created_at="2000-01-01T00:00:00Z")

            manifest = load_host_bridge_session(root)

            self.assertIsNone(manifest)
            with self.assertRaises(HostBridgeUnavailableError):
                require_live_host_bridge_session(root)

    def test_wait_for_live_host_bridge_session_observes_startup_manifest(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)

            def worker() -> None:
                time.sleep(0.1)
                activate_host_bridge_session(root)

            thread = threading.Thread(target=worker)
            thread.start()
            manifest = wait_for_live_host_bridge_session(root, timeout_ms=1000, wait_interval_ms=25)
            thread.join(timeout=2.0)

        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.status, "active")

    def test_bridge_request_processing_updates_live_host_state(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            session = activate_host_bridge_session(root)
            request = enqueue_host_bridge_request(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="cli-bridge",
                ),
                session=session,
            )
            responses = process_pending_host_bridge_requests(root, state, session=session)

        self.assertEqual(len(responses), 1)
        response = responses[0]
        self.assertEqual(response.request_id, request.request_id)
        self.assertEqual(response.status, "ok")
        self.assertIsNotNone(state.snapshot)
        self.assertEqual(state.snapshot.active_projection["selected_layer"], "python_docs_projection")
        self.assertIn("project_query", state.snapshot.raw_payload_cache)

    def test_dispatch_command_via_host_bridge_waits_for_live_response(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            self._build_layers(root)
            state = default_host_state(root)
            activate_host_bridge_session(root)

            def worker() -> None:
                time.sleep(0.1)
                process_pending_host_bridge_requests(root, state)

            thread = threading.Thread(target=worker)
            thread.start()
            response = dispatch_command_via_host_bridge(
                root,
                create_host_command_envelope(
                    tool_name=PROJECT_QUERY_TOOL_NAME,
                    payload={"query": "class object function", "limit": 3},
                    actor="human",
                    source_surface="cli-bridge",
                ),
                timeout_ms=2000,
                wait_interval_ms=25,
            )
            thread.join(timeout=2.0)

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.tool_name, PROJECT_QUERY_TOOL_NAME)
        self.assertEqual(response.bridge_policy["timeout_ms"], 2000)
        self.assertEqual(response.bridge_policy["timeout_source"], "caller_override")
        self.assertEqual(
            response.payload["capture"]["command"]["source_surface"],
            "cli-bridge",
        )
        self.assertEqual(
            response.payload["capture"]["response"]["projection_frame"]["selected_layer"],
            "python_docs_projection",
        )

    def test_truly_unsupported_tool_is_rejected_before_bridge_enqueue(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            activate_host_bridge_session(root)

            with self.assertRaises(HostBridgeError):
                enqueue_host_bridge_request(
                    root,
                    create_host_command_envelope(
                        tool_name="ngraph.unsupported.tool",
                        payload={"history_limit": 5},
                        actor="human",
                        source_surface="cli-bridge",
                    ),
                )

    def test_cleanup_host_bridge_transport_removes_stale_files(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            bridge_root = default_host_bridge_root(root)
            session = activate_host_bridge_session(root, created_at="2000-01-01T00:00:00Z")
            request_dir = bridge_root / "requests"
            response_dir = bridge_root / "responses"
            request_dir.mkdir(parents=True, exist_ok=True)
            response_dir.mkdir(parents=True, exist_ok=True)
            request_file = request_dir / "old_request.json"
            response_file = response_dir / "old_response.json"
            request_file.write_text("{}", encoding="utf-8")
            response_file.write_text("{}", encoding="utf-8")
            old_time = time.time() - 3600
            os.utime(request_file, (old_time, old_time))
            os.utime(response_file, (old_time, old_time))

            report = cleanup_host_bridge_transport(root, stale_after_seconds=1.0)

        self.assertEqual(session.status, "active")
        self.assertEqual(report["removed_requests"], 1)
        self.assertEqual(report["removed_responses"], 1)
        self.assertEqual(report["removed_session"], 1)

    def test_bridge_maintenance_reports_before_cleanup_and_after_state(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            bridge_root = default_host_bridge_root(root)
            request_dir = bridge_root / "requests"
            response_dir = bridge_root / "responses"
            request_dir.mkdir(parents=True, exist_ok=True)
            response_dir.mkdir(parents=True, exist_ok=True)
            request_file = request_dir / "old_request.json"
            response_file = response_dir / "old_response.json"
            request_file.write_text("{}", encoding="utf-8")
            response_file.write_text("{}", encoding="utf-8")
            old_time = time.time() - 3600
            os.utime(request_file, (old_time, old_time))
            os.utime(response_file, (old_time, old_time))

            report = run_host_bridge_maintenance(root, stale_after_seconds=1.0)

        payload = report.to_dict()
        self.assertEqual(payload["before"]["pending_request_count"], 1)
        self.assertEqual(payload["before"]["pending_response_count"], 1)
        self.assertEqual(payload["cleanup"]["removed_requests"], 1)
        self.assertEqual(payload["cleanup"]["removed_responses"], 1)
        self.assertEqual(payload["after"]["pending_request_count"], 0)
        self.assertEqual(payload["after"]["pending_response_count"], 0)
        self.assertEqual(payload["removed_total"], 2)

    def test_bridge_maintenance_command_emits_json(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            root = Path(temp)
            bridge_root = default_host_bridge_root(root)
            request_dir = bridge_root / "requests"
            request_dir.mkdir(parents=True, exist_ok=True)
            request_file = request_dir / "old_request.json"
            request_file.write_text("{}", encoding="utf-8")
            old_time = time.time() - 3600
            os.utime(request_file, (old_time, old_time))
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main([
                        "mcp-bridge-maintenance",
                        "--bridge-retention-seconds",
                        "1",
                        "--dump-json",
                    ])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["before"]["pending_request_count"], 1)
        self.assertEqual(payload["after"]["pending_request_count"], 0)
        self.assertEqual(payload["cleanup"]["removed_requests"], 1)


if __name__ == "__main__":
    unittest.main()
