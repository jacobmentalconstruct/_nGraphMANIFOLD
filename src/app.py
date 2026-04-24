"""Application composition root for nGraphMANIFOLD."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from .core.config import AppSettings
from .core.coordination import (
    DEFAULT_HOST_BRIDGE_ATTACH_GRACE_MS,
    DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
    HOST_BUILDER_SCORE_TOOL_NAME,
    HOST_COCKPIT_TOOL_NAME,
    HOST_HISTORY_VIEW_TOOL_NAME,
    HOST_PROJECTION_SCORE_TOOL_NAME,
    HOST_READ_PANELS_TOOL_NAME,
    HOST_PROMOTE_CALL_TOOL_NAME,
    HOST_SEED_SEARCH_TOOL_NAME,
    HOST_STATUS_TOOL_NAME,
    HOST_STREAM_TOOL_NAME,
    HOST_TOOLS_TOOL_NAME,
    HostBridgeError,
    HostBridgeUnavailableError,
    PROJECT_QUERY_TOOL_NAME,
    TRAVERSAL_TOOL_NAME,
    DEFAULT_PYTHON_DOCS_DOCUMENTS,
    McpInspectionHistoryStore,
    build_english_lexicon_baseline,
    build_default_registered_tool_call,
    create_host_command_envelope,
    build_history_aware_inspector_payload,
    build_interaction_stream_payload,
    build_visibility_cockpit_payload,
    build_python_docs_corpus,
    build_mcp_tool_registry,
    default_builder_task_score_path,
    default_context_projection_score_path,
    default_mcp_inspection_history_path,
    resolve_project_document_profile,
    prune_default_history_trace,
    dispatch_command_via_host_bridge,
    dispatch_host_command,
    ingest_project_documents_for_traversal,
    load_host_bridge_session,
    lookup_english_lexicon_entry,
    run_context_projection_arbitration_scoring,
    run_real_builder_task_scoring,
    resolve_host_bridge_timeout_policy,
    run_seed_search_traversal,
    wait_for_live_host_bridge_session,
)
from .core.engine import ApplicationEngine
from .core.logging import configure_logging
from .ui.gui_main import launch_ui
from .ui.mcp_inspector import (
    launch_interaction_stream,
    launch_mcp_inspector,
    launch_visibility_cockpit,
)

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser owned by the composition root."""
    parser = argparse.ArgumentParser(
        prog="nGraphMANIFOLD",
        description="Semantic operating substrate scaffold.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=(
            "status",
            "ui",
            "mcp-inspect",
            "mcp-tools",
            "mcp-history",
            "mcp-ingest-docs",
            "mcp-score-tasks",
            "mcp-history-view",
            "mcp-cockpit",
            "mcp-stream",
            "mcp-search-seeds",
            "mcp-promote-call",
            "mcp-read-panels",
            "ingest-python-docs",
            "ingest-lexicon",
            "lookup-lexicon",
            "project-query",
            "project-query-score",
        ),
        help="Command to run.",
    )
    parser.add_argument(
        "--dump-json",
        action="store_true",
        help="For inspection commands, write raw JSON to stdout instead of opening a panel or logging.",
    )
    parser.add_argument(
        "--detached-window",
        action="store_true",
        help="For visible inspection commands, force a separate popup window instead of updating the live host workspace when one is available.",
    )
    parser.add_argument(
        "--use-host-bridge",
        action="store_true",
        help="For bridge-enabled commands, target the already-open host workspace instead of running locally.",
    )
    parser.add_argument(
        "--bridge-timeout-ms",
        type=int,
        default=None,
        help=(
            "When using --use-host-bridge, optional override for how long to wait. "
            f"If omitted, the bridge uses a command-aware default (global default {DEFAULT_HOST_BRIDGE_TIMEOUT_MS} ms)."
        ),
    )
    parser.add_argument(
        "--history-limit",
        type=int,
        default=10,
        help="For mcp-history, number of recent inspection records to return.",
    )
    parser.add_argument(
        "--query",
        default="Current Park Point",
        help="For search and projection commands, text query used to rank candidates.",
    )
    parser.add_argument(
        "--seed-limit",
        type=int,
        default=5,
        help="For mcp-search-seeds, number of ranked seed candidates to include.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="For ingest-lexicon or ingest-python-docs, optional maximum number of entries to ingest.",
    )
    parser.add_argument(
        "--tool-filter",
        default="",
        help="For mcp-stream or mcp-cockpit, optional exact tool name filter.",
    )
    parser.add_argument(
        "--layer-filter",
        default="",
        help="For mcp-stream or mcp-cockpit, optional exact selected-layer filter.",
    )
    parser.add_argument(
        "--call-id",
        default="",
        help="For mcp-promote-call, optional explicit call id. Defaults to the latest history record.",
    )
    parser.add_argument(
        "--panel-mode",
        choices=("active", "panel", "all"),
        default="active",
        help="For mcp-read-panels, whether to read the active panel, one named panel, or all panels.",
    )
    parser.add_argument(
        "--panel-name",
        default="",
        help="For mcp-read-panels --panel-mode panel, the named host panel to read.",
    )
    parser.add_argument(
        "--project-doc-profile",
        choices=("core", "expanded"),
        default="core",
        help="For project-doc ingestion and builder-facing scoring/search, choose a bounded document profile.",
    )
    parser.add_argument(
        "--demote",
        action="store_true",
        help="For mcp-promote-call, clear an operator pin instead of setting it.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="For ingest-lexicon or ingest-python-docs, rebuild the cartridge from an empty database.",
    )
    parser.add_argument(
        "--include-prose",
        action="store_true",
        help="For ingest-python-docs, include broad prose descriptions in addition to projection anchors.",
    )
    parser.add_argument(
        "--all-python-docs",
        action="store_true",
        help="For ingest-python-docs, scan the full Python docs tree instead of the bounded projection set.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the application command and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.verbose)
    settings = AppSettings.from_environment()
    engine = ApplicationEngine(settings)

    def _host_session_for_visible_command(command_name: str):
        if args.dump_json or args.detached_window:
            return None
        try:
            session = wait_for_live_host_bridge_session(
                settings.project_root,
                timeout_ms=DEFAULT_HOST_BRIDGE_ATTACH_GRACE_MS,
            )
        except Exception:
            return None
        if session is None:
            return None
        if command_name not in set(session.supported_tools):
            return None
        return session

    def _run_bridge_enabled_host_command(command_name: str, payload: dict[str, object]) -> tuple[int, str, bool]:
        live_session = None if args.use_host_bridge else _host_session_for_visible_command(command_name)
        deliver_to_host = bool(args.use_host_bridge or live_session is not None)
        command = create_host_command_envelope(
            tool_name=command_name,
            payload=payload,
            actor="human",
            source_surface="cli-bridge" if deliver_to_host else "cli",
        )
        if deliver_to_host:
            bridge_policy = resolve_host_bridge_timeout_policy(
                command_name,
                requested_timeout_ms=args.bridge_timeout_ms,
            )
            try:
                response = dispatch_command_via_host_bridge(
                    settings.project_root,
                    command,
                    timeout_ms=args.bridge_timeout_ms,
                )
            except HostBridgeUnavailableError as exc:
                LOGGER.error("Host bridge unavailable: %s", exc)
                return 1, json.dumps({"error": str(exc)}, indent=2, sort_keys=True), True
            except HostBridgeError as exc:
                LOGGER.error("Host bridge failed: %s", exc)
                return 1, json.dumps({"error": str(exc)}, indent=2, sort_keys=True), True
            rendered_payload = dict(response.payload or {})
            rendered_payload["_bridge"] = {
                "request_id": response.request_id,
                "session_id": response.session_id,
                "status": response.status,
                "responded_at": response.responded_at,
                "policy": response.bridge_policy or bridge_policy,
                "snapshot_summary": response.snapshot_summary,
            }
            rendered = json.dumps(rendered_payload, indent=2, sort_keys=True)
            return 0, rendered, True
        result = dispatch_host_command(
            settings.project_root,
            command,
            history_limit=args.history_limit,
        )
        return 0, result.rendered_json, False

    if args.command == "status":
        exit_code, rendered, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_STATUS_TOOL_NAME,
            {},
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{rendered}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Status view delivered to the live host workspace.")
            return 0
        status = json.loads(rendered)
        LOGGER.info("nGraphMANIFOLD status: %s", status.get("status", "n/a"))
        LOGGER.info("project_root=%s", status.get("project_root", "n/a"))
        LOGGER.info("active_tranche=%s", status.get("active_tranche", "n/a"))
        LOGGER.info("next_tranche=%s", status.get("next_tranche", "n/a"))
        return 0

    if args.command == "ui":
        return launch_ui(settings)

    if args.command == "mcp-inspect":
        with tempfile.TemporaryDirectory() as temp:
            result = build_default_registered_tool_call(Path(temp) / "mcp_inspection.sqlite3")
        history = McpInspectionHistoryStore(default_mcp_inspection_history_path(settings.project_root))
        history.record_call(result.to_dict())
        payload = history.snapshot(limit=1).to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-tools":
        exit_code, payload, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_TOOLS_TOOL_NAME,
            {},
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{payload}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Tool registry view delivered to the live host workspace.")
            return 0
        registry = json.loads(payload)
        LOGGER.info("registered MCP tool candidates:\n%s", payload)
        LOGGER.info("traversal tool candidate=%s", TRAVERSAL_TOOL_NAME)
        LOGGER.info("project query tool candidate=%s", PROJECT_QUERY_TOOL_NAME)
        return 0

    if args.command == "mcp-history":
        history_path = default_mcp_inspection_history_path(settings.project_root)
        prune_default_history_trace(settings.project_root, history_path)
        history = McpInspectionHistoryStore(history_path)
        payload = history.snapshot(limit=args.history_limit).to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-ingest-docs":
        resolved_profile, document_paths = resolve_project_document_profile(args.project_doc_profile)
        result = ingest_project_documents_for_traversal(
            settings.project_root,
            document_profile=resolved_profile,
            document_relpaths=document_paths,
        )
        history = McpInspectionHistoryStore(default_mcp_inspection_history_path(settings.project_root))
        history.record_call(result.tool_call.to_dict())
        payload = json.dumps(result.to_dict(), indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-score-tasks":
        exit_code, payload, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_BUILDER_SCORE_TOOL_NAME,
            {
                "history_limit": args.history_limit,
                "project_doc_profile": args.project_doc_profile,
            },
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{payload}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Builder score view delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-history-view":
        exit_code, rendered, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_HISTORY_VIEW_TOOL_NAME,
            {"history_limit": args.history_limit},
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{rendered}\n")
            return exit_code
        history_payload = json.loads(rendered)
        if isinstance(history_payload, dict) and "summary_text" not in history_payload:
            inspector = build_history_aware_inspector_payload(
                settings.project_root,
                history_path=default_mcp_inspection_history_path(settings.project_root),
                limit=args.history_limit,
            )
            history_payload["summary_text"] = inspector.to_summary_text()
            rendered = json.dumps(history_payload, indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("History view delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, rendered)

    if args.command == "mcp-cockpit":
        exit_code, rendered, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_COCKPIT_TOOL_NAME,
            {
                "history_limit": max(6, args.history_limit),
                "tool_filter": args.tool_filter,
                "layer_filter": args.layer_filter,
            },
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{rendered}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Cockpit view delivered to the live host workspace.")
            return 0
        return launch_visibility_cockpit(settings, rendered)

    if args.command == "mcp-stream":
        exit_code, rendered, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_STREAM_TOOL_NAME,
            {
                "history_limit": args.history_limit,
                "tool_filter": args.tool_filter,
                "layer_filter": args.layer_filter,
            },
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{rendered}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Stream view delivered to the live host workspace.")
            return 0
        return launch_interaction_stream(
            settings,
            history_limit=args.history_limit,
            tool_filter=args.tool_filter,
            layer_filter=args.layer_filter,
        )

    if args.command == "mcp-search-seeds":
        exit_code, payload, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_SEED_SEARCH_TOOL_NAME,
            {
                "query": args.query,
                "seed_limit": args.seed_limit,
                "project_doc_profile": args.project_doc_profile,
            },
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{payload}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Seed search delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-promote-call":
        exit_code, rendered, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_PROMOTE_CALL_TOOL_NAME,
            {
                "call_id": args.call_id,
                "pinned": not args.demote,
            },
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{rendered}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Promotion control delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, rendered)

    if args.command == "mcp-read-panels":
        exit_code, rendered, _ = _run_bridge_enabled_host_command(
            HOST_READ_PANELS_TOOL_NAME,
            {
                "mode": args.panel_mode,
                "panel_name": args.panel_name,
            },
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{rendered}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        return launch_mcp_inspector(settings, rendered)

    if args.command == "ingest-lexicon":
        result = build_english_lexicon_baseline(
            settings.project_root,
            limit=args.limit,
            reset=args.reset,
        )
        payload = result.to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "ingest-python-docs":
        result = build_python_docs_corpus(
            settings.project_root,
            limit=args.limit,
            reset=args.reset,
            include_prose=args.include_prose,
            document_relpaths=None if args.all_python_docs else DEFAULT_PYTHON_DOCS_DOCUMENTS,
        )
        payload = result.to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "lookup-lexicon":
        result = lookup_english_lexicon_entry(
            settings.project_root,
            args.query,
            limit=args.limit or 5,
        )
        payload = result.to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "project-query":
        exit_code, payload, delivered_to_host = _run_bridge_enabled_host_command(
            PROJECT_QUERY_TOOL_NAME,
            {"query": args.query, "limit": args.limit or 3},
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{payload}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Project query delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "project-query-score":
        exit_code, payload, delivered_to_host = _run_bridge_enabled_host_command(
            HOST_PROJECTION_SCORE_TOOL_NAME,
            {"history_limit": args.history_limit},
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{payload}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        if delivered_to_host:
            LOGGER.info("Projection score view delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, payload)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
