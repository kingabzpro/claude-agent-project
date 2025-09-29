# Claude Agent SDK Tutorial Projects

This repository contains three progressive tutorial projects demonstrating the Claude Agent SDK, from simple one-shot queries to advanced multi-tool applications.

## Prerequisites

- Python 3.10+
- Node.js 18+ (required by Claude Code CLI)
- Claude Code CLI installed and configured
- Claude API access

## Installation

### 1. Install Claude Code CLI

**For Windows:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**For other platforms:**
```bash
npm i -g @anthropic-ai/claude-code
```

### 2. Install Python SDK

```bash
pip install claude-agent-sdk
```

### 3. Install project dependencies

```bash
pip install -r requirements.txt
```

## Tutorial Flow

### 🟢 Easy: One-shot Blog Outline

**Project**: `blog_outline/oneshot_outline.py`

A simple one-shot query that demonstrates basic Claude Agent SDK usage without tools.

```bash
python blog_outline\oneshot_outline.py
```

**What you'll learn:**
- Basic SDK setup with `ClaudeAgentOptions`
- Simple async query execution
- Message streaming and text extraction
- No tools required - pure AI response

**Key concepts:**
- `query()` function for one-shot interactions
- `AssistantMessage` and `TextBlock` handling
- Async/await patterns

---

### 🟡 Medium: InspireBot CLI

**Project**: `inspire_me/inspire_web.py`

A CLI tool that combines web search with a custom fallback tool for motivational quotes.

```bash
python inspire_me\inspire_web.py
python inspire_me\inspire_web.py "women in leadership"  # with custom topic
```

**What you'll learn:**
- Custom tool creation with `@tool` decorator
- MCP server setup with `create_sdk_mcp_server`
- Tool fallback strategies (WebSearch → custom tool)
- Terminal UI enhancements (typewriter effect, colors)
- Tool usage visualization

**Key concepts:**
- Custom tool definition and implementation
- MCP server configuration
- `allowed_tools` and `mcp_servers` options
- Tool execution flow and result handling
- CLI argument parsing

---

### 🔴 Advanced: NoteSmith Multi-Tool App

**Project**: `note_smith/app.py`

A comprehensive notes application with multiple tools, safety hooks, and usage tracking.

```bash
python note_smith\app.py
```

**Commands:**
- `/summarize <url>` - Summarize web pages
- `/note <text>` - Save notes locally
- `/find <pattern>` - Search saved notes
- `/help` - Show available commands
- `/exit` - Quit the application

**What you'll learn:**
- Multi-tool applications with built-in and custom tools
- Safety hooks with `HookMatcher` and `HookContext`
- Persistent data storage (local file system)
- Interactive CLI with command parsing
- Usage tracking and cost monitoring
- Error handling and graceful degradation

**Key concepts:**
- `ClaudeSDKClient` for persistent sessions
- Multiple custom tools working together
- File system operations and data persistence
- Safety mechanisms to prevent dangerous operations
- Usage statistics and cost tracking
- Interactive application patterns

## Project Structure

```
├── blog_outline/
│   └── oneshot_outline.py     # Simple one-shot query
├── inspire_me/
│   └── inspire_web.py         # CLI with web search + custom tool
├── note_smith/
│   ├── app.py                 # Multi-tool notes application
│   └── notes/                 # Generated notes storage
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Key SDK Features Demonstrated

### Core SDK Components
- **`ClaudeAgentOptions`** - Configuration for model, system prompts, and tools
- **`query()`** - One-shot interactions
- **`ClaudeSDKClient`** - Persistent client for interactive applications

### Tool System
- **`@tool`** - Decorator for custom tool definition
- **`create_sdk_mcp_server`** - MCP server creation
- **Built-in tools** - WebSearch, WebFetch, Read, Write, etc.

### Safety & Control
- **`HookMatcher`** - Tool execution hooks
- **`permission_mode`** - Tool execution permissions
- **`allowed_tools`** - Tool whitelisting

### Message Handling
- **`AssistantMessage`** - AI responses
- **`TextBlock`** - Text content
- **`ToolUseBlock`** - Tool execution requests
- **`ToolResultBlock`** - Tool execution results
- **`ResultMessage`** - Final results with usage stats

## Learning Path

1. **Start with Easy**: Understand basic SDK patterns and async programming
2. **Move to Medium**: Learn tool creation and MCP server setup
3. **Master Advanced**: Build complex applications with multiple tools and safety features

Each project builds upon the previous one, introducing new concepts while reinforcing core patterns.

## Troubleshooting

- Ensure Claude Agent CLI is properly configured
- Check that your Claude API key has sufficient credits
- Verify Python version compatibility (3.8+)
- For NoteSmith, ensure write permissions in the project directory

## Next Steps

After completing these tutorials, you'll be ready to:
- Build custom tools for your specific use cases
- Create interactive CLI applications
- Implement safety mechanisms for production use
- Design multi-tool workflows
- Handle complex message streaming patterns

Happy building! 🚀
