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
    PROJECT_QUERY_TOOL_NAME,
    TRAVERSAL_TOOL_NAME,
    DEFAULT_PYTHON_DOCS_DOCUMENTS,
    McpInspectionHistoryStore,
    build_english_lexicon_baseline,
    build_default_registered_tool_call,
    build_history_aware_inspector_payload,
    build_python_docs_corpus,
    build_mcp_tool_registry,
    default_builder_task_score_path,
    default_mcp_inspection_history_path,
    ingest_project_documents_for_traversal,
    lookup_english_lexicon_entry,
    run_project_query_interaction,
    run_real_builder_task_scoring,
    run_seed_search_traversal,
)
from .core.engine import ApplicationEngine
from .core.logging import configure_logging
from .ui.gui_main import launch_ui
from .ui.mcp_inspector import launch_mcp_inspector

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
            "mcp-search-seeds",
            "ingest-python-docs",
            "ingest-lexicon",
            "lookup-lexicon",
            "project-query",
        ),
        help="Command to run.",
    )
    parser.add_argument(
        "--dump-json",
        action="store_true",
        help="For inspection commands, write raw JSON to stdout instead of opening a panel or logging.",
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
        history = McpInspectionHistoryStore(default_mcp_inspection_history_path(settings.project_root))
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
        inspector = build_history_aware_inspector_payload(
            settings.project_root,
            history_path=default_mcp_inspection_history_path(settings.project_root),
            limit=args.history_limit,
        )
        payload = inspector.to_dict()
        payload["summary_text"] = inspector.to_summary_text()
        rendered = json.dumps(payload, indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{rendered}\n")
            return 0
        return launch_mcp_inspector(settings, rendered)

    if args.command == "mcp-search-seeds":
        result = run_seed_search_traversal(
            settings.project_root,
            args.query,
            history_path=default_mcp_inspection_history_path(settings.project_root),
            limit=args.seed_limit,
        )
        payload = result.to_json()
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
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
        capture = run_project_query_interaction(
            settings.project_root,
            args.query,
            limit=args.limit or 3,
            actor="human",
            source_surface="cli",
        )
        call = {
            "call_id": capture.capture_id,
            "tool": {
                "tool_name": PROJECT_QUERY_TOOL_NAME,
                "capability_name": capture.capability["name"],
                "title": "Project Query Through Context Layers",
                "readiness": "registration_candidate",
            },
            "status": "ok",
            "capture": capture.to_dict(),
        }
        history = McpInspectionHistoryStore(default_mcp_inspection_history_path(settings.project_root))
        history.record_call(call)
        payload = json.dumps(call, indent=2, sort_keys=True)
        if args.dump_json:
            sys.stdout.write(f"{payload}\n")
            return 0
        return launch_mcp_inspector(settings, payload)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
