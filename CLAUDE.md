# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UltraThink** is an MCP (Model Context Protocol) server built with FastMCP framework. The project provides tools that can be consumed by MCP clients.

## Development Commands

### Setup & Dependencies

```bash
# Install dependencies (managed by uv)
uv sync
```

### Task Commands (npm-like)

```bash
# List all tasks
uv run task --list

# Run server
uv run task run

# Run tests with coverage
uv run task test

# Quick tests (no coverage)
uv run task test-quick

# Run test client
uv run task client

# Format code (ruff + prettier)
uv run task format

# Lint code
uv run task lint

# Type check with mypy
uv run task typecheck

# Clean cache
uv run task clean
```

### Direct Commands (Alternative)

**Prefer using `uv run task` commands above.** For direct execution:

```bash
# Run the server directly
uv run ultrathink

# Run the test client directly (connects to server via in-memory transport)
uv run task client
# Or: uv run python examples/client.py
```

This will test all available tools by connecting to the MCP server and calling each tool with sample inputs.

## Architecture

### Project Structure

```
src/ultrathink/                    # Main package
├── models/                        # DATA MODELS
│   ├── thought.py                 # Thought, ThoughtRequest, ThoughtResponse models
│   └── session.py                 # ThinkingSession model
├── services/                      # BUSINESS LOGIC
│   └── thinking_service.py        # UltraThinkService
├── interface/                     # EXTERNAL INTERFACE
│   └── mcp_server.py              # FastMCP server & tool registration
├── __init__.py                    # Package exports
└── __main__.py                    # CLI entry point

tests/                             # Test files (100% coverage, mirroring source structure)
├── models/
│   ├── test_thought.py            # Thought model tests
│   └── test_session.py            # Session logging tests
├── services/
│   └── test_thinking_service.py   # Service validation, functionality, branching, multi-session
├── interface/
│   └── test_mcp_server.py         # MCP tool function tests
└── test_cli.py                    # CLI entry point tests

examples/                          # Example/demo scripts
└── client.py                      # Test harness for the MCP server
```

### Core Structure

- **src/ultrathink/interface/mcp_server.py**: MCP server entry point using FastMCP
  - Define MCP server instance with `FastMCP(name)`
  - Register tools using `@mcp.tool` decorator
  - Imports from services layer

- **src/ultrathink/\_\_main\_\_.py**: CLI entry point
  - Imports `mcp` from `.interface.mcp_server`
  - Defines `main()` function that calls `mcp.run()`
  - Enables `uv run ultrathink` command

- **examples/client.py**: Test harness for the MCP server
  - Uses `Client` from FastMCP for in-memory testing
  - Connects to server via `async with Client(mcp)`
  - Lists and calls tools to verify functionality

### Adding New Tools

Tools are added in `src/ultrathink/interface/mcp_server.py` by decorating functions with `@mcp.tool`:

```python
from ..services.thinking_service import UltraThinkService

@mcp.tool
def tool_name(param: type) -> return_type:
    """Tool description shown to MCP clients"""
    return result
```

The FastMCP framework automatically:

- Converts function signatures to MCP tool schemas
- Handles parameter validation
- Manages STDIO transport for external clients

### Testing Pattern

All tools should be tested:

1. Unit tests organized by layers (mirroring source structure):
   - `tests/models/test_thought.py` - Thought model properties and formatting
   - `tests/models/test_session.py` - Session logging and formatted output
   - `tests/services/test_thinking_service.py` - Service validation, functionality, branching, multi-session
   - `tests/interface/test_mcp_server.py` - MCP tool function tests
   - `tests/test_cli.py` - CLI entry point tests
2. Integration tests via `examples/client.py`:
   - Connect to server using in-memory transport
   - List available tools
   - Call each tool with sample inputs
   - Verify expected outputs

### Imports

When working with the codebase:

```python
# From external code
from ultrathink import mcp, UltraThinkService, Thought

# Within the package (relative imports)
from ..services.thinking_service import UltraThinkService
from ..models.thought import Thought, ThoughtRequest, ThoughtResponse
from ..models.session import ThinkingSession
```

### Session Management

**Important Design Note:** Sessions are stored in-memory only (`UltraThinkService._sessions: dict[str, ThinkingSession]`). This means:

- **Sessions are ephemeral** - all session data is lost when the server restarts
- **No persistence layer** - sessions exist only in memory during server runtime
- **Production consideration** - if persistent sessions are needed, implement custom session storage (disk, database, Redis, etc.)

This design choice keeps the implementation simple and stateless-friendly, but developers should be aware that session continuity across restarts requires additional implementation.

## Dependencies

- **fastmcp**: Framework for building MCP servers with minimal boilerplate
- **mypy**: Type checker configured in strict mode for entire codebase
- Python 3.12+ required (specified in pyproject.toml)

## Code Quality

- **Type Safety**: All code (src, tests, examples) is fully type-checked with mypy in strict mode
- **Coverage**: 100% test coverage maintained across all code
- **Formatting**: Automated with ruff and prettier
- **Linting**: Enforced with ruff

Always run `uv run task typecheck` before committing to ensure type safety.
