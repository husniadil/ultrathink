# UltraThink

A Python MCP (Model Context Protocol) server for sequential thinking and problem-solving, built with FastMCP.

This is a Python port of the [TypeScript sequential thinking MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) with 100% feature parity, renamed to "UltraThink".

## Features

- **UltraThink**: Break down complex problems into manageable steps
- **Dynamic Adjustments**: Revise and refine thoughts as understanding deepens
- **Branching**: Explore alternative paths of reasoning
- **Confidence Scoring**: Explicit uncertainty tracking (0.0-1.0 scale)
- **Auto-adjustment**: Automatically adjusts total thoughts if needed
- **Formatted Logging**: Colored terminal output with rich formatting (can be disabled)
- **100% Test Coverage**: Comprehensive test suite with 41 test cases
- **Type Safety**: Full mypy strict mode type checking for production code
- **DDD Architecture**: Clean domain model with entities, aggregates, and services

## Installation

```bash
# Install all dependencies (including dev dependencies)
uv sync

# Or install manually
uv add fastmcp==2.13.0.2 rich==14.2.0
uv add --dev pytest==8.4.2 pytest-cov==7.0.0 taskipy==1.14.1 mypy>=1.18.2
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
- `thought_number` (int): Current thought number (>=1)
- `total_thoughts` (int): Estimated total thoughts needed (>=1)
- `next_thought_needed` (bool): Whether another thought step is needed

**Optional:**

- `is_revision` (bool): Whether this revises previous thinking
- `revises_thought` (int): Which thought number is being reconsidered
- `branch_from_thought` (int): Branching point thought number
- `branch_id` (str): Branch identifier
- `needs_more_thoughts` (bool): If more thoughts are needed
- `confidence` (float): Confidence level (0.0-1.0, e.g., 0.7 for 70% confident)

### Response

Returns a JSON object with:

- `thoughtNumber`: Current thought number
- `totalThoughts`: Total thoughts (auto-adjusted if needed)
- `nextThoughtNeeded`: Whether more thinking is needed
- `branches`: List of branch IDs
- `thoughtHistoryLength`: Number of thoughts processed
- `confidence`: Confidence level of this thought (0.0-1.0, optional)

### Example

```python
from fastmcp import Client
from ultrathink.main import mcp

async with Client(mcp) as client:
    result = await client.call_tool("ultrathink", {
        "thought": "I need to solve this problem step by step",
        "thought_number": 1,
        "total_thoughts": 3,
        "next_thought_needed": True
    })
```

## Configuration

### Environment Variables

- `DISABLE_THOUGHT_LOGGING`: Set to `"true"` to disable colored thought logging to stderr

### Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ultrathink": {
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
    "ultrathink": {
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

## Architecture

Built with **Domain-Driven Design (DDD)** principles for clean separation of concerns and maintainable code.

### Files

**src/ultrathink/**

- \***\*init**.py\*\*: Package exports
- \***\*main**.py\*\*: CLI entry point (enables `uv run ultrathink`)
- **main.py**: MCP server entry point with FastMCP tool registration
- **dto.py**: Interface DTOs (ThoughtRequest, ThoughtResponse)
- **thought.py**: Thought entity with validation and behaviors
- **session.py**: ThinkingSession aggregate root
- **service.py**: UltraThinkService application service

**tests/** (35 tests, 100% coverage)

- **test_server.py**: Server tests (validation, functionality, branching)
- **test_thought.py**: Thought entity tests (properties, formatting)
- **test_logging.py**: Logging and formatting tests
- **test_main.py**: Main entry point and MCP server tests

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

**test_server.py** (25 tests)

- Validation (10 tests): Parameter validation and error handling (including confidence range)
- Functionality (5 tests): Core features and thought tracking (including confidence scoring)
- Branching (2 tests): Alternative reasoning paths
- Edge Cases (5 tests): Boundary conditions
- Response Format (3 tests): Output structure validation

**test_thought.py** (11 tests)

- Entity Properties (2 tests): is_final, is_branch properties
- Auto-adjustment (2 tests): Total thoughts adjustment logic
- Formatting (4 tests): Visual output for regular, revision, branch, and confidence display
- Validation (1 test): Whitespace-only thought rejection
- Confidence (2 tests): Confidence field validation and defaults

**test_logging.py** (3 tests)

- Formatted logging for regular, revision, and branch thoughts

**test_main.py** (2 tests)

- Tool function invocation
- CLI entry point

## Differences from TypeScript Version

While maintaining 100% feature parity, the Python version uses:

- **Pydantic** for validation instead of manual type checking
- **Rich** for colored output instead of chalk
- **pytest** for testing instead of vitest
- **FastMCP** decorator pattern for tool registration
- **Strict mode** in Pydantic to prevent type coercion
- **DDD Architecture**:
  - Interface DTOs for validation (`ThoughtRequest`, `ThoughtResponse`)
  - Entities (`Thought`) with behaviors
  - Aggregate Root (`ThinkingSession`) for domain logic
  - Application Service (`UltraThinkService`) for orchestration
  - Pure domain layer with no interface dependencies

## License

MIT
