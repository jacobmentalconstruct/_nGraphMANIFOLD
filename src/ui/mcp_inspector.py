"""Raw MCP inspection panel."""

from __future__ import annotations

import json
import logging

from src.core.config import AppSettings

LOGGER = logging.getLogger(__name__)


def launch_mcp_inspector(settings: AppSettings, payload: str) -> int:
    """Open a minimal raw JSON viewer for MCP-shaped inspection data."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        LOGGER.exception("MCP inspector UI is unavailable. project_root=%s", settings.project_root)
        LOGGER.info("MCP inspection payload:\n%s", payload)
        return 1

    try:
        root = tk.Tk()
        root.title("nGraphMANIFOLD MCP Inspector")
        root.geometry("980x720")

        frame = ttk.Frame(root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        parsed = _try_parse_json(payload)
        if parsed and "raw" in parsed:
            tabs = ttk.Notebook(frame)
            tabs.pack(fill=tk.BOTH, expand=True)
            summary_tab = ttk.Frame(tabs, padding=4)
            raw_tab = ttk.Frame(tabs, padding=4)
            tabs.add(summary_tab, text="Summary")
            tabs.add(raw_tab, text="Raw JSON")
            _add_text_view(summary_tab, _summary_text(parsed))
            _add_text_view(raw_tab, payload)
        else:
            _add_text_view(frame, payload)

        LOGGER.info("MCP inspector opened. project_root=%s", settings.project_root)
        root.mainloop()
        return 0
    except Exception:
        LOGGER.exception("MCP inspector panel could not be opened. project_root=%s", settings.project_root)
        LOGGER.info("MCP inspection payload:\n%s", payload)
        return 1


def _add_text_view(parent, payload: str) -> None:
    import tkinter as tk
    from tkinter import ttk

    text = tk.Text(parent, wrap="none", undo=False)
    y_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text.yview)
    x_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text.xview)
    text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    text.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    text.insert("1.0", payload)
    text.configure(state="disabled")


def _try_parse_json(payload: str) -> dict | None:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _summary_text(payload: dict) -> str:
    if "summary_text" in payload:
        return str(payload["summary_text"])
    lines = [
        "nGraphMANIFOLD MCP History",
        f"records: {payload.get('record_count', 'n/a')}",
        f"history: {payload.get('history_path', 'n/a')}",
        "",
        "Recent calls:",
    ]
    for call in payload.get("calls", []):
        task = f" task={call.get('task_id')}" if call.get("task_id") else ""
        projection = ""
        if call.get("selected_layer"):
            projection = (
                f" selected_layer={call.get('selected_layer')} "
                f"candidates={call.get('candidate_count')}"
            )
        lines.append(
            f"- {call.get('captured_at')} {call.get('tool_name')} "
            f"score={call.get('aggregate_score')} steps={call.get('step_count')} "
            f"blockers={call.get('blocker_count')}{projection}{task}"
        )
    return "\n".join(lines)
