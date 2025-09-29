import asyncio

import streamlit as st
from claude_agent_sdk import AssistantMessage, ClaudeSDKClient, TextBlock
from dotenv import load_dotenv

from hooks import HOOKS
from settings import AppConfig
from tools import ALLOWED_TOOL_NAMES, utilities_server

load_dotenv()
st.set_page_config(page_title="Claude 4.5 Agent WebUI", layout="wide")

# --- Sidebar controls ---
st.sidebar.title("Claude 4.5 Agent")
model = st.sidebar.selectbox("Model", ["opus", "sonnet", "haiku"], index=0)
perm = st.sidebar.selectbox(
    "Permission Mode", ["acceptEdits", "default", "plan", "bypassPermissions"], index=0
)
use_tools = st.sidebar.multiselect(
    "Allowed tools",
    ["Read", "Write", "Bash"] + ALLOWED_TOOL_NAMES,
    default=["Read", "Write"] + ALLOWED_TOOL_NAMES,
)

# Prepare options for this run
cfg = AppConfig(model=model, permission_mode=perm)
OPTIONS = cfg.make_options()
OPTIONS.mcp_servers = {"utils": utilities_server}
OPTIONS.allowed_tools = use_tools
OPTIONS.hooks = HOOKS

if "client" not in st.session_state:
    st.session_state.client = ClaudeSDKClient(options=OPTIONS)
    # connect once per session
    asyncio.run(st.session_state.client.connect())
    st.session_state.history = []  # [(role, text)]

st.title("Claude 4.5 — Python Agent SDK (WebUI)")

# Render history
for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

prompt = st.chat_input("Type a message…")


def render_assistant_stream():
    buf = []
    placeholder = st.empty()

    async def _run():
        async for msg in st.session_state.client.receive_response():
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock):
                        buf.append(b.text)
                        placeholder.markdown("".join(buf))

    asyncio.run(_run())
    return "".join(buf)


if prompt:
    # Send user message
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Query Claude with streaming response
    async def _query():
        await st.session_state.client.query(prompt)

    asyncio.run(_query())

    with st.chat_message("assistant"):
        text = render_assistant_stream()
    st.session_state.history.append(("assistant", text))

# Utilities row
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 New Session"):

        async def _reset():
            await st.session_state.client.disconnect()
            st.session_state.client = ClaudeSDKClient(options=OPTIONS)
            await st.session_state.client.connect()

        asyncio.run(_reset())
        st.session_state.history = []
        st.rerun()
with col2:
    st.caption("Tools active: " + ", ".join(OPTIONS.allowed_tools))
