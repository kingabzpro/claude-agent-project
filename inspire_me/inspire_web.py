import sys
import json
import asyncio
import random
import time
from typing import Any

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    ResultMessage,
)

# -------------------------
# Custom fallback tool
# -------------------------
QUOTES = [
    "Dream big, start small — but start.",
    "Stay curious, stay humble, keep building.",
    "Every expert was once a beginner.",
    "Small wins stack into big victories.",
    "Consistency beats intensity when intensity is inconsistent.",
]

@tool("inspire_me", "Return a random motivational quote", {})
async def inspire_me(_: dict) -> dict:
    return {"content": [{"type": "text", "text": random.choice(QUOTES)}]}

UTILS = create_sdk_mcp_server("inspire_util", "1.0.0", [inspire_me])

# -------------------------
# Tiny terminal helpers
# -------------------------
def is_tty() -> bool:
    try:
        return sys.stdout.isatty()
    except Exception:
        return False

def typewrite(text: str, delay: float = 0.02) -> None:
    """Print with a typewriter effect if TTY; otherwise plain print."""
    if not is_tty():
        print(text)
        return
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def faint(s: str) -> str:
    """Dim text if terminal supports ANSI."""
    return s if not is_tty() else f"\033[2m{s}\033[0m"

def bold(s: str) -> str:
    return s if not is_tty() else f"\033[1m{s}\033[0m"

# -------------------------
# Main
# -------------------------
async def main():
    topic = "engineering focus" if len(sys.argv) < 2 else " ".join(sys.argv[1:])

    options = ClaudeAgentOptions(
        model="sonnet",  # switch to "sonnet-4.5" if your CLI lists it
        system_prompt=(
            "You are InspireBot.\n"
            "- First, try WebSearch to find a short, uplifting quote relevant to the user's topic.\n"
            "- If WebSearch is unhelpful or no clear quote is found, call the custom 'inspire_me' tool.\n"
            "- Output ONE short line only. No preface, no commentary, <= 120 characters."
        ),
        allowed_tools=[
            "WebSearch",
            "mcp__inspire_util__inspire_me",
        ],
        mcp_servers={"inspire_util": UTILS},
    )

    prompt = (
        "Find a short, uplifting quote for today's inspiration. "
        f"Topic: {topic}. Prefer something crisp and modern.\n"
        "If search yields multiple options, pick the best single line."
    )

    final_line_parts: list[str] = []

    if is_tty():
        print(bold("🌐 InspireBot (WebSearch + fallback tool)"))
        print(faint("Tip: pass a custom topic:  python inspire_web_animated.py \"women in leadership\""))
        print()

    async for message in query(prompt=prompt, options=options):
        # Stream assistant messages for tool usage + final text
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tool_name = block.name
                    tool_input = block.input or {}
                    print(f"{bold('🛠️  Tool used:')} {tool_name}")
                    print(f"{faint('   input:')} {json.dumps(tool_input, ensure_ascii=False)}")
                elif isinstance(block, ToolResultBlock):
                    # Show summarized tool result text if present
                    shown = False
                    if isinstance(block.content, list):
                        for part in block.content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text = (part.get("text") or "").strip()
                                if text:
                                    preview = text if len(text) <= 200 else (text[:197] + "…")
                                    print(f"{faint('   result:')} {preview}")
                                    shown = True
                                    break
                    if not shown:
                        print(f"{faint('   result:')} (no textual content)")
                elif isinstance(block, TextBlock):
                    # This should be the final “inspiration” line content
                    final_line_parts.append(block.text)

        elif isinstance(message, ResultMessage):
            # allow the iterator to finish naturally (no break)
            pass

    final_line = " ".join(part.strip() for part in final_line_parts).strip()
    if not final_line:
        final_line = random.choice(QUOTES)  # ultimate fallback, just in case

    # Animate the final line (typewriter), or plain if not a TTY
    typewrite(final_line, delay=0.02)

if __name__ == "__main__":
    asyncio.run(main())
