"""Local MCP adapter and raw inspection capture tests."""

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
    PROJECT_QUERY_TOOL_NAME,
    TRAVERSAL_CAPABILITY_NAME,
    TRAVERSAL_TOOL_NAME,
    build_default_registered_tool_call,
    build_default_traversal_inspection,
    build_mcp_tool_registry,
    call_registered_mcp_tool,
    run_traversal_mcp_adapter,
)
from src.core.analysis import enrich_relations, persist_relation_enrichments
from src.core.persistence import SemanticCartridge
from src.core.transformation import SourceDocument, semantic_objects_from_source


class LocalMcpAdapterTests(unittest.TestCase):
    def _cartridge_with_seed(self, temp: str):
        cartridge = SemanticCartridge(Path(temp) / "adapter.sqlite3")
        objects = semantic_objects_from_source(
            SourceDocument(
                source_ref="fixture://adapter",
                content="# Adapter\n\nWalk relation data.\n\nExpose raw JSON.",
            )
        )
        for obj in objects:
            cartridge.upsert_object(obj)
        report = enrich_relations(objects)
        persist_relation_enrichments(cartridge, report)
        return cartridge, objects[1].semantic_id

    def test_traversal_adapter_captures_raw_request_response_and_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, seed = self._cartridge_with_seed(temp)

            capture = run_traversal_mcp_adapter(cartridge, seed, max_depth=1)

        payload = capture.to_dict()
        self.assertEqual(payload["capability"]["name"], TRAVERSAL_CAPABILITY_NAME)
        self.assertEqual(payload["request"]["seed_semantic_id"], seed)
        self.assertIn("traversal_report", payload["response"])
        self.assertGreater(payload["response"]["traversal_report"]["steps"], [])
        self.assertTrue(payload["usefulness_report"]["meets_acceptance"])

    def test_default_traversal_inspection_builds_visible_json_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            capture = build_default_traversal_inspection(Path(temp) / "inspection.sqlite3")

        payload = json.loads(capture.to_json())
        self.assertIn("capture_id", payload)
        self.assertEqual(payload["capability"]["name"], TRAVERSAL_CAPABILITY_NAME)
        self.assertIn("seam_manifest", payload)
        self.assertIn("raw capture intended for builder inspection", payload["notes"])

    def test_mcp_inspect_dump_json_command_returns_payload_without_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stdout = io.StringIO()
            old_root = os.environ.get("NGRAPH_PROJECT_ROOT")
            os.environ["NGRAPH_PROJECT_ROOT"] = temp
            try:
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["mcp-inspect", "--dump-json"])
            finally:
                if old_root is None:
                    os.environ.pop("NGRAPH_PROJECT_ROOT", None)
                else:
                    os.environ["NGRAPH_PROJECT_ROOT"] = old_root

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertGreaterEqual(payload["record_count"], 1)
        call = payload["records"][0]["call"]
        self.assertIn("call_id", call)
        self.assertEqual(call["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertEqual(call["capture"]["capability"]["name"], TRAVERSAL_CAPABILITY_NAME)

    def test_tool_registry_registers_traversal_candidate(self) -> None:
        registry = build_mcp_tool_registry()
        tool = registry.get(TRAVERSAL_TOOL_NAME)

        self.assertEqual(registry.status, "local_registration_candidate")
        self.assertEqual(tool.capability_name, TRAVERSAL_CAPABILITY_NAME)
        self.assertEqual(tool.input_schema["required"], ["db_path", "seed_semantic_id"])
        self.assertEqual(tool.output_schema["required"], ["call_id", "tool", "status", "capture"])

    def test_registered_traversal_tool_calls_adapter_with_serializable_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cartridge, seed = self._cartridge_with_seed(temp)
            result = call_registered_mcp_tool(
                TRAVERSAL_TOOL_NAME,
                {
                    "db_path": str(cartridge.db_path),
                    "seed_semantic_id": seed,
                    "max_depth": 1,
                    "max_steps": 16,
                    "include_incoming": True,
                },
            )

        payload = result.to_dict()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertEqual(payload["capture"]["request"]["seed_semantic_id"], seed)
        self.assertTrue(payload["capture"]["usefulness_report"]["meets_acceptance"])

    def test_default_registered_tool_call_uses_same_inspection_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = build_default_registered_tool_call(Path(temp) / "registered.sqlite3")

        payload = result.to_dict()
        self.assertEqual(payload["tool"]["tool_name"], TRAVERSAL_TOOL_NAME)
        self.assertIn("traversal_report", payload["capture"]["response"])

    def test_mcp_tools_dump_json_command_lists_registry(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(["mcp-tools", "--dump-json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "local_registration_candidate")
        self.assertEqual(payload["tools"][0]["tool_name"], TRAVERSAL_TOOL_NAME)
        tool_names = {tool["tool_name"] for tool in payload["tools"]}
        self.assertIn(PROJECT_QUERY_TOOL_NAME, tool_names)


if __name__ == "__main__":
    unittest.main()
