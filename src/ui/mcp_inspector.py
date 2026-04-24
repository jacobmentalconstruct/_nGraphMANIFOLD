"""Raw MCP inspection panel."""

from __future__ import annotations

import json
import logging

from src.core.config import AppSettings
from src.core.coordination import (
    build_interaction_stream_payload,
    default_host_state,
)

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
        if parsed and ("raw" in parsed or "search" in parsed or _has_projection_frame(parsed)):
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


def launch_visibility_cockpit(settings: AppSettings, payload: str) -> int:
    """Open a unified read-only visibility cockpit over existing history surfaces."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        LOGGER.exception("Visibility cockpit UI is unavailable. project_root=%s", settings.project_root)
        LOGGER.info("Visibility cockpit payload:\n%s", payload)
        return 1

    parsed = _try_parse_json(payload) or {}
    try:
        root = tk.Tk()
        root.title("nGraphMANIFOLD Visibility Cockpit")
        root.geometry("1240x860")

        frame = ttk.Frame(root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        tabs = ttk.Notebook(frame)
        tabs.grid(row=0, column=0, sticky="nsew")
        cockpit_tab = ttk.Frame(tabs, padding=6)
        raw_tab = ttk.Frame(tabs, padding=6)
        tabs.add(cockpit_tab, text="Cockpit")
        tabs.add(raw_tab, text="Raw JSON")

        _build_cockpit_tab(cockpit_tab, parsed)
        _add_text_view(raw_tab, payload)

        LOGGER.info("Visibility cockpit opened. project_root=%s", settings.project_root)
        root.mainloop()
        return 0
    except Exception:
        LOGGER.exception("Visibility cockpit could not be opened. project_root=%s", settings.project_root)
        LOGGER.info("Visibility cockpit payload:\n%s", payload)
        return 1


def launch_interaction_stream(
    settings: AppSettings,
    *,
    history_limit: int = 50,
    poll_ms: int = 1500,
    tool_filter: str = "",
    layer_filter: str = "",
) -> int:
    """Open a basic polling stream of recent query/result records."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        LOGGER.exception("Interaction stream UI is unavailable. project_root=%s", settings.project_root)
        return 1

    try:
        host_state = default_host_state(settings.project_root, history_limit=history_limit)
        host_state.refresh()
        root = tk.Tk()
        root.title("nGraphMANIFOLD Interaction Stream")
        root.geometry("1080x760")

        frame = ttk.Frame(root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        controls = ttk.Frame(frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        status_var = tk.StringVar(value="stream starting")
        ttk.Label(controls, textvariable=status_var).pack(side=tk.LEFT)
        ttk.Button(controls, text="Refresh", command=lambda: _refresh()).pack(side=tk.RIGHT)

        tabs = ttk.Notebook(frame)
        tabs.grid(row=1, column=0, sticky="nsew")
        stream_tab = ttk.Frame(tabs, padding=4)
        raw_tab = ttk.Frame(tabs, padding=4)
        tabs.add(stream_tab, text="Stream")
        tabs.add(raw_tab, text="Raw JSON")
        stream_text = _add_mutable_text_view(stream_tab)
        stream_text._ngraph_stream_call_ids = set()
        _configure_stream_tags(stream_text)
        raw_text = _add_mutable_text_view(raw_tab)

        def _refresh() -> None:
            snapshot = host_state.refresh()
            stream_payload = build_interaction_stream_payload(
                settings.project_root,
                history_path=snapshot.history_path,
                limit=history_limit,
                tool_filter=tool_filter,
                layer_filter=layer_filter,
            )
            _sync_stream_items(stream_text, stream_payload.items)
            _write_text(raw_text, stream_payload.to_json())
            filter_bits = []
            if tool_filter:
                filter_bits.append(f"tool={tool_filter}")
            if layer_filter:
                filter_bits.append(f"layer={layer_filter}")
            filter_text = f" filters={' '.join(filter_bits)}" if filter_bits else ""
            status_var.set(
                f"records={snapshot.record_count} showing={len(stream_payload.items)}{filter_text}"
            )

        def _poll() -> None:
            _refresh()
            root.after(max(500, int(poll_ms)), _poll)

        _poll()
        LOGGER.info("Interaction stream opened. project_root=%s", settings.project_root)
        root.mainloop()
        return 0
    except Exception:
        LOGGER.exception("Interaction stream could not be opened. project_root=%s", settings.project_root)
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


def _add_mutable_text_view(parent):
    import tkinter as tk
    from tkinter import ttk

    text = tk.Text(parent, wrap="word", undo=False)
    y_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text.yview)
    x_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text.xview)
    text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    text._ngraph_scrollbar_held = False

    text.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    def _pause_autoscroll(_event) -> None:
        text._ngraph_scrollbar_held = True

    def _resume_autoscroll(_event) -> None:
        text._ngraph_scrollbar_held = False

    y_scroll.bind("<ButtonPress-1>", _pause_autoscroll)
    y_scroll.bind("<ButtonRelease-1>", _resume_autoscroll)
    return text


def _write_text(text_widget, payload: str) -> None:
    text_widget.configure(state="normal")
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", payload)
    text_widget.see("end")
    text_widget.configure(state="disabled")


def _configure_stream_tags(text_widget) -> None:
    text_widget.configure(
        background="#f6f8fb",
        foreground="#18212f",
        padx=10,
        pady=10,
        spacing1=2,
        spacing3=2,
    )
    text_widget.tag_configure(
        "card_top",
        background="#dfe8f5",
        foreground="#172033",
        font=("Segoe UI", 10, "bold"),
        lmargin1=12,
        lmargin2=12,
        rmargin=12,
        spacing1=10,
    )
    text_widget.tag_configure(
        "card_body",
        background="#ffffff",
        foreground="#1e293b",
        font=("Segoe UI", 10),
        lmargin1=18,
        lmargin2=18,
        rmargin=12,
    )
    text_widget.tag_configure(
        "label",
        background="#ffffff",
        foreground="#475569",
        font=("Segoe UI", 9, "bold"),
    )
    text_widget.tag_configure(
        "query",
        background="#eef6ff",
        foreground="#0f3b63",
        font=("Segoe UI", 10, "bold"),
        lmargin1=18,
        lmargin2=18,
        rmargin=12,
    )
    text_widget.tag_configure(
        "response",
        background="#eefaf2",
        foreground="#14532d",
        font=("Segoe UI", 10, "bold"),
        lmargin1=18,
        lmargin2=18,
        rmargin=12,
    )
    text_widget.tag_configure(
        "subtle",
        background="#ffffff",
        foreground="#64748b",
        font=("Segoe UI", 9),
        lmargin1=18,
        lmargin2=18,
        rmargin=12,
    )
    text_widget.tag_configure(
        "spacer",
        background="#f6f8fb",
        font=("Segoe UI", 4),
    )


def _write_stream_items(text_widget, items) -> None:
    text_widget._ngraph_stream_call_ids = set()
    text_widget.configure(state="normal")
    text_widget.delete("1.0", "end")
    if not items:
        text_widget.insert("end", "No interaction records yet.\n", ("subtle",))
    for index, item in enumerate(items, start=1):
        _insert_stream_item(text_widget, item, index)
        text_widget._ngraph_stream_call_ids.add(item.call_id)
    text_widget.see("end")
    text_widget.configure(state="disabled")


def _sync_stream_items(text_widget, items) -> None:
    known_ids = getattr(text_widget, "_ngraph_stream_call_ids", set())
    if not known_ids:
        _write_stream_items(text_widget, items)
        return
    new_items = [item for item in items if item.call_id not in known_ids]
    if not new_items:
        return
    scrollbar_held = bool(getattr(text_widget, "_ngraph_scrollbar_held", False))
    previous_yview = text_widget.yview()
    text_widget.configure(state="normal")
    current_count = len(known_ids)
    for offset, item in enumerate(new_items, start=1):
        _insert_stream_item(text_widget, item, current_count + offset)
        known_ids.add(item.call_id)
    text_widget._ngraph_stream_call_ids = known_ids
    if scrollbar_held:
        text_widget.yview_moveto(previous_yview[0])
    else:
        text_widget.see("end")
    text_widget.configure(state="disabled")


def _insert_stream_item(text_widget, item, index: int) -> None:
    text_widget.insert(
        "end",
        f"  Object {index}  |  {item.captured_at}  |  {item.tool_name}  |  {item.status}  \n",
        ("card_top",),
    )
    text_widget.insert("end", "  QUERY   ", ("label", "query"))
    text_widget.insert("end", f"{item.query or '(no query text)'}\n", ("query",))
    text_widget.insert("end", "  RESULT  ", ("label", "response"))
    text_widget.insert("end", f"{item.response or '(no response summary)'}\n", ("response",))
    if item.selected_layer:
        text_widget.insert(
            "end",
            f"  LAYER   {item.selected_layer}    KIND {item.selected_kind or 'n/a'}    SCORE {item.selected_score}\n",
            ("card_body",),
        )
    if item.content_preview:
        text_widget.insert("end", f"  PREVIEW {item.content_preview}\n", ("card_body",))
    if item.source_ref:
        text_widget.insert("end", f"  SOURCE  {item.source_ref}\n", ("subtle",))
    for flow_item in getattr(item, "projection_flow", ()):
        text_widget.insert(
            "end",
            "  FLOW    "
            f"{flow_item.get('role')} rank {flow_item.get('rank')} "
            f"{flow_item.get('kind')} score={flow_item.get('score')} "
            f"{flow_item.get('content_preview', '')}\n",
            ("subtle",),
        )
    text_widget.insert(
        "end",
        f"  CALL    {item.call_id}    AGGREGATE {item.aggregate_score}\n",
        ("subtle",),
    )
    text_widget.insert("end", "\n", ("spacer",))


def _try_parse_json(payload: str) -> dict | None:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _has_projection_frame(payload: dict) -> bool:
    return bool(payload.get("capture", {}).get("response", {}).get("projection_frame"))


def _summary_text(payload: dict) -> str:
    if "search" in payload:
        return _seed_search_summary_text(payload)
    if _has_projection_frame(payload):
        return _projection_summary_text(payload)
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


def _seed_search_summary_text(payload: dict) -> str:
    search = payload.get("search", {})
    selected = search.get("selected_seed") or {}
    flow = search.get("selected_flow") or {}
    lines = [
        "nGraphMANIFOLD Seed Flow",
        f"query: {search.get('query', 'n/a')}",
        f"candidate_count: {search.get('candidate_count', 'n/a')}",
        "",
        "Selected Seed:",
        f"source: {selected.get('source_ref', 'n/a')}",
        f"kind: {selected.get('kind', 'n/a')}",
        f"score: {selected.get('score', 'n/a')}",
    ]
    heading = " > ".join(str(item) for item in selected.get("heading_trail", []) if item)
    if heading:
        lines.append(f"heading: {heading}")
    if selected.get("matched_terms"):
        lines.append(f"matched_terms: {', '.join(str(item) for item in selected.get('matched_terms', []))}")
    lines.append("")
    lines.append("Score Breakdown:")
    breakdown = selected.get("score_breakdown") or {}
    if breakdown:
        for key, value in sorted(breakdown.items(), key=lambda item: (-float(item[1]), item[0])):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- n/a")
    breadcrumb = flow.get("breadcrumb") or []
    if breadcrumb:
        lines.append("")
        lines.append("Breadcrumb:")
        lines.append(" > ".join(str(item) for item in breadcrumb))
    lines.append("")
    lines.append("Source Flow:")
    flow_objects = flow.get("objects") or []
    if not flow_objects:
        lines.append("- n/a")
    for obj in flow_objects:
        prefix = ">>" if obj.get("role") == "selected" else "  "
        block = obj.get("block_index")
        block_text = f"block {block}" if block is not None else "block n/a"
        obj_heading = " > ".join(str(item) for item in obj.get("heading_trail", []) if item)
        heading_suffix = f" [{obj_heading}]" if obj_heading else ""
        lines.append(
            f"{prefix} {obj.get('role')} {block_text} {obj.get('kind')}{heading_suffix}: "
            f"{obj.get('content_preview', '')}"
        )
    lines.append("")
    lines.append("Recent Traversal:")
    tool_call = payload.get("tool_call", {})
    capture = tool_call.get("capture", {})
    traversal = capture.get("response", {}).get("traversal_report", {})
    lines.append(f"tool: {tool_call.get('tool', {}).get('tool_name', 'n/a')}")
    lines.append(f"steps: {len(traversal.get('steps', []))}")
    lines.append(f"blockers: {len(traversal.get('blockers', []))}")
    return "\n".join(lines)


def _projection_summary_text(payload: dict) -> str:
    capture = payload.get("capture", {})
    command = capture.get("command", {})
    frame = capture.get("response", {}).get("projection_frame", {})
    selected = frame.get("selected_candidate") or {}
    flow = frame.get("selected_flow") or {}
    lines = [
        "nGraphMANIFOLD Projection Flow",
        f"query: {command.get('payload', {}).get('query', 'n/a')}",
        f"selected_layer: {frame.get('selected_layer', 'n/a')}",
        f"context_stack: {', '.join(str(item) for item in frame.get('context_stack', []))}",
        "",
        "Selected Candidate:",
        f"kind: {selected.get('kind', 'n/a')}",
        f"score: {selected.get('score', 'n/a')}",
        f"source: {selected.get('source_ref', 'n/a')}",
    ]
    heading = " > ".join(str(item) for item in selected.get("heading_trail", []) if item)
    if heading:
        lines.append(f"heading: {heading}")
    matched = selected.get("matched_terms") or []
    if matched:
        lines.append(f"matched_terms: {', '.join(str(item) for item in matched)}")
    evidence = selected.get("evidence") or []
    if evidence:
        lines.append(f"evidence: {' | '.join(str(item) for item in evidence)}")
    lines.append("")
    lines.append("Layer Summary:")
    for projection in frame.get("projections", []):
        layer = projection.get("layer", {})
        lines.append(
            f"- {layer.get('name', 'n/a')} score={projection.get('layer_score', 'n/a')} "
            f"candidates={projection.get('candidate_count', 'n/a')}"
        )
    breadcrumb = flow.get("breadcrumb") or []
    if breadcrumb:
        lines.append("")
        lines.append("Breadcrumb:")
        lines.append(" > ".join(str(item) for item in breadcrumb))
    lines.append("")
    lines.append("Projection Flow:")
    flow_objects = flow.get("objects") or []
    if not flow_objects:
        lines.append("- n/a")
    for obj in flow_objects:
        prefix = ">>" if obj.get("role") == "selected" else "  "
        lines.append(
            f"{prefix} {obj.get('role')} rank {obj.get('rank')} "
            f"{obj.get('kind')} score={obj.get('score')}: {obj.get('content_preview', '')}"
        )
    return "\n".join(lines)


def _build_cockpit_tab(parent, payload: dict) -> None:
    import tkinter as tk
    from tkinter import ttk

    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    content = ttk.Frame(canvas, padding=4)
    window = canvas.create_window((0, 0), window=content, anchor="nw")

    def _resize_content(event) -> None:
        canvas.itemconfigure(window, width=event.width)

    def _sync_scroll(_event) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", _resize_content)
    content.bind("<Configure>", _sync_scroll)

    content.columnconfigure(0, weight=1)
    row = 0
    _cockpit_section(
        content,
        row,
        "Scores",
        _cockpit_scores_text(payload),
    )
    row += 1
    _cockpit_section(
        content,
        row,
        "Latest Projection",
        _cockpit_projection_text(payload.get("latest_projection")),
    )
    row += 1
    _cockpit_section(
        content,
        row,
        "Latest Seed",
        _cockpit_seed_text(payload.get("latest_seed")),
    )
    row += 1
    _cockpit_section(
        content,
        row,
        "Recent Stream",
        _cockpit_stream_text(payload.get("stream", {})),
    )


def _cockpit_section(parent, row: int, title: str, body: str) -> None:
    from tkinter import ttk

    section = ttk.LabelFrame(parent, text=title, padding=8)
    section.grid(row=row, column=0, sticky="ew", pady=(0, 8))
    section.columnconfigure(0, weight=1)
    text = _add_mutable_text_view(section)
    _write_text(text, body)


def _cockpit_scores_text(payload: dict) -> str:
    builder = payload.get("latest_builder_score") or {}
    projection = payload.get("latest_projection_score") or {}
    builder_report = builder.get("usefulness_report", {})
    projection_report = projection.get("usefulness_report", {})
    lines = [
        f"builder_score: {builder_report.get('aggregate_score', 'n/a')} accepted={builder.get('meets_acceptance', 'n/a')}",
        f"projection_score: {projection_report.get('aggregate_score', 'n/a')} accepted={projection.get('meets_acceptance', 'n/a')}",
        f"history_records: {payload.get('record_count', 'n/a')}",
        f"history_path: {payload.get('history_path', 'n/a')}",
    ]
    return "\n".join(lines)


def _cockpit_projection_text(payload: dict | None) -> str:
    if not payload:
        return "No project-query capture found yet."
    selected = payload.get("selected_candidate") or {}
    flow = payload.get("selected_flow") or {}
    lines = [
        f"query: {payload.get('query', 'n/a')}",
        f"selected_layer: {payload.get('selected_layer', 'n/a')}",
        f"selected_kind: {selected.get('kind', 'n/a')}",
        f"selected_score: {selected.get('score', 'n/a')}",
        f"source: {selected.get('source_ref', 'n/a')}",
        "",
        "layer_summaries:",
    ]
    for item in payload.get("layer_summaries", []):
        lines.append(
            f"- {item.get('name', 'n/a')} score={item.get('layer_score', 'n/a')} "
            f"candidates={item.get('candidate_count', 'n/a')}"
        )
    lines.append("")
    lines.append("projection_flow:")
    for item in flow.get("objects", []):
        lines.append(
            f"- {item.get('role')} rank {item.get('rank')} {item.get('kind')} "
            f"score={item.get('score')}: {item.get('content_preview', '')}"
        )
    if not flow.get("objects"):
        lines.append("- n/a")
    return "\n".join(lines)


def _cockpit_seed_text(payload: dict | None) -> str:
    if not payload:
        return "No builder-seed snapshot found yet."
    flow = payload.get("seed_flow") or {}
    lines = [
        f"task_id: {payload.get('task_id', 'n/a')}",
        f"seed_source: {payload.get('seed_source_ref', 'n/a')}",
        f"steps: {payload.get('traversal_step_count', 'n/a')}",
        f"blockers: {payload.get('blocker_count', 'n/a')}",
        "",
        "seed_flow:",
    ]
    for item in flow.get("objects", []):
        lines.append(
            f"- {item.get('role')} block {item.get('block_index')} "
            f"{item.get('kind')}: {item.get('content_preview', '')}"
        )
    if not flow.get("objects"):
        lines.append("- n/a")
    return "\n".join(lines)


def _cockpit_stream_text(payload: dict) -> str:
    items = payload.get("items", [])
    if not items:
        return "No stream items yet."
    lines: list[str] = []
    for index, item in enumerate(items[:6], start=1):
        lines.append(
            f"[{index}] {item.get('captured_at', 'n/a')} {item.get('tool_name', 'n/a')} "
            f"{item.get('query', '(no query)')}"
        )
        lines.append(f"    {item.get('response', '(no response)')}")
    return "\n".join(lines)
