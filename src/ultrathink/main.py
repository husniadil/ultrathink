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
    thought_number: Annotated[
        int,
        Field(
            ge=1, description="Current thought number (numeric value, e.g., 1, 2, 3)"
        ),
    ],
    total_thoughts: Annotated[
        int,
        Field(
            ge=1,
            description="Estimated total thoughts needed (numeric value, e.g., 3, 5, 10)",
        ),
    ],
    next_thought_needed: Annotated[
        bool, Field(description="Whether another thought step is needed")
    ],
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
    - next_thought_needed: True if you need more thinking, even if at what seemed like the end
    - thought_number: Current number in sequence (can go beyond initial total if needed)
    - total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
    - is_revision: A boolean indicating if this thought revises previous thinking
    - revises_thought: If is_revision is true, which thought number is being reconsidered
    - branch_from_thought: If branching, which thought number is the branching point
    - branch_id: Identifier for the current branch (if any)
    - needs_more_thoughts: If reaching end but realizing more thoughts needed

    Example usage:

    Thought 1: "I need to design a caching strategy. Let me first consider the access patterns..."
    Thought 2: "Based on access patterns, I see two viable approaches: LRU or LFU..."
    Thought 3 (revision of 2): "Wait, I should also consider TTL-based expiration..."
    Thought 4 (branch from 2): "Let me explore a hybrid approach combining LRU with TTL..."
    Thought 5: "The hybrid approach addresses both requirements. Final recommendation: ..."

    Usage guide:
    1. Start with an initial estimate of needed thoughts, be ready to adjust total_thoughts as you progress
    2. Question or revise previous thoughts using is_revision=true and revises_thought parameters
    3. Explore alternative reasoning paths using branch_from_thought and branch_id parameters
    4. Add more thoughts if needed, even after reaching what seemed like the end
    5. Express uncertainty when present - this is valuable information
    6. Clearly state what you're analyzing or deciding in each thought
    7. Ignore information that is irrelevant to the current step
    8. Generate solution hypotheses as you develop understanding
    9. Verify hypotheses through subsequent thinking steps
    10. Repeat the process until you reach a satisfactory solution
    11. Provide a single, ideally correct answer as the final output
    12. Only set next_thought_needed=false when truly done and you have a complete answer
    """
    # Construct ThoughtRequest from flat parameters
    request = ThoughtRequest(
        thought=thought,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        next_thought_needed=next_thought_needed,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        branch_id=branch_id,
        needs_more_thoughts=needs_more_thoughts,
    )
    return thinking_service.process_thought(request)
