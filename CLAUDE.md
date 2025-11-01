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
├── domain/                        # DOMAIN LAYER
│   ├── entities/
│   │   └── thought.py             # Thought entity with validation and behaviors
│   └── aggregates/
│       └── thinking_session.py    # ThinkingSession aggregate root
├── application/                   # APPLICATION LAYER
│   └── services/
│       └── thinking_service.py    # UltraThinkService application service
├── dto/                           # DATA TRANSFER OBJECTS
│   ├── request.py                 # ThoughtRequest DTO
│   └── response.py                # ThoughtResponse DTO
├── infrastructure/                # INFRASTRUCTURE LAYER
│   └── mcp/
│       └── server.py              # FastMCP server & tool registration
├── __init__.py                    # Package exports
└── __main__.py                    # CLI entry point

tests/                             # Test files (100% coverage, mirroring source structure)
├── domain/
│   ├── entities/
│   │   └── test_thought.py        # Thought entity tests
│   └── aggregates/
│       └── test_session_logging.py # Session logging tests
├── application/
│   └── services/
│       └── test_thinking_service.py # Service tests (validation, functionality, branching, multi-session)
├── infrastructure/
│   └── mcp/
│       └── test_server.py         # MCP tool function tests
└── test_cli.py                    # CLI entry point tests

examples/                          # Example/demo scripts
└── client.py                      # Test harness for the MCP server
```

### Core Structure

- **src/ultrathink/infrastructure/mcp/server.py**: MCP server entry point using FastMCP
  - Define MCP server instance with `FastMCP(name)`
  - Register tools using `@mcp.tool` decorator
  - Imports from application service layer

- **src/ultrathink/**main**.py**: CLI entry point
  - Imports `mcp` from `.infrastructure.mcp.server`
  - Defines `main()` function that calls `mcp.run()`
  - Enables `uv run ultrathink` command

- **examples/client.py**: Test harness for the MCP server
  - Uses `Client` from FastMCP for in-memory testing
  - Connects to server via `async with Client(mcp)`
  - Lists and calls tools to verify functionality

### Adding New Tools

Tools are added in `src/ultrathink/infrastructure/mcp/server.py` by decorating functions with `@mcp.tool`:

```python
from ...application.services.thinking_service import UltraThinkService

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

1. Unit tests organized by DDD layers (mirroring source structure):
   - `tests/domain/entities/test_thought.py` - Thought entity properties and formatting
   - `tests/domain/aggregates/test_session_logging.py` - Session logging and formatted output
   - `tests/application/services/test_thinking_service.py` - Service validation, functionality, branching, multi-session
   - `tests/infrastructure/mcp/test_server.py` - MCP tool function tests
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

# Within the package (relative imports following DDD layers)
from ...application.services.thinking_service import UltraThinkService
from ...domain.entities.thought import Thought
from ...domain.aggregates.thinking_session import ThinkingSession
from ...dto.request import ThoughtRequest
from ...dto.response import ThoughtResponse
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
