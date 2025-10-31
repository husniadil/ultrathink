# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ultrathink** is an MCP (Model Context Protocol) server built with FastMCP framework. The project provides tools that can be consumed by MCP clients.

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
src/ultrathink/          # Main package
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── main.py              # FastMCP server & tool registration
├── dto.py               # Interface DTOs (ThoughtRequest, ThoughtResponse)
├── thought.py           # Thought entity with validation and behaviors
├── session.py           # ThinkingSession aggregate root
└── service.py           # UltraThinkService application service

tests/                   # Test files (35 tests, 100% coverage)
├── test_server.py       # Server tests (validation, functionality, branching)
├── test_thought.py      # Thought entity tests (properties, formatting)
├── test_logging.py      # Logging and formatting tests
└── test_main.py         # Main entry point and MCP server tests

examples/                # Example/demo scripts
└── client.py            # Test harness for the MCP server
```

### Core Structure

- **src/ultrathink/main.py**: MCP server entry point using FastMCP
  - Define MCP server instance with `FastMCP(name)`
  - Register tools using `@mcp.tool` decorator
  - Import from `.server` module

- **src/ultrathink/**main**.py**: CLI entry point
  - Imports `mcp` from `.main`
  - Defines `main()` function that calls `mcp.run()`
  - Enables `uv run ultrathink` command

- **examples/client.py**: Test harness for the MCP server
  - Uses `Client` from FastMCP for in-memory testing
  - Connects to server via `async with Client(mcp)`
  - Lists and calls tools to verify functionality

### Adding New Tools

Tools are added in `src/ultrathink/main.py` by decorating functions with `@mcp.tool`:

```python
from .service import UltraThinkService

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

1. Unit tests (35 tests organized by concern):
   - `tests/test_server.py` - Server validation, functionality, branching (22 tests)
   - `tests/test_thought.py` - Thought entity properties and formatting (8 tests)
   - `tests/test_logging.py` - Logging and formatted output (3 tests)
   - `tests/test_main.py` - Main entry point and CLI (2 tests)
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
from .service import UltraThinkService
from .thought import Thought
```

## Dependencies

- **fastmcp**: Framework for building MCP servers with minimal boilerplate
- **mypy**: Type checker configured in strict mode for entire codebase
- Python 3.12+ required (specified in pyproject.toml)

## Code Quality

- **Type Safety**: All code (src, tests, examples) is fully type-checked with mypy in strict mode
- **Coverage**: 100% test coverage across 35 tests
- **Formatting**: Automated with ruff and prettier
- **Linting**: Enforced with ruff

Always run `uv run task typecheck` before committing to ensure type safety.
