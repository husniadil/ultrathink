from typing import Annotated
from pydantic import Field
from fastmcp import FastMCP
from ..services.thinking_service import UltraThinkService
from ..models.thought import ThoughtRequest, ThoughtResponse
from ..models.assumption import Assumption

mcp = FastMCP("UltraThink")

thinking_service = UltraThinkService()


@mcp.tool
def ultrathink(
    thought: Annotated[
        str,
        Field(
            min_length=1,
            description=(
                "Your current thinking step. Can include: regular analytical steps, "
                "revisions of previous thoughts, questions about previous decisions, "
                "realizations about needing more analysis, changes in approach, "
                "hypothesis generation, or hypothesis verification"
            ),
        ),
    ],
    total_thoughts: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "Current estimate of thoughts needed (can be adjusted up/down as you progress). "
                "Numeric value, e.g., 3, 5, 10"
            ),
        ),
    ],
    next_thought_needed: Annotated[
        bool | None,
        Field(
            None,
            description=(
                "Whether another thought step is needed. Auto-assigned as "
                "(thought_number < total_thoughts) if omitted. Set explicitly to override: "
                "True to extend beyond total_thoughts, False to end early"
            ),
        ),
    ] = None,
    thought_number: Annotated[
        int | None,
        Field(
            None,
            ge=1,
            description=(
                "Current number in sequence. Auto-assigned sequentially if omitted (1, 2, 3...), "
                "or provide explicit number for branching/semantic control"
            ),
        ),
    ] = None,
    session_id: Annotated[
        str | None,
        Field(
            None,
            description=(
                "Optional session identifier for managing multiple thinking sessions. "
                "None (default): creates new session with auto-generated UUID. "
                "Provide session_id from previous response: continue that thinking session. "
                "Provide custom string: create or resume session with that ID (resilient recovery)"
            ),
        ),
    ] = None,
    is_revision: Annotated[
        bool | None,
        Field(
            None,
            description="Boolean indicating if this thought revises previous thinking. Use with revises_thought parameter",
        ),
    ] = None,
    revises_thought: Annotated[
        int | None,
        Field(
            None,
            ge=1,
            description="If is_revision is true, which thought number is being reconsidered",
        ),
    ] = None,
    branch_from_thought: Annotated[
        int | None,
        Field(
            None,
            ge=1,
            description="If branching, which thought number is the branching point. Use with branch_id parameter",
        ),
    ] = None,
    branch_id: Annotated[
        str | None,
        Field(
            None,
            description="Identifier for the current branch (if branching from a previous thought)",
        ),
    ] = None,
    needs_more_thoughts: Annotated[
        bool | None,
        Field(
            None,
            description="If reaching end but realizing more thoughts are needed beyond initial estimate",
        ),
    ] = None,
    confidence: Annotated[
        float | None,
        Field(
            None,
            ge=0.0,
            le=1.0,
            description=(
                "Confidence level (0.0-1.0) expressing certainty about this thought. "
                "Low (0.3-0.6): exploratory thinking, initial hypotheses, uncertain analysis. "
                "Medium (0.6-0.8): reasoned analysis, likely conclusions, working hypotheses. "
                "High (0.8-1.0): verified solutions, confident conclusions, proven facts"
            ),
        ),
    ] = None,
    uncertainty_notes: Annotated[
        str | None,
        Field(
            None,
            description="Optional explanation for doubts or concerns (complements confidence score)",
        ),
    ] = None,
    outcome: Annotated[
        str | None,
        Field(
            None,
            description="What was achieved or expected as result of this thought",
        ),
    ] = None,
    assumptions: Annotated[
        list[Assumption] | None,
        Field(
            None,
            description=(
                "Assumptions made in this thought. Required fields: "
                "id (e.g., 'A1'), text (the assumption). "
                "Optional fields: confidence (0.0-1.0, default 1.0), "
                "critical (bool, default True), verifiable (bool, default False), "
                "evidence (str, default None), verification_status ('unverified'|'verified_true'|'verified_false', default None). "
                "Note: Core fields (text, critical) are immutable after creation - only verification fields can be updated."
            ),
        ),
    ] = None,
    depends_on_assumptions: Annotated[
        list[str] | None,
        Field(
            None,
            description="Assumption IDs from previous thoughts that this thought depends on (e.g., ['A1', 'A2'])",
        ),
    ] = None,
    invalidates_assumptions: Annotated[
        list[str] | None,
        Field(
            None,
            description="Assumption IDs proven false by this thought (e.g., ['A3'])",
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

    Usage notes:
    - Each call returns a ThoughtResponse with session_id - use this to continue the same thinking session
    - You can run multiple independent thinking sessions in parallel by using different session_ids
    - The tool automatically manages thought numbering and determines if more thoughts are needed
    - Use confidence scoring (0.0-1.0) to explicitly track uncertainty in your reasoning
    - Session state is maintained in memory - reuse custom session_ids for resilient recovery
    - The response is returned to you for tracking progress - communicate insights to the user as you think

    Parameter groups:
    - Core params: thought, total_thoughts (required)
    - Auto-managed: thought_number, next_thought_needed (optional - auto-assigned if omitted)
    - Session management: session_id (optional - None creates new session)
    - Revision params: is_revision, revises_thought (use together)
    - Branching params: branch_from_thought, branch_id (use together)
    - Confidence tracking: confidence, uncertainty_notes, outcome (optional)
    - Assumption tracking: assumptions, depends_on_assumptions, invalidates_assumptions (optional)

    Example usage:

    Thought 1 (confidence: 0.6): "I need to design a caching strategy. Let me first consider the access patterns..."
    Thought 2 (confidence: 0.7): "Based on access patterns, I see two viable approaches: LRU or LFU..."
    Thought 3 (revision of 2, confidence: 0.75): "Wait, I should also consider TTL-based expiration..."
    Thought 4 (branch from 2, confidence: 0.8): "Let me explore a hybrid approach combining LRU with TTL..."
    Thought 5 (confidence: 0.95): "The hybrid approach addresses both requirements. Final recommendation: ..."

    Thinking workflow:
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
    7. Track assumptions explicitly using the assumptions parameter:
       - State what you're taking for granted with assumption objects
       - Mark critical assumptions (if false, reasoning collapses)
       - Express confidence in each assumption (separate from thought confidence)
       - Mark assumptions as verifiable if they can be checked
    8. Build on previous assumptions using depends_on_assumptions to show reasoning dependencies
    9. Invalidate false assumptions using invalidates_assumptions when discovering errors
    10. Monitor risky_assumptions in response (critical + low confidence + unverified)
    11. Clearly state what you're analyzing or deciding in each thought
    12. Ignore information that is irrelevant to the current step
    13. Generate solution hypotheses as you develop understanding
    14. Verify hypotheses through subsequent thinking steps
    15. Repeat the process until you reach a satisfactory solution
    16. Provide a single, ideally correct answer as the final output
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
        assumptions=assumptions,
        depends_on_assumptions=depends_on_assumptions,
        invalidates_assumptions=invalidates_assumptions,
    )
    return thinking_service.process_thought(request)
