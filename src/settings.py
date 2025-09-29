from dataclasses import dataclass
import os
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions


@dataclass
class AppConfig:
    model: str = os.getenv("CLAUDE_MODEL", "opus")
    permission_mode: str | None = os.getenv("PERMISSION_MODE", "acceptEdits")
    cwd: str | None = os.getenv("CWD", None)

    def make_options(self) -> ClaudeAgentOptions:
        return ClaudeAgentOptions(
            model=self.model,
            permission_mode=self.permission_mode,
            cwd=Path(self.cwd) if self.cwd else None,
            setting_sources=None,
        )
