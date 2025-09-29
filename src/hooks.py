from typing import Any

from claude_agent_sdk import HookContext, HookMatcher


async def pre_tool_guard(
    input_data: dict[str, Any], tool_use_id: str | None, ctx: HookContext
) -> dict[str, Any]:
    if input_data.get("tool_name") == "Bash":
        cmd = str(input_data.get("tool_input", {}).get("command", ""))
        if "rm -rf /" in cmd:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Dangerous command blocked",
                }
            }
    return {}


async def pre_tool_log(
    input_data: dict[str, Any], tool_use_id: str | None, ctx: HookContext
) -> dict[str, Any]:
    print(
        f"[PRE] tool={input_data.get('tool_name')} input={input_data.get('tool_input')}"
    )
    return {}


async def post_tool_log(
    input_data: dict[str, Any], tool_use_id: str | None, ctx: HookContext
) -> dict[str, Any]:
    print(f"[POST] tool={input_data.get('tool_name')}")
    return {}


HOOKS = {
    "PreToolUse": [
        HookMatcher(hooks=[pre_tool_log]),
        HookMatcher(matcher="Bash", hooks=[pre_tool_guard]),
    ],
    "PostToolUse": [HookMatcher(hooks=[post_tool_log])],
}
