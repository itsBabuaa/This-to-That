import streamlit as st
import json
import pandas as pd
from datetime import datetime
from utils.ui import apply_styles
from utils.sidebar import render_sidebar
from utils.history import init_history

apply_styles()
init_history()
render_sidebar()

st.markdown("## Log Visualizer")
st.caption("Upload or paste JSON logs to extract turn latency and tool call metrics. Pure rule-based parsing, no LLM.")

with st.expander("How to read the results", expanded=False):
    st.markdown("""
**Turn Latency Table** — one row per conversation turn:
- **Turn** — turn number from the log
- **Agent** — which agent handled this turn (e.g. reception, sales)
- **User Said** — what the user said (truncated)
- **Turn Latency (ms)** — total time from turn start to next turn start. This is the end-to-end response time the user experiences, including LLM thinking and all tool calls in between
- **Tool Time (ms)** — total execution time of all tools called during this turn
- **LLM Time (ms)** — turn latency minus tool time = pure LLM thinking/generation time
- **Tools Called** — which tools were invoked during this turn
- **State** — state machine transitions (if any)

**Tool Call Details Table** — one row per tool invocation:
- **Turn** — which turn triggered this tool call
- **Tool** — tool name (e.g. emit_event, set_preferred_language)
- **Duration (ms)** — how long the tool took to execute
- **Buffered** — whether the response was buffered
- **Timestamps** — UTC and JST wall clock times
    """)

tab_upload, tab_paste = st.tabs(["Upload Log File", "Paste JSON"])
raw_json = None
source_name = "log"

with tab_upload:
    uploaded = st.file_uploader("Upload a JSON log file", type=["json"], key="log_upload")
    if uploaded:
        raw_json = uploaded.read().decode("utf-8")
        source_name = uploaded.name.rsplit(".", 1)[0]

with tab_paste:
    pasted = st.text_area("Paste JSON log data", height=200, key="log_paste",
                          placeholder='[{"turn": 1, ...}, {"type": "tool_call", ...}]')
    if pasted.strip():
        raw_json = pasted


def _ts(s: str) -> datetime | None:
    """Parse ISO timestamp string to datetime."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _ms_between(t1: datetime | None, t2: datetime | None) -> int:
    if t1 and t2:
        return int((t2 - t1).total_seconds() * 1000)
    return 0


def parse_logs(data: list) -> tuple[list[dict], list[dict]]:
    """
    Rule-based parser. No LLM involved.

    Returns:
        turn_rows: per-turn latency (user message -> next turn start, including tool calls)
        tool_rows: per-tool-call details
    """
    if not isinstance(data, list):
        return [], []

    turn_rows = []
    tool_rows = []

    # First pass: collect turns and tool calls in order
    entries = []  # (type, data) — "turn" or "tool"
    for item in data:
        if isinstance(item, dict):
            if "turn" in item:
                entries.append(("turn", item))
            elif item.get("type") == "tool_call":
                entries.append(("tool", item))

    # Second pass: for each turn, find the last user message timestamp,
    # then find when the system finishes responding (= start of next turn with a new user msg)
    for idx, (etype, entry) in enumerate(entries):
        if etype == "turn":
            turn_num = entry["turn"]
            agent = entry.get("agent", "")
            turn_ts = entry.get("wall_clock", "")
            since_session = entry.get("timing", {}).get("since_session_ms", 0)
            since_prev = entry.get("timing", {}).get("since_prev_ms", 0)
            state_from = entry.get("state_change", {}).get("from", "")
            state_to = entry.get("state_change", {}).get("to", "")

            # Find last user message in this turn's messages
            last_user_ts = None
            user_text = ""
            messages = entry.get("messages", [])
            for msg in messages:
                if msg.get("role") == "user" and not msg.get("prior", False):
                    user_text = msg.get("text", "")
                    last_user_ts = _ts(msg.get("ts", ""))
            # If no non-prior user msg, check the last user msg with prior=true
            if not last_user_ts:
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_text = msg.get("text", "")
                        break

            # Find tool calls that belong to this turn (between this turn and next turn)
            turn_tools = []
            for j in range(idx + 1, len(entries)):
                if entries[j][0] == "tool":
                    turn_tools.append(entries[j][1])
                elif entries[j][0] == "turn":
                    break

            # Calculate turn latency:
            # From this turn's wall_clock to the next turn's wall_clock
            # This captures: LLM thinking + tool calls + everything in between
            turn_start = _ts(turn_ts)
            next_turn_ts = None
            for j in range(idx + 1, len(entries)):
                if entries[j][0] == "turn":
                    next_turn_ts = _ts(entries[j][1].get("wall_clock", ""))
                    break

            # If there are tool calls after this turn, use the last tool call's timestamp + duration
            last_tool_end = None
            if turn_tools:
                last_tool = turn_tools[-1]
                lt_ts = _ts(last_tool.get("wall_clock", ""))
                lt_dur = last_tool.get("duration_ms", 0)
                if lt_ts:
                    from datetime import timedelta
                    last_tool_end = lt_ts + timedelta(milliseconds=lt_dur)

            # Turn latency = time from turn start to whichever comes later:
            # next turn start or last tool end
            turn_latency = 0
            if turn_start and next_turn_ts:
                turn_latency = _ms_between(turn_start, next_turn_ts)
            elif turn_start and last_tool_end:
                turn_latency = _ms_between(turn_start, last_tool_end)

            total_tool_ms = sum(t.get("duration_ms", 0) for t in turn_tools)
            tool_names = ", ".join(t.get("tool", "") for t in turn_tools) if turn_tools else "-"

            turn_rows.append({
                "Turn": turn_num,
                "Agent": agent,
                "User Said": user_text[:80] + ("..." if len(user_text) > 80 else ""),
                "Turn Latency (ms)": turn_latency,
                "Tool Time (ms)": total_tool_ms,
                "LLM Time (ms)": max(0, turn_latency - total_tool_ms),
                "Tools Called": tool_names,
                "Since Session (ms)": since_session,
                "Since Prev (ms)": since_prev,
                "State": f"{state_from} -> {state_to}" if state_to else "",
                "Timestamp": turn_ts,
            })

            # Add tool rows
            for t in turn_tools:
                tool_rows.append({
                    "Turn": turn_num,
                    "Tool": t.get("tool", "unknown"),
                    "Duration (ms)": t.get("duration_ms", 0),
                    "Buffered": t.get("buffered", False),
                    "Timestamp (UTC)": t.get("wall_clock", ""),
                    "Timestamp (JST)": t.get("wall_clock_jst", ""),
                })

    return turn_rows, tool_rows


if raw_json:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        st.stop()

    turn_rows, tool_rows = parse_logs(data)

    if not turn_rows and not tool_rows:
        st.warning("No turns or tool calls found in the log data.")
        st.stop()

    # --- Summary ---
    st.markdown("### Summary")
    df_turns = pd.DataFrame(turn_rows) if turn_rows else pd.DataFrame()
    df_tools = pd.DataFrame(tool_rows) if tool_rows else pd.DataFrame()

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Turns", len(df_turns))
    with m2:
        st.metric("Tool Calls", len(df_tools))
    with m3:
        if not df_turns.empty:
            st.metric("Avg Turn Latency", f"{df_turns['Turn Latency (ms)'].mean():.0f} ms")
        else:
            st.metric("Avg Turn Latency", "-")
    with m4:
        if not df_turns.empty:
            st.metric("Max Turn Latency", f"{df_turns['Turn Latency (ms)'].max()} ms")
        else:
            st.metric("Max Turn Latency", "-")
    with m5:
        if not df_tools.empty:
            st.metric("Unique Tools", df_tools["Tool"].nunique())
        else:
            st.metric("Unique Tools", "0")

    st.divider()

    # --- Turn Latency Table ---
    if not df_turns.empty:
        st.markdown("### Turn Latency")
        st.caption("Time from turn start to next turn (includes LLM thinking + all tool calls)")
        st.dataframe(df_turns, use_container_width=True, hide_index=True)

        # Latency chart
        st.markdown("### Turn Latency Chart")
        chart_df = df_turns[["Turn", "LLM Time (ms)", "Tool Time (ms)"]].set_index("Turn")
        st.bar_chart(chart_df)

    st.divider()

    # --- Tool Call Details ---
    if not df_tools.empty:
        st.markdown("### Tool Call Details")
        tools_filter = ["All"] + sorted(df_tools["Tool"].unique().tolist())
        selected = st.selectbox("Filter by tool", tools_filter)
        filtered = df_tools if selected == "All" else df_tools[df_tools["Tool"] == selected]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    # --- Download ---
    st.divider()
    dl1, dl2 = st.columns(2)
    with dl1:
        if not df_turns.empty:
            st.download_button("Download Turn Latency CSV",
                               df_turns.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"{source_name}_turn_latency.csv", mime="text/csv",
                               use_container_width=True)
    with dl2:
        if not df_tools.empty:
            st.download_button("Download Tool Calls CSV",
                               df_tools.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"{source_name}_tool_calls.csv", mime="text/csv",
                               use_container_width=True)
