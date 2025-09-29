from typing import Iterable

from claude_agent_sdk import AssistantMessage, TextBlock, ToolResultBlock, ToolUseBlock


def extract_text_blocks(messages: Iterable) -> str:
    chunks: list[str] = []
    for m in messages:
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, TextBlock):
                    chunks.append(b.text)
                elif isinstance(b, ToolUseBlock):
                    chunks.append(f"[tool:{b.name}] → {b.input}")
                elif isinstance(b, ToolResultBlock):
                    chunks.append("[tool:result]")
    return "".join(chunks).strip()
