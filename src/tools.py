from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server


@tool("calculate", "Evaluate a safe math expression", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    import re

    expr = args["expression"]
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
        return {
            "content": [{"type": "text", "text": "Invalid expression"}],
            "is_error": True,
        }
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return {"content": [{"type": "text", "text": f"Result: {result}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}], "is_error": True}


@tool("now", "Return current timestamp", {})
async def now(args: dict[str, Any]) -> dict[str, Any]:
    from datetime import datetime

    return {"content": [{"type": "text", "text": datetime.now().isoformat()}]}


utilities_server = create_sdk_mcp_server(
    name="utilities", version="1.0.0", tools=[calculate, now]
)

ALLOWED_TOOL_NAMES = [
    "mcp__utilities__calculate",
    "mcp__utilities__now",
]
