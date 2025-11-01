from typing import Annotated
from pydantic import Field
from fastmcp import FastMCP
from .service import UltraThinkService
from .dto import ThoughtRequest, ThoughtResponse

mcp = FastMCP("UltraThink")

thinking_service = UltraThinkService()


@mcp.tool
def ultrathink(
    thought: Annotated[
        str, Field(min_length=1, description="Your current thinking step")
    ],
    total_thoughts: Annotated[
        int,
        Field(
            ge=1,
            description="Estimated total thoughts needed (numeric value, e.g., 3, 5, 10)",
        ),
    ],
    next_thought_needed: Annotated[
        bool | None,
        Field(
            None,
            description="Whether another thought step is needed (auto: true if thought_number < total_thoughts)",
        ),
    ] = None,
    thought_number: Annotated[
        int | None,
        Field(
            None,
            ge=1,
            description="Current thought number (auto-assigned if omitted, or provide explicit number for branching/semantic control)",
        ),
    ] = None,
    session_id: Annotated[
        str | None,
        Field(None, description="Session identifier (None = create new session)"),
    ] = None,
    is_revision: Annotated[
        bool | None, Field(None, description="Whether this revises previous thinking")
    ] = None,
    revises_thought: Annotated[
        int | None, Field(None, ge=1, description="Which thought is being reconsidered")
    ] = None,
    branch_from_thought: Annotated[
        int | None, Field(None, ge=1, description="Branching point thought number")
    ] = None,
    branch_id: Annotated[
        str | None, Field(None, description="Branch identifier")
    ] = None,
    needs_more_thoughts: Annotated[
        bool | None, Field(None, description="If more thoughts are needed")
    ] = None,
    confidence: Annotated[
        float | None,
        Field(
            None,
            ge=0.0,
            le=1.0,
            description="Confidence level (0.0-1.0, e.g., 0.7 for 70% confident)",
        ),
    ] = None,
    uncertainty_notes: Annotated[
        str | None,
        Field(
            None,
            description="Optional explanation for uncertainty or doubts about this thought",
        ),
    ] = None,
    outcome: Annotated[
        str | None,
        Field(
            None,
            description="What was achieved or expected as result of this thought",
        ),
    ] = None,
) -> ThoughtResponse:
    """
    A detailed tool for dynamic and reflective problem-solving through thoughts.
    This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
    Each thought can build on, question, or revise previous insights as understanding deepens.

    IMPORTANT: You MUST use this tool proactively for complex reasoning tasks requiring multi-step analysis.

    When to use this tool:
    - Breaking down complex problems into steps (>3 steps of reasoning required)
    - Planning and design with room for revision
    - Analysis that might need course correction
    - Problems where the full scope might not be clear initially
    - Problems that require a multi-step solution
    - Tasks that need to maintain context over multiple steps
    - Situations where irrelevant information needs to be filtered out
    - Architecture decisions with multiple trade-offs
    - Algorithm design and optimization problems
    - Debugging multi-layered issues

    DO NOT use this tool for:
    - Simple one-step answers or direct lookups
    - Straightforward code edits without complex logic
    - Basic file operations or searches
    - Tasks that are already clear and unambiguous
    - Simple factual questions with direct answers

    Parameters explained:
    - thought: Your current thinking step, which can include:
      * Regular analytical steps
      * Revisions of previous thoughts
      * Questions about previous decisions
      * Realizations about needing more analysis
      * Changes in approach
      * Hypothesis generation
      * Hypothesis verification
    - next_thought_needed: Optional - auto-assigned as (thought_number < total_thoughts) if omitted. Set explicitly to override (e.g., True to extend beyond total_thoughts, False to end early)
    - thought_number: Current number in sequence - auto-assigned sequentially if omitted (1, 2, 3...), or provide explicit number for branching/semantic control
    - total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
    - session_id: Optional session identifier for managing multiple thinking sessions
      * None (default): Creates a new session with auto-generated UUID
      * Provide a session_id from previous response: Continue that thinking session
      * Provide a custom string: Create or resume session with that ID (resilient recovery)
    - is_revision: A boolean indicating if this thought revises previous thinking
    - revises_thought: If is_revision is true, which thought number is being reconsidered
    - branch_from_thought: If branching, which thought number is the branching point
    - branch_id: Identifier for the current branch (if any)
    - needs_more_thoughts: If reaching end but realizing more thoughts needed
    - confidence: Optional confidence level (0.0-1.0) expressing certainty about this thought
    - uncertainty_notes: Optional explanation for doubts or concerns (complements confidence score)
    - outcome: What was achieved or expected as result of this thought

    Example usage:

    Thought 1 (confidence: 0.6): "I need to design a caching strategy. Let me first consider the access patterns..."
    Thought 2 (confidence: 0.7): "Based on access patterns, I see two viable approaches: LRU or LFU..."
    Thought 3 (revision of 2, confidence: 0.75): "Wait, I should also consider TTL-based expiration..."
    Thought 4 (branch from 2, confidence: 0.8): "Let me explore a hybrid approach combining LRU with TTL..."
    Thought 5 (confidence: 0.95): "The hybrid approach addresses both requirements. Final recommendation: ..."

    Usage guide:
    1. Start with an initial estimate of needed thoughts, be ready to adjust total_thoughts as you progress
    2. Question or revise previous thoughts using is_revision=true and revises_thought parameters
    3. Explore alternative reasoning paths using branch_from_thought and branch_id parameters
    4. Add more thoughts if needed, even after reaching what seemed like the end
    5. Manage sessions for context continuity:
       - First call: Omit session_id (or set to None) to create new session
       - Subsequent calls: Use session_id from response to continue the same session
       - Multiple problems: Use different session_ids for separate thinking contexts
       - Resilient recovery: Reuse the same custom session_id across reconnections
    6. Express uncertainty using the confidence parameter (0.0=very uncertain, 1.0=very certain)
       - Low confidence (0.3-0.6): Exploratory thinking, initial hypotheses, uncertain analysis
       - Medium confidence (0.6-0.8): Reasoned analysis, likely conclusions, working hypotheses
       - High confidence (0.8-1.0): Verified solutions, confident conclusions, proven facts
    7. Clearly state what you're analyzing or deciding in each thought
    8. Ignore information that is irrelevant to the current step
    9. Generate solution hypotheses as you develop understanding
    10. Verify hypotheses through subsequent thinking steps
    11. Repeat the process until you reach a satisfactory solution
    12. Provide a single, ideally correct answer as the final output
    13. The next_thought_needed parameter is auto-assigned based on progress (thought_number < total_thoughts). Only set it explicitly when you need to override the default behavior (e.g., to extend thinking beyond the initial estimate or to end early)
    """
    # Construct ThoughtRequest from flat parameters
    request = ThoughtRequest(
        thought=thought,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        next_thought_needed=next_thought_needed,
        session_id=session_id,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        branch_id=branch_id,
        needs_more_thoughts=needs_more_thoughts,
        confidence=confidence,
        uncertainty_notes=uncertainty_notes,
        outcome=outcome,
    )
    return thinking_service.process_thought(request)
