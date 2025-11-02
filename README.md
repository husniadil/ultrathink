# UltraThink MCP Server

<div align="center">

**A Python MCP server for sequential thinking and problem-solving**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13.0.2-green.svg)](https://github.com/jlowin/fastmcp)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

> **Enhanced Python port** of the [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) by Anthropic.
> Maintains full compatibility while adding **confidence scoring**, **auto-assigned thought numbers**, and **multi-session support**.

> [!NOTE]
> **Meta**: This MCP server was built iteratively using UltraThink itself - a practical example of the tool's capability to break down complex problems, manage architectural decisions, and maintain context across development sessions.

---

## Features

- **UltraThink**: Break down complex problems into manageable steps
- **Dynamic Adjustments**: Revise and refine thoughts as understanding deepens
- **Branching**: Explore alternative paths of reasoning
- **Confidence Scoring**: Explicit uncertainty tracking (0.0-1.0 scale)
- **Auto-adjustment**: Automatically adjusts total thoughts if needed
- **Multi-Session Support**: Manage multiple concurrent thinking sessions with session IDs
- **Formatted Logging**: Colored terminal output with rich formatting (can be disabled)
- **100% Test Coverage**: Comprehensive test suite with full code coverage
- **Type Safety**: Full mypy strict mode type checking for production code
- **Simple Layered Architecture**: Clean separation with models, services, and interface layers

## Installation

### Quick Install (Recommended)

Run directly with uvx from GitHub (no installation needed):

```bash
uvx --from git+https://github.com/husniadil/ultrathink ultrathink
```

### Development Setup

For local development:

```bash
# Clone the repository
git clone https://github.com/husniadil/ultrathink.git
cd ultrathink

# Install all dependencies (including dev dependencies)
uv sync
```

## Usage

### Task Commands (npm-like)

```bash
# List all available tasks
uv run task --list

# Run the server
uv run task run

# Run tests with coverage
uv run task test

# Run tests without coverage (quick)
uv run task test-quick

# Run the test client
uv run task client

# Format code (ruff + prettier)
uv run task format

# Lint code
uv run task lint

# Type check with mypy
uv run task typecheck

# Clean cache files
uv run task clean
```

### Direct Commands (Alternative)

For direct execution without task runner:

```bash
# Run the server directly
uv run ultrathink

# Run the test client directly
uv run python examples/client.py
```

**Note:** For testing, linting, and formatting, prefer using `uv run task` commands shown above.

## Tool: ultrathink

The server provides a single tool for dynamic and reflective problem-solving through structured thinking.

### Parameters

**Required:**

- `thought` (str): Your current thinking step
- `total_thoughts` (int): Estimated total thoughts needed (>=1)

**Optional:**

- `thought_number` (int): Current thought number - auto-assigned sequentially if omitted (1, 2, 3...), or provide explicit number for branching/semantic control
- `next_thought_needed` (bool): Whether another thought step is needed. Auto-assigned as `thought_number < total_thoughts` if omitted. Set explicitly to override default behavior
- `session_id` (str): Session identifier for managing multiple thinking sessions (None = create new, provide ID to continue session)
- `is_revision` (bool): Whether this revises previous thinking
- `revises_thought` (int): Which thought number is being reconsidered
- `branch_from_thought` (int): Branching point thought number
- `branch_id` (str): Branch identifier
- `needs_more_thoughts` (bool): If more thoughts are needed
- `confidence` (float): Confidence level (0.0-1.0, e.g., 0.7 for 70% confident)
- `uncertainty_notes` (str): Optional explanation for doubts or concerns about this thought
- `outcome` (str): What was achieved or expected as result of this thought

### Response

Returns a JSON object with:

- `session_id`: Session identifier for continuation
- `thoughtNumber`: Current thought number
- `totalThoughts`: Total thoughts (auto-adjusted if needed)
- `nextThoughtNeeded`: Whether more thinking is needed
- `branches`: List of branch IDs
- `thoughtHistoryLength`: Number of thoughts processed in this session
- `confidence`: Confidence level of this thought (0.0-1.0, optional)
- `uncertainty_notes`: Explanation for doubts or concerns (optional)
- `outcome`: What was achieved or expected (optional)

### Example

#### Basic Usage

```python
from fastmcp import Client
from ultrathink.main import mcp

async with Client(mcp) as client:
    # Simple sequential thinking with auto-assigned fields
    result = await client.call_tool("ultrathink", {
        "thought": "Let me analyze this problem step by step",
        "total_thoughts": 3
        # thought_number auto-assigned: 1
        # next_thought_needed auto-assigned: True (1 < 3)
    })
```

#### With Enhanced Features

```python
async with Client(mcp) as client:
    # With confidence scoring and explicit session
    result = await client.call_tool("ultrathink", {
        "thought": "Initial hypothesis - this approach might work",
        "total_thoughts": 5,
        "confidence": 0.6,  # 60% confident
        # next_thought_needed auto-assigned: True
        "session_id": "problem-solving-session-1"
    })

    # Continue the same session with higher confidence
    result2 = await client.call_tool("ultrathink", {
        "thought": "After analysis, I'm more certain about this solution",
        "total_thoughts": 5,
        "confidence": 0.9,  # 90% confident
        # next_thought_needed auto-assigned: True
        "session_id": "problem-solving-session-1"  # Same session
    })

    # Branch from a previous thought
    result3 = await client.call_tool("ultrathink", {
        "thought": "Let me explore an alternative approach",
        "total_thoughts": 6,
        "confidence": 0.7,
        "branch_from_thought": 1,
        "branch_id": "alternative-path",
        # next_thought_needed auto-assigned: True
        "session_id": "problem-solving-session-1"
    })
```

#### With Uncertainty Notes and Outcome

```python
async with Client(mcp) as client:
    # Track uncertainty and outcomes
    result = await client.call_tool("ultrathink", {
        "thought": "Testing the authentication fix",
        "total_thoughts": 5,
        "confidence": 0.8,
        "uncertainty_notes": "Haven't tested under high load yet",
        "outcome": "Login flow works for standard users"
    })

    # Response includes the new fields
    print(result["confidence"])          # 0.8
    print(result["uncertainty_notes"])   # "Haven't tested under high load yet"
    print(result["outcome"])             # "Login flow works for standard users"
```

## Configuration

### Environment Variables

- `DISABLE_THOUGHT_LOGGING`: Set to `"true"` to disable colored thought logging to stderr

### Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

#### Using uvx from GitHub (Recommended)

```json
{
  "mcpServers": {
    "UltraThink": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/husniadil/ultrathink",
        "ultrathink"
      ]
    }
  }
}
```

#### Local Development

For local development from source:

```json
{
  "mcpServers": {
    "UltraThink": {
      "command": "uv",
      "args": ["--directory", "/path/to/ultrathink", "run", "ultrathink"]
    }
  }
}
```

### Local Configuration File

For local development and testing, you can create a `.mcp.json` file (see `.mcp.json.example`):

```bash
# Copy the example file
cp .mcp.json.example .mcp.json

# Edit to match your local path
# Change /path/to/ultrathink to your actual directory
```

Example configuration (`.mcp.json.example`):

```json
{
  "mcpServers": {
    "UltraThink": {
      "command": "uv",
      "args": ["--directory", "/path/to/ultrathink", "run", "ultrathink"],
      "env": {
        "DISABLE_THOUGHT_LOGGING": "false"
      }
    }
  }
}
```

This configuration:

- Enables thought logging by default (`DISABLE_THOUGHT_LOGGING: "false"`)
- Can be used with MCP clients that support `.mcp.json` configuration
- Useful for testing the server locally with colored output enabled
- **Note:** `.mcp.json` is gitignored - customize it for your local setup

## Session Management

### Session Lifecycle

**Important:** Sessions are stored **in-memory only** and will be lost when the server restarts or terminates. Each session is identified by a unique session ID and maintains:

- Thought history for that session
- Branch tracking
- Sequential thought numbering

**Implications:**

- Sessions do not persist across server restarts
- All thinking context is lost when the server stops
- For production use cases requiring persistent sessions, you would need to implement custom session persistence (e.g., to disk, database, or external state management)

**Best Practices:**

- Use custom session IDs (instead of auto-generated UUIDs) for resilient recovery if you need to recreate session context
- Keep session-critical information in your application layer if persistence is required
- Consider sessions as ephemeral working memory for active problem-solving tasks

## Architecture

Built with **Simple Layered Architecture** principles for clean separation of concerns and maintainable code.

### Files

**src/ultrathink/** (3-layer structure)

**Models Layer** (`models/`)

- **thought.py**: Thought, ThoughtRequest, ThoughtResponse models
- **session.py**: ThinkingSession model

**Services Layer** (`services/`)

- **thinking_service.py**: UltraThinkService business logic

**Interface Layer** (`interface/`)

- **mcp_server.py**: MCP server entry point with FastMCP tool registration

**Root Files**

- **\_\_init\_\_.py**: Package exports
- **\_\_main\_\_.py**: CLI entry point (enables `uv run ultrathink`)

**tests/** (100% coverage, mirroring source structure)

**Models Tests** (`models/`)

- **test_thought.py**: Thought model tests (properties, formatting)
- **test_session.py**: Session logging and formatting tests

**Services Tests** (`services/`)

- **test_thinking_service.py**: Service tests (validation, functionality, branching, multi-session)

**Interface Tests** (`interface/`)

- **test_mcp_server.py**: MCP tool function tests

**Root Test Files**

- **test_cli.py**: CLI entry point tests

**examples/**

- **client.py**: Test client demonstrating tool usage

### Architecture Layers

#### 1. Models Layer

Pydantic models for data representation and validation:

**Thought**: Core model representing a single thought with validation and behaviors
**ThoughtRequest**: Input model from MCP clients with validation
**ThoughtResponse**: Output model to MCP clients with structured data
**ThinkingSession**: Session model managing thought history and branches

```python
# Type-safe DTO usage
request = ThoughtRequest(
    thought="My thinking step",
    thought_number=1,
    total_thoughts=3,
    next_thought_needed=True
)
response = ThoughtResponse(
    thought_number=1,
    total_thoughts=3,
    next_thought_needed=True,
    branches=[],
    thought_history_length=1
)
```

#### 2. Services Layer

Business logic and orchestration:

**UltraThinkService**: Orchestrates the thinking process

**Responsibilities:**

- **Model Translation**: `ThoughtRequest → Thought` model (input)
- **Business Logic**: Delegate to `ThinkingSession`
- **Response Building**: Session state → `ThoughtResponse` model (output)
- **Validation**: Leverages Pydantic for automatic validation
- **Session Management**: Create and manage multiple thinking sessions

**Key Method:**

- `process_thought(request: ThoughtRequest) → ThoughtResponse`: Main orchestration

```python
service = UltraThinkService()

# Full flow:
# 1. Receives ThoughtRequest from interface layer
# 2. Translates to Thought model
# 3. Calls session.add_thought() (business logic)
# 4. Builds ThoughtResponse from session state
# 5. Returns response
request = ThoughtRequest(thought="...", thought_number=1, ...)
response = service.process_thought(request)
```

#### 3. Interface Layer

External interface using FastMCP:

**mcp_server.py**: MCP server tool registration

**Responsibilities:**

- Define MCP tools using `@mcp.tool` decorator
- Map tool parameters to model types
- Call services layer for processing
- Return responses to MCP clients

```python
@mcp.tool
def ultrathink(thought: str, total_thoughts: int, ...) -> ThoughtResponse:
    request = ThoughtRequest(thought=thought, total_thoughts=total_thoughts, ...)
    return thinking_service.process_thought(request)
```

**Type Safety Benefits:**

- Pydantic validation on all inputs/outputs
- No arbitrary dicts - strict typing throughout
- Automatic validation errors
- Clear separation between interface and business logic

### Architecture Benefits

1. **Clear Separation of Concerns**:
   - Models layer = Data models with validation and behaviors
   - Services layer = Business logic and orchestration
   - Interface layer = External API (MCP tools)

2. **Simpler Structure**: Flatter folder hierarchy (2 levels instead of 3)

3. **Easier Imports**: Shorter relative import paths (`..models` vs `...domain.entities`)

4. **Consolidated Models**: Related models grouped together (Thought, ThoughtRequest, ThoughtResponse in one file)

5. **Testable**: Easy to test each layer in isolation

6. **Maintainable**:
   - Change interface? → Update interface layer only
   - Change business rules? → Update services layer only
   - Change validation? → Update models layer only

7. **Extensible**: Easy to add new models, services, or tools

8. **Interface Independence**: Services can be reused with different interfaces (REST API, gRPC, CLI, etc.)

9. **Type Safety**: Pydantic models throughout ensure validation at all boundaries

## Development

### Running Tests

```bash
# Run all tests with coverage (recommended)
uv run task test

# Run tests without coverage (quick)
uv run task test-quick

# Coverage is 100%
```

### Type Checking

```bash
# Run mypy type checker on all code
uv run task typecheck

# Mypy runs in strict mode on entire codebase
```

The project uses **mypy in strict mode** across the entire codebase (`src/`, `tests/`, `examples/`) to ensure complete type safety.

### Test Organization

Tests are organized by concern for better maintainability:

**test_server.py**: Validation, functionality, branching, edge cases, response format, reference validation, and multi-session support

**test_thought.py**: Entity properties, auto-adjustment, formatting, validation, and confidence scoring

**test_logging.py**: Formatted logging for regular, revision, and branch thoughts

**test_main.py**: Tool function invocation and CLI entry point

## Credits

This project is a Python port of the [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) by Anthropic, part of the Model Context Protocol servers collection. The original implementation provides the foundation for structured thinking and problem-solving.

## New Features

While maintaining full compatibility with the original design, UltraThink adds several enhancements:

1. **Confidence Scoring** - Explicit uncertainty tracking with 0.0-1.0 scale for each thought
2. **Auto-assigned Thought Numbers** - Optional thought numbering (auto-increments if omitted)
3. **Multi-Session Support** - Manage multiple concurrent thinking sessions with session IDs

## License

[MIT](LICENSE)
