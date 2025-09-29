# src/app.py
# --- Windows subprocess support (Claude CLI needs Proactor loop on Windows) ---
import sys, asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import asyncio as _asyncio
import shutil, subprocess
import streamlit as st
from dotenv import load_dotenv

from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, _errors
from settings import AppConfig
from tools import utilities_server, ALLOWED_TOOL_NAMES
from hooks import HOOKS

# -------- App setup --------
load_dotenv()
st.set_page_config(page_title="Claude 4.5 Sonnet — Agent WebUI", layout="wide")

# Fixed config: Sonnet 4.5 + acceptEdits + our MCP tools
cfg = AppConfig(model="sonnet", permission_mode="acceptEdits")
OPTIONS = cfg.make_options()
OPTIONS.mcp_servers = {"utils": utilities_server}
OPTIONS.allowed_tools = ["Read", "Write"] + ALLOWED_TOOL_NAMES
OPTIONS.hooks = HOOKS

# -------- Preflight: verify CLI is callable in THIS process (claude) --------
CLI_CANDIDATES = ["claude", "claude-code"]  # try 'claude' first, then fallback

def preflight_cli() -> str:
    """
    Return the resolved CLI command ('claude' or 'claude-code') verified with --version.
    Stop the app with a helpful error if neither works.
    """
    for cmd in CLI_CANDIDATES:
        path_hint = shutil.which(cmd)
        if not path_hint:
            continue
        try:
            out = subprocess.run([cmd, "--version"], capture_output=True, text=True, check=True)
            ver = (out.stdout or out.stderr).strip()
            st.caption(f"CLI OK: {cmd} — {ver} @ {path_hint}")
            return cmd
        except Exception:
            # found on PATH but couldn't execute; try next candidate
            continue

    # Neither worked
    st.error(
        "Claude CLI not found/usable by this process.\n\n"
        "Fix:\n"
        "1) Install:  npm i -g @anthropic-ai/claude-code\n"
        "2) Ensure the global npm bin (often %APPDATA%\\npm on Windows) is on PATH for this conda/venv.\n"
        "3) Verify in the SAME terminal:\n"
        "     claude --version   (preferred)\n"
        "  or claude-code --version\n"
        "4) Re-run: streamlit run src/app.py\n"
    )
    st.stop()

RESOLVED_CLI = preflight_cli()

# If your SDK supports steering the CLI name/path, you can pass it:
# (leave commented unless your claude-agent-sdk version documents this)
# OPTIONS.extra_args = {"cliCommand": RESOLVED_CLI}

# -------- Session state --------
if "client" not in st.session_state:
    st.session_state.client = None        # type: ClaudeSDKClient | None
    st.session_state.history = []         # list[tuple[str, str]]
    st.session_state.busy = False

def _connect_new_client():
    c = ClaudeSDKClient(options=OPTIONS)
    _asyncio.run(c.connect())
    return c

def ensure_client():
    if st.session_state.client is None:
        try:
            st.session_state.client = _connect_new_client()
        except _errors.CLINotFoundError:
            st.error("Claude CLI not found at runtime. Ensure 'claude' (or 'claude-code') is on PATH.")
            st.stop()
        except _errors.CLIConnectionError as e:
            st.error("Failed to start Claude CLI subprocess. Run Streamlit from the same terminal where "
                     f"`{RESOLVED_CLI} --version` works.\n\n{e}")
            st.stop()

def reconnect_client():
    try:
        if st.session_state.client is not None:
            _asyncio.run(st.session_state.client.disconnect())
    except Exception:
        pass
    st.session_state.client = None
    ensure_client()

def send_with_retry(prompt: str) -> bool:
    """
    Send a prompt. If stdin is broken (CLI died), reconnect once and retry.
    """
    for attempt in (1, 2):
        try:
            _asyncio.run(st.session_state.client.query(prompt))
            return True
        except _errors.CLIConnectionError as e:
            if attempt == 1:
                reconnect_client()
                continue
            st.error(f"Claude CLI connection failed twice.\n\nLast error:\n{e}")
            return False
        except Exception as e:
            st.error(f"Unexpected error while sending to Claude:\n{e}")
            return False
    return False

def stream_response() -> str:
    """Stream assistant messages; return accumulated text."""
    buf: list[str] = []
    placeholder = st.empty()

    async def _run():
        async for msg in st.session_state.client.receive_response():
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock):
                        buf.append(b.text)
                        placeholder.markdown("".join(buf))

    _asyncio.run(_run())
    return "".join(buf)

# -------- UI --------
st.title("Claude 4.5 — Sonnet · Python Agent SDK (WebUI)")

# Render history
for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

prompt = st.chat_input("Type a message…")

if prompt and not st.session_state.busy:
    st.session_state.busy = True
    try:
        ensure_client()

        # show user message
        st.session_state.history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        # send (with reconnect retry)
        ok = send_with_retry(prompt)
        with st.chat_message("assistant"):
            if ok:
                text = stream_response()
                st.session_state.history.append(("assistant", text))
            else:
                st.markdown("_No reply due to CLI error (see above)._")
    finally:
        st.session_state.busy = False

# Minimal top control (no sidebar)
if st.button("🔄 New Session"):
    try:
        if st.session_state.client is not None:
            _asyncio.run(st.session_state.client.disconnect())
    except Exception:
        pass
    st.session_state.client = None
    st.session_state.history = []
    st.rerun()
