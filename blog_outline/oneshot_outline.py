import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)

PROMPT = """Create a crisp markdown outline (H2/H3 bullets) for a 500-word blog post:
Title: Why Sovereign AI Compute Matters in 2026
Audience: CTOs and Heads of AI
Tone: pragmatic, non-hype
Include: 3 buyer pains, 3 evaluation criteria, 1 closing CTA
"""

async def main():
    options = ClaudeAgentOptions(
        model="sonnet",  # use "sonnet-4.5" if your CLI shows it as available
        system_prompt="You are a precise technical copy strategist."
    )

    async for msg in query(prompt=PROMPT, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="")  # only the outline
        elif isinstance(msg, ResultMessage):
            pass  # let the iterator end naturally

if __name__ == "__main__":
    asyncio.run(main())
