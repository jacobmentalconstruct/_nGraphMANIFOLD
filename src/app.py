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
    DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
    HOST_COCKPIT_TOOL_NAME,
    HOST_HISTORY_VIEW_TOOL_NAME,
    HOST_SEED_SEARCH_TOOL_NAME,
    HOST_STREAM_TOOL_NAME,
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
    prune_default_history_trace,
    dispatch_command_via_host_bridge,
    dispatch_host_command,
    ingest_project_documents_for_traversal,
    lookup_english_lexicon_entry,
    run_context_projection_arbitration_scoring,
    run_real_builder_task_scoring,
    run_seed_search_traversal,
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
        "--use-host-bridge",
        action="store_true",
        help="For bridge-enabled commands, target the already-open host workspace instead of running locally.",
    )
    parser.add_argument(
        "--bridge-timeout-ms",
        type=int,
        default=DEFAULT_HOST_BRIDGE_TIMEOUT_MS,
        help="When using --use-host-bridge, milliseconds to wait for the live host to process the request.",
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

    def _run_bridge_enabled_host_command(command_name: str, payload: dict[str, object]) -> tuple[int, str]:
        command = create_host_command_envelope(
            tool_name=command_name,
            payload=payload,
            actor="human",
            source_surface="cli-bridge" if args.use_host_bridge else "cli",
        )
        if args.use_host_bridge:
            try:
                response = dispatch_command_via_host_bridge(
                    settings.project_root,
                    command,
                    timeout_ms=args.bridge_timeout_ms,
                )
            except HostBridgeUnavailableError as exc:
                LOGGER.error("Host bridge unavailable: %s", exc)
                return 1, json.dumps({"error": str(exc)}, indent=2, sort_keys=True)
            except HostBridgeError as exc:
                LOGGER.error("Host bridge failed: %s", exc)
                return 1, json.dumps({"error": str(exc)}, indent=2, sort_keys=True)
            rendered = json.dumps(response.payload or {}, indent=2, sort_keys=True)
            return 0, rendered
        result = dispatch_host_command(
            settings.project_root,
            command,
            history_limit=args.history_limit,
        )
        return 0, result.rendered_json

    if args.command == "status":
        status = engine.status()
        LOGGER.info("nGraphMANIFOLD status: %s", status.status)
        LOGGER.info("project_root=%s", status.project_root)
        LOGGER.info("active_tranche=%s", status.active_tranche)
        LOGGER.info("next_tranche=%s", status.next_tranche)
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
        registry = build_mcp_tool_registry()
        payload = json.dumps(registry.to_dict(), indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
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
        result = ingest_project_documents_for_traversal(settings.project_root)
        history = McpInspectionHistoryStore(default_mcp_inspection_history_path(settings.project_root))
        history.record_call(result.tool_call.to_dict())
        payload = json.dumps(result.to_dict(), indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-score-tasks":
        run = run_real_builder_task_scoring(
            settings.project_root,
            history_path=default_mcp_inspection_history_path(settings.project_root),
            score_path=default_builder_task_score_path(settings.project_root),
        )
        payload = run.to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "mcp-history-view":
        result = dispatch_host_command(
            settings.project_root,
            create_host_command_envelope(
                tool_name=HOST_HISTORY_VIEW_TOOL_NAME,
                payload={"history_limit": args.history_limit},
                actor="human",
                source_surface="cli",
            ),
            history_limit=args.history_limit,
        )
        payload = dict(result.payload)
        inspector = build_history_aware_inspector_payload(
            settings.project_root,
            history_path=default_mcp_inspection_history_path(settings.project_root),
            limit=args.history_limit,
        )
        payload["summary_text"] = inspector.to_summary_text()
        rendered = json.dumps(payload, indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        return launch_mcp_inspector(settings, rendered)

    if args.command == "mcp-cockpit":
        result = dispatch_host_command(
            settings.project_root,
            create_host_command_envelope(
                tool_name=HOST_COCKPIT_TOOL_NAME,
                payload={"history_limit": max(6, args.history_limit)},
                actor="human",
                source_surface="cli",
            ),
            history_limit=max(6, args.history_limit),
        )
        rendered = result.rendered_json
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        return launch_visibility_cockpit(settings, rendered)

    if args.command == "mcp-stream":
        result = dispatch_host_command(
            settings.project_root,
            create_host_command_envelope(
                tool_name=HOST_STREAM_TOOL_NAME,
                payload={"history_limit": args.history_limit},
                actor="human",
                source_surface="cli",
            ),
            history_limit=args.history_limit,
        )
        if args.dump_json:
            sys.stdout.write(f"{result.rendered_json}\n")
            return 0
        return launch_interaction_stream(settings, history_limit=args.history_limit)

    if args.command == "mcp-search-seeds":
        exit_code, payload = _run_bridge_enabled_host_command(
            HOST_SEED_SEARCH_TOOL_NAME,
            {"query": args.query, "seed_limit": args.seed_limit},
        )
        if exit_code != 0:
            if args.dump_json:
                sys.stdout.write(f"{payload}\n")
            return exit_code
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        if args.use_host_bridge:
            LOGGER.info("Seed search delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, payload)

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
        exit_code, payload = _run_bridge_enabled_host_command(
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
        if args.use_host_bridge:
            LOGGER.info("Project query delivered to the live host workspace.")
            return 0
        return launch_mcp_inspector(settings, payload)

    if args.command == "project-query-score":
        run = run_context_projection_arbitration_scoring(
            settings.project_root,
            history_path=default_mcp_inspection_history_path(settings.project_root),
            score_path=default_context_projection_score_path(settings.project_root),
        )
        payload = run.to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
