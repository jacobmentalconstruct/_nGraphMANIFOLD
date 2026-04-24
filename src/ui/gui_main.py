"""Primary desktop host workspace for the shared command/state spine."""

from __future__ import annotations

import logging
from typing import Any

from src.core.config import AppSettings
from src.core.coordination import (
    DEFAULT_HOST_BRIDGE_POLL_INTERVAL_MS,
    HOST_COCKPIT_TOOL_NAME,
    HOST_HISTORY_VIEW_TOOL_NAME,
    HOST_PANEL_ORDER,
    HOST_STATUS_TOOL_NAME,
    HOST_TOOLS_TOOL_NAME,
    HOST_PROMOTE_CALL_TOOL_NAME,
    HOST_READ_PANELS_TOOL_NAME,
    HOST_BUILDER_SCORE_TOOL_NAME,
    HOST_PROJECTION_SCORE_TOOL_NAME,
    HOST_SEED_SEARCH_TOOL_NAME,
    HOST_STREAM_TOOL_NAME,
    PROJECT_QUERY_TOOL_NAME,
    SharedHostState,
    activate_host_bridge_session,
    close_host_bridge_session,
    create_host_command_envelope,
    default_host_state,
    dispatch_host_command,
    heartbeat_host_bridge_session,
    pending_host_bridge_request_count,
    process_pending_host_bridge_requests,
)

LOGGER = logging.getLogger(__name__)


def run_ui_project_query(
    settings: AppSettings,
    query: str,
    *,
    limit: int = 3,
    host_state: SharedHostState | None = None,
) -> dict[str, Any]:
    """Run project query from the shared UI host surface."""
    command = create_host_command_envelope(
        tool_name=PROJECT_QUERY_TOOL_NAME,
        payload={"query": query, "limit": int(limit)},
        actor="human",
        source_surface="ui",
    )
    return dispatch_host_command(
        settings.project_root,
        command,
        state=host_state,
    ).payload


def launch_ui(settings: AppSettings) -> int:
    """Open the canonical desktop host workspace for the prototype."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        LOGGER.exception("UI is unavailable. project_root=%s", settings.project_root)
        return 1

    try:
        host_state = default_host_state(settings.project_root, history_limit=12)
        snapshot = host_state.refresh()
        bridge_session = activate_host_bridge_session(settings.project_root)
        host_state.cache_payload("host_bridge_session", bridge_session.to_dict())
        host_state.cache_payload("host_bridge_pending_count", 0)

        root = tk.Tk()
        root.title("nGraphMANIFOLD Host Workspace")
        root.geometry("1280x860")

        frame = ttk.Frame(root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        controls = ttk.Frame(frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        controls.columnconfigure(0, weight=1)

        query_var = tk.StringVar(value="class object function")
        limit_var = tk.IntVar(value=3)
        status_var = tk.StringVar(value=f"records={snapshot.record_count}")
        ttk.Entry(controls, textvariable=query_var).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Spinbox(controls, from_=1, to=20, textvariable=limit_var, width=4).grid(
            row=0, column=1, padx=(0, 6)
        )
        run_query_button = ttk.Button(controls, text="Project Query")
        run_query_button.grid(row=0, column=2, padx=(0, 6))
        seed_search_button = ttk.Button(controls, text="Seed Search")
        seed_search_button.grid(row=0, column=3, padx=(0, 6))
        promote_button = ttk.Button(controls, text="Promote Active")
        promote_button.grid(row=0, column=4, padx=(0, 6))
        demote_button = ttk.Button(controls, text="Demote Active")
        demote_button.grid(row=0, column=5, padx=(0, 6))
        refresh_button = ttk.Button(controls, text="Refresh")
        refresh_button.grid(row=0, column=6, padx=(0, 6))
        status_button = ttk.Button(controls, text="Status")
        status_button.grid(row=0, column=7, padx=(0, 6))
        tools_button = ttk.Button(controls, text="Tools")
        tools_button.grid(row=0, column=8, padx=(0, 6))
        builder_score_button = ttk.Button(controls, text="Builder Score")
        builder_score_button.grid(row=0, column=9, padx=(0, 6))
        projection_score_button = ttk.Button(controls, text="Projection Score")
        projection_score_button.grid(row=0, column=10, padx=(0, 6))
        ttk.Label(controls, textvariable=status_var).grid(row=0, column=11, sticky="e")

        tabs = ttk.Notebook(frame)
        tabs.grid(row=1, column=0, sticky="nsew")
        stream_tab = ttk.Frame(tabs, padding=4)
        history_tab = ttk.Frame(tabs, padding=4)
        cockpit_tab = ttk.Frame(tabs, padding=4)
        status_tab = ttk.Frame(tabs, padding=4)
        tools_tab = ttk.Frame(tabs, padding=4)
        projection_tab = ttk.Frame(tabs, padding=4)
        seed_tab = ttk.Frame(tabs, padding=4)
        scores_tab = ttk.Frame(tabs, padding=4)
        raw_tab = ttk.Frame(tabs, padding=4)
        tabs.add(stream_tab, text="Command Stream")
        tabs.add(history_tab, text="History Summary")
        tabs.add(cockpit_tab, text="Cockpit")
        tabs.add(status_tab, text="Status")
        tabs.add(tools_tab, text="Tool Registry")
        tabs.add(projection_tab, text="Active Projection")
        tabs.add(seed_tab, text="Active Seed Flow")
        tabs.add(scores_tab, text="Scores")
        tabs.add(raw_tab, text="Raw JSON")
        tab_name_to_frame = {
            "stream": stream_tab,
            "history": history_tab,
            "cockpit": cockpit_tab,
            "status": status_tab,
            "tools": tools_tab,
            "projection": projection_tab,
            "seed": seed_tab,
            "scores": scores_tab,
            "raw": raw_tab,
        }
        tab_id_to_name = {str(frame): name for name, frame in tab_name_to_frame.items()}

        stream_text = _add_text_view(stream_tab)
        history_text = _add_text_view(history_tab)
        cockpit_text = _add_text_view(cockpit_tab)
        status_text = _add_text_view(status_tab)
        tools_text = _add_text_view(tools_tab)
        projection_text = _add_text_view(projection_tab)
        seed_text = _add_text_view(seed_tab)
        scores_text = _add_text_view(scores_tab)
        raw_text = _add_text_view(raw_tab)

        def _render_snapshot() -> None:
            current = host_state.refresh()
            panels = current.panels
            _write_text(stream_text, str((panels.get("stream") or {}).get("text", "")))
            _write_text(history_text, str((panels.get("history") or {}).get("text", "")))
            _write_text(cockpit_text, str((panels.get("cockpit") or {}).get("text", "")))
            _write_text(status_text, str((panels.get("status") or {}).get("text", "")))
            _write_text(tools_text, str((panels.get("tools") or {}).get("text", "")))
            _write_text(projection_text, str((panels.get("projection") or {}).get("text", "")))
            _write_text(seed_text, str((panels.get("seed") or {}).get("text", "")))
            _write_text(scores_text, str((panels.get("scores") or {}).get("text", "")))
            _write_text(raw_text, str((panels.get("raw") or {}).get("text", current.to_json())))
            _update_status(current)

        def _select_panel(panel_name: str) -> None:
            frame = tab_name_to_frame.get(panel_name)
            if frame is None:
                return
            host_state.set_active_tab(panel_name)
            tabs.select(frame)

        def _update_status(current=None) -> None:
            current = current or host_state.snapshot or host_state.refresh()
            active_tool = current.active_command.get("tool_name", "") if current.active_command else ""
            live_cache = host_state.raw_payload_cache
            bridge_info = live_cache.get("host_bridge_session", {})
            pending_count = int(live_cache.get("host_bridge_pending_count", 0))
            bridge_id = str(bridge_info.get("session_id", ""))[:8] or "none"
            status_var.set(
                f"records={current.record_count} active={active_tool or 'none'} "
                f"tab={current.active_tab} cache={len(live_cache)} bridge={bridge_id} pending={pending_count}"
            )

        def _run_command(command) -> None:
            run_query_button.configure(state="disabled")
            seed_search_button.configure(state="disabled")
            promote_button.configure(state="disabled")
            demote_button.configure(state="disabled")
            refresh_button.configure(state="disabled")
            status_button.configure(state="disabled")
            tools_button.configure(state="disabled")
            builder_score_button.configure(state="disabled")
            projection_score_button.configure(state="disabled")
            root.update_idletasks()
            try:
                dispatch_host_command(settings.project_root, command, state=host_state)
                _render_snapshot()
            except Exception as exc:
                LOGGER.exception("Host workspace action failed. project_root=%s", settings.project_root)
                status_var.set(f"action failed: {exc}")
            finally:
                run_query_button.configure(state="normal")
                seed_search_button.configure(state="normal")
                promote_button.configure(state="normal")
                demote_button.configure(state="normal")
                refresh_button.configure(state="normal")
                status_button.configure(state="normal")
                tools_button.configure(state="normal")
                builder_score_button.configure(state="normal")
                projection_score_button.configure(state="normal")

        def _dispatch(tool_name: str) -> None:
            query = query_var.get().strip()
            if tool_name in {PROJECT_QUERY_TOOL_NAME, HOST_SEED_SEARCH_TOOL_NAME} and not query:
                status_var.set("query is empty")
                return
            if tool_name == HOST_PROMOTE_CALL_TOOL_NAME and not host_state.active_call_id:
                status_var.set("no active call to promote")
                return
            try:
                if tool_name == PROJECT_QUERY_TOOL_NAME:
                    command = create_host_command_envelope(
                        tool_name=PROJECT_QUERY_TOOL_NAME,
                        payload={"query": query, "limit": max(1, int(limit_var.get()))},
                        actor="human",
                        source_surface="ui",
                    )
                elif tool_name == HOST_SEED_SEARCH_TOOL_NAME:
                    command = create_host_command_envelope(
                        tool_name=HOST_SEED_SEARCH_TOOL_NAME,
                        payload={"query": query, "seed_limit": max(1, int(limit_var.get()))},
                        actor="human",
                        source_surface="ui",
                    )
                elif tool_name == HOST_READ_PANELS_TOOL_NAME:
                    command = create_host_command_envelope(
                        tool_name=HOST_READ_PANELS_TOOL_NAME,
                        payload={"mode": "active"},
                        actor="human",
                        source_surface="ui",
                    )
                elif tool_name in {
                    HOST_STATUS_TOOL_NAME,
                    HOST_TOOLS_TOOL_NAME,
                    HOST_BUILDER_SCORE_TOOL_NAME,
                    HOST_PROJECTION_SCORE_TOOL_NAME,
                }:
                    command = create_host_command_envelope(
                        tool_name=tool_name,
                        payload={"history_limit": host_state.history_limit},
                        actor="human",
                        source_surface="ui",
                    )
                else:
                    command = create_host_command_envelope(
                        tool_name=tool_name,
                        payload={"history_limit": host_state.history_limit},
                        actor="human",
                        source_surface="ui",
                    )
                _run_command(command)
            except Exception as exc:
                LOGGER.exception("Host workspace action failed. project_root=%s", settings.project_root)
                status_var.set(f"action failed: {exc}")

        def _promote_active(pinned: bool) -> None:
            if not host_state.active_call_id:
                status_var.set("no active call to promote")
                return
            command = create_host_command_envelope(
                tool_name=HOST_PROMOTE_CALL_TOOL_NAME,
                payload={
                    "call_id": host_state.active_call_id,
                    "pinned": bool(pinned),
                },
                actor="human",
                source_surface="ui",
            )
            _run_command(command)

        def _bridge_tick() -> None:
            nonlocal bridge_session
            try:
                bridge_session = heartbeat_host_bridge_session(settings.project_root, bridge_session.session_id)
                host_state.cache_payload("host_bridge_session", bridge_session.to_dict())
                pending_count = pending_host_bridge_request_count(settings.project_root)
                host_state.cache_payload("host_bridge_pending_count", pending_count)
                responses = process_pending_host_bridge_requests(
                    settings.project_root,
                    host_state,
                    session=bridge_session,
                )
                if responses:
                    latest = responses[-1]
                    host_state.cache_payload("host_bridge_last_response", latest.to_dict())
                    host_state.cache_payload(
                        "host_bridge_pending_count",
                        pending_host_bridge_request_count(settings.project_root),
                    )
                    if latest.tool_name == PROJECT_QUERY_TOOL_NAME:
                        _select_panel("projection")
                    elif latest.tool_name == HOST_SEED_SEARCH_TOOL_NAME:
                        _select_panel("seed")
                    elif latest.tool_name == HOST_HISTORY_VIEW_TOOL_NAME:
                        _select_panel("history")
                    elif latest.tool_name == HOST_COCKPIT_TOOL_NAME:
                        _select_panel("cockpit")
                    elif latest.tool_name == HOST_STATUS_TOOL_NAME:
                        _select_panel("status")
                    elif latest.tool_name == HOST_TOOLS_TOOL_NAME:
                        _select_panel("tools")
                    elif latest.tool_name in {HOST_BUILDER_SCORE_TOOL_NAME, HOST_PROJECTION_SCORE_TOOL_NAME}:
                        _select_panel("scores")
                    elif latest.tool_name == HOST_STREAM_TOOL_NAME:
                        _select_panel("stream")
                    elif latest.tool_name == HOST_READ_PANELS_TOOL_NAME:
                        requested_mode = str((latest.payload or {}).get("mode", "active"))
                        if requested_mode == "panel":
                            requested_panel = str(((latest.payload or {}).get("panel") or {}).get("name", ""))
                            _select_panel(requested_panel or host_state.active_tab)
                        elif requested_mode == "active":
                            _select_panel(str((latest.payload or {}).get("active_tab", host_state.active_tab)))
                        else:
                            _select_panel(host_state.active_tab)
                    else:
                        _select_panel("stream")
                    _render_snapshot()
                else:
                    _update_status()
            except Exception:
                LOGGER.exception("Host bridge poll failed. project_root=%s", settings.project_root)
                status_var.set("host bridge poll failed")
            finally:
                root.after(DEFAULT_HOST_BRIDGE_POLL_INTERVAL_MS, _bridge_tick)

        def _on_close() -> None:
            try:
                close_host_bridge_session(settings.project_root, bridge_session.session_id)
            finally:
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", _on_close)
        run_query_button.configure(command=lambda: _dispatch(PROJECT_QUERY_TOOL_NAME))
        seed_search_button.configure(command=lambda: _dispatch(HOST_SEED_SEARCH_TOOL_NAME))
        promote_button.configure(command=lambda: _promote_active(True))
        demote_button.configure(command=lambda: _promote_active(False))
        refresh_button.configure(command=lambda: _dispatch(HOST_HISTORY_VIEW_TOOL_NAME))
        status_button.configure(command=lambda: _dispatch(HOST_STATUS_TOOL_NAME))
        tools_button.configure(command=lambda: _dispatch(HOST_TOOLS_TOOL_NAME))
        builder_score_button.configure(command=lambda: _dispatch(HOST_BUILDER_SCORE_TOOL_NAME))
        projection_score_button.configure(command=lambda: _dispatch(HOST_PROJECTION_SCORE_TOOL_NAME))

        def _on_tab_changed(_event=None) -> None:
            current_tab = tabs.select()
            panel_name = tab_id_to_name.get(str(current_tab), "stream")
            if panel_name not in HOST_PANEL_ORDER:
                panel_name = "stream"
            host_state.set_active_tab(panel_name)
            if host_state.snapshot is not None:
                _update_status(host_state.snapshot)

        tabs.bind("<<NotebookTabChanged>>", _on_tab_changed)

        host_state.set_active_tab("stream")
        _render_snapshot()
        root.after(DEFAULT_HOST_BRIDGE_POLL_INTERVAL_MS, _bridge_tick)
        LOGGER.info("Host workspace opened. project_root=%s", settings.project_root)
        root.mainloop()
        return 0
    except Exception:
        LOGGER.exception("Host workspace could not be opened. project_root=%s", settings.project_root)
        return 1


def _stream_text(snapshot) -> str:
    lines = [
        "nGraphMANIFOLD Command Stream",
        f"records: {snapshot.record_count}",
        f"history: {snapshot.history_path}",
        (
            "rolling trace: "
            f"{snapshot.retention.get('active_reasoning_count', 'n/a')} active / "
            f"{snapshot.retention.get('durable_evidence_count', 'n/a')} durable / "
            f"limit={snapshot.retention.get('rolling_trace_limit', 'n/a')}"
        ),
        "",
    ]
    if not snapshot.stream_items:
        lines.append("No interaction records yet.")
        return "\n".join(lines)
    for index, item in enumerate(snapshot.stream_items[:8], start=1):
        lines.append(f"[{index}] {item.captured_at} {item.tool_name} status={item.status}")
        lines.append(f"    query: {item.query or '(no query text)'}")
        lines.append(f"    result: {item.response or '(no response summary)'}")
        if item.selected_layer:
            lines.append(
                f"    layer={item.selected_layer} kind={item.selected_kind or 'n/a'} score={item.selected_score}"
            )
        if item.source_ref:
            lines.append(f"    source={item.source_ref}")
        lines.append("")
    return "\n".join(lines)


def _projection_text(snapshot) -> str:
    projection = snapshot.active_projection
    if not projection:
        return "No active projection yet."
    selected = projection.get("selected_candidate") or {}
    flow = projection.get("selected_flow") or {}
    lines = [
        "nGraphMANIFOLD Active Projection",
        f"query: {projection.get('query', 'n/a')}",
        f"selected_layer: {projection.get('selected_layer', 'n/a')}",
        f"selected_kind: {selected.get('kind', 'n/a')}",
        f"selected_score: {selected.get('score', 'n/a')}",
        f"source: {selected.get('source_ref', 'n/a')}",
        "",
        "Layer Summary:",
    ]
    for item in projection.get("layer_summaries", []):
        lines.append(
            f"- {item.get('name', 'n/a')} score={item.get('layer_score', 'n/a')} "
            f"candidates={item.get('candidate_count', 'n/a')}"
        )
    lines.append("")
    lines.append("Selected Flow:")
    for item in flow.get("objects", []):
        lines.append(
            f"- {item.get('role')} rank {item.get('rank')} {item.get('kind')} "
            f"score={item.get('score')}: {item.get('content_preview', '')}"
        )
    if not flow.get("objects"):
        lines.append("- n/a")
    return "\n".join(lines)


def _history_text(snapshot) -> str:
    lines = [
        "nGraphMANIFOLD History Summary",
        f"records: {snapshot.record_count}",
        f"history: {snapshot.history_path}",
        (
            "rolling trace: "
            f"{snapshot.retention.get('active_reasoning_count', 'n/a')} active / "
            f"{snapshot.retention.get('durable_evidence_count', 'n/a')} durable / "
            f"limit={snapshot.retention.get('rolling_trace_limit', 'n/a')}"
        ),
        "",
        "Recent Calls:",
    ]
    if not snapshot.recent_calls:
        lines.append("No persisted calls yet.")
        return "\n".join(lines)
    for call in snapshot.recent_calls[:10]:
        projection = ""
        if call.selected_layer:
            projection = f" selected_layer={call.selected_layer} candidates={call.candidate_count}"
        task = f" task={call.task_id}" if call.task_id else ""
        lines.append(
            f"- {call.captured_at} {call.tool_name} score={call.aggregate_score} "
            f"steps={call.step_count} blockers={call.blocker_count}{projection}{task}"
        )
    return "\n".join(lines)


def _cockpit_text(snapshot) -> str:
    lines = [
        "nGraphMANIFOLD Cockpit",
        "",
        _scores_text(snapshot),
        "",
        "Latest Projection:",
    ]
    projection = snapshot.active_projection or {}
    selected = projection.get("selected_candidate") or {}
    if projection:
        lines.extend(
            [
                f"- query: {projection.get('query', 'n/a')}",
                f"- selected_layer: {projection.get('selected_layer', 'n/a')}",
                f"- selected_kind: {selected.get('kind', 'n/a')}",
                f"- selected_score: {selected.get('score', 'n/a')}",
                f"- source: {selected.get('source_ref', 'n/a')}",
            ]
        )
    else:
        lines.append("- none")
    lines.extend(["", "Latest Seed:"])
    seed = snapshot.active_seed or {}
    selected_seed = seed.get("selected_seed") or {}
    if seed:
        lines.extend(
            [
                f"- query: {seed.get('query', 'n/a')}",
                f"- selected_source: {selected_seed.get('source_ref', 'n/a')}",
                f"- steps: {len((seed.get('traversal_report') or {}).get('steps', []))}",
                f"- blockers: {len((seed.get('traversal_report') or {}).get('blockers', []))}",
            ]
        )
    else:
        lines.append("- none")
    lines.extend(["", "Recent Stream:"])
    if not snapshot.stream_items:
        lines.append("- none")
    for index, item in enumerate(snapshot.stream_items[:6], start=1):
        lines.append(
            f"[{index}] {item.captured_at} {item.tool_name} "
            f"{item.query or '(no query text)'}"
        )
        lines.append(f"    {item.response or '(no response summary)'}")
    return "\n".join(lines)


def _seed_text(snapshot) -> str:
    seed = snapshot.active_seed
    if not seed:
        return "No active seed flow yet."
    selected = seed.get("selected_seed") or {}
    flow = seed.get("selected_flow") or {}
    traversal = seed.get("traversal_report") or {}
    lines = [
        "nGraphMANIFOLD Active Seed Flow",
        f"query: {seed.get('query', 'n/a')}",
        f"candidate_count: {seed.get('candidate_count', 'n/a')}",
        f"selected_source: {selected.get('source_ref', 'n/a')}",
        f"selected_kind: {selected.get('kind', 'n/a')}",
        f"tool: {seed.get('tool_name', 'n/a')}",
        f"steps: {len(traversal.get('steps', []))}",
        f"blockers: {len(traversal.get('blockers', []))}",
        "",
        "Seed Flow:",
    ]
    for item in flow.get("objects", []):
        lines.append(
            f"- {item.get('role')} block {item.get('block_index')} {item.get('kind')}: "
            f"{item.get('content_preview', '')}"
        )
    if not flow.get("objects"):
        lines.append("- n/a")
    return "\n".join(lines)


def _scores_text(snapshot) -> str:
    builder = snapshot.latest_builder_score or {}
    projection = snapshot.latest_projection_score or {}
    builder_report = builder.get("usefulness_report", {})
    projection_report = projection.get("usefulness_report", {})
    lines = [
        "nGraphMANIFOLD Score Summaries",
        f"builder_score: {builder_report.get('aggregate_score', 'n/a')} accepted={builder.get('meets_acceptance', 'n/a')}",
        f"projection_score: {projection_report.get('aggregate_score', 'n/a')} accepted={projection.get('meets_acceptance', 'n/a')}",
        f"history_records: {snapshot.record_count}",
        (
            "rolling_trace: "
            f"{snapshot.retention.get('active_reasoning_count', 'n/a')} active / "
            f"{snapshot.retention.get('durable_evidence_count', 'n/a')} durable"
        ),
        f"raw_cache_keys: {', '.join(sorted(snapshot.raw_payload_cache.keys())) or 'none'}",
    ]
    return "\n".join(lines)


def _add_text_view(parent):
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
    return text


def _write_text(text_widget, payload: str) -> None:
    text_widget.configure(state="normal")
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", payload)
    text_widget.configure(state="disabled")
