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
- **DDD Architecture**: Clean domain model with entities, aggregates, and services

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

Built with **Domain-Driven Design (DDD)** principles for clean separation of concerns and maintainable code.

### Files

**src/ultrathink/** (Folder-based DDD structure)

**Domain Layer** (`domain/`)

- **entities/thought.py**: Thought entity with validation and behaviors
- **aggregates/thinking_session.py**: ThinkingSession aggregate root

**Application Layer** (`application/`)

- **services/thinking_service.py**: UltraThinkService application service

**DTO Layer** (`dto/`)

- **request.py**: ThoughtRequest DTO
- **response.py**: ThoughtResponse DTO

**Infrastructure Layer** (`infrastructure/`)

- **mcp/server.py**: MCP server entry point with FastMCP tool registration

**Root Files**

- **\_\_init\_\_.py**: Package exports
- **\_\_main\_\_.py**: CLI entry point (enables `uv run ultrathink`)

**tests/** (100% coverage, mirroring source structure)

**Domain Tests** (`domain/`)

- **entities/test_thought.py**: Thought entity tests (properties, formatting)
- **aggregates/test_session_logging.py**: Session logging and formatting tests

**Application Tests** (`application/`)

- **services/test_thinking_service.py**: Service tests (validation, functionality, branching, multi-session)

**Infrastructure Tests** (`infrastructure/`)

- **mcp/test_server.py**: MCP tool function tests

**Root Test Files**

- **test_cli.py**: CLI entry point tests

**examples/**

- **client.py**: Test client demonstrating tool usage

### DDD Layers

#### 0. Interface DTOs

Pydantic models for request/response validation at the interface boundary:

**ThoughtRequest**: Input DTO from MCP clients with validation
**ThoughtResponse**: Output DTO to MCP clients with structured data

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

#### 1. Entity: `Thought`

The core domain entity representing a single thought with:

**Data:**

- thought text, numbers, metadata
- revision/branch information

**Behaviors:**

- `is_branch`: Check if thought is a branch
- `is_final`: Check if thought is final
- `auto_adjust_total()`: Auto-adjust total thoughts
- `format()`: Format thought for display

```python
thought = Thought(
    thought="My thinking step",
    thought_number=1,
    total_thoughts=3,
    next_thought_needed=True
)
thought.auto_adjust_total()
formatted = thought.format()
```

#### 2. Aggregate Root: `ThinkingSession`

Manages the collection of thoughts and enforces business rules (Pure domain - no protocol knowledge):

**Responsibilities:**

- Maintain thought history
- Track branches
- Enforce domain invariants
- Coordinate logging

**Public Interface:**

- `add_thought(thought)`: Add thought to session
- `thought_count`: Get total thoughts (property)
- `branch_ids`: Get all branch IDs (property)

```python
session = ThinkingSession(disable_logging=False)
session.add_thought(thought)
count = session.thought_count
branches = session.branch_ids
```

#### 3. Application Service: `UltraThinkService`

Orchestrates the thinking process and handles DTO-to-domain translation:

**Responsibilities:**

- **DTO Translation**: `ThoughtRequest → Thought` entity (input)
- **Domain Orchestration**: Delegate to `ThinkingSession`
- **Response Building**: Domain state → `ThoughtResponse` DTO (output)
- **Validation**: Leverages Pydantic for automatic validation

**Key Method:**

- `process_thought(request: ThoughtRequest) → ThoughtResponse`: Main orchestration

```python
service = UltraThinkService()

# Full flow:
# 1. Receives ThoughtRequest DTO from interface layer
# 2. Translates to Thought entity (domain layer)
# 3. Calls session.add_thought() (domain logic)
# 4. Builds ThoughtResponse DTO from domain state
# 5. Returns response DTO
request = ThoughtRequest(thought="...", thought_number=1, ...)
response = service.process_thought(request)
```

**Type Safety Benefits:**

- Pydantic validation on all inputs/outputs
- No arbitrary dicts - strict typing throughout
- Automatic validation errors
- Clear separation between interface and domain layers

### DDD Benefits

1. **Clear Separation of Concerns**:
   - Interface layer (DTOs) = Input/output validation
   - Domain layer (Entity, Aggregate) = Pure business logic
   - Application layer (Service) = DTO translation & orchestration

2. **Domain Logic in Entities**: Business rules live with the data they govern

3. **Testable**: Easy to test entities and aggregates in isolation

4. **Maintainable**:
   - Change interface contract? → Update DTOs & Service only
   - Change business rules? → Update Domain layer only

5. **Extensible**: Easy to add new behaviors to entities

6. **Interface Independence**: Domain can be reused with different interfaces (REST API, gRPC, CLI, etc.)

7. **Defensive Validation**: Both DTO and Entity layers validate independently (defense in depth):
   - `ThoughtRequest` (DTO) validates at the interface boundary for MCP inputs
   - `Thought` (Entity) validates for direct instantiation (tests, future use cases)
   - This ensures entities are self-protecting and don't rely on upstream validation
   - While fields appear duplicated, each layer serves a distinct purpose

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
