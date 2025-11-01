from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class ThoughtRequest(BaseModel):
    """
    DTO: Request model for ultrathink tool (Interface layer)
    Represents input from MCP clients
    """

    model_config = {"strict": True}

    thought: Annotated[
        str, Field(min_length=1, description="Your current thinking step")
    ]
    total_thoughts: Annotated[
        int,
        Field(
            ge=1,
            description="Estimated total thoughts needed (numeric value, e.g., 3, 5, 10)",
        ),
    ]
    next_thought_needed: Annotated[
        bool | None,
        Field(
            None,
            description="Whether another thought step is needed (auto: true if thought_number < total_thoughts)",
        ),
    ] = None
    thought_number: Annotated[
        int | None,
        Field(
            None,
            ge=1,
            description="Current thought number (auto-assigned if omitted, or provide explicit number for branching/semantic control)",
        ),
    ] = None
    session_id: Annotated[
        str | None,
        Field(None, description="Session identifier (None = create new session)"),
    ] = None
    is_revision: Annotated[
        bool | None, Field(None, description="Whether this revises previous thinking")
    ] = None
    revises_thought: Annotated[
        int | None, Field(None, ge=1, description="Which thought is being reconsidered")
    ] = None
    branch_from_thought: Annotated[
        int | None, Field(None, ge=1, description="Branching point thought number")
    ] = None
    branch_id: Annotated[str | None, Field(None, description="Branch identifier")] = (
        None
    )
    needs_more_thoughts: Annotated[
        bool | None, Field(None, description="If more thoughts are needed")
    ] = None
    confidence: Annotated[
        float | None,
        Field(
            None,
            ge=0.0,
            le=1.0,
            description="Confidence level (0.0-1.0, e.g., 0.7 for 70% confident)",
        ),
    ] = None
    uncertainty_notes: Annotated[
        str | None,
        Field(
            None,
            description="Optional explanation for uncertainty or doubts about this thought",
        ),
    ] = None
    outcome: Annotated[
        str | None,
        Field(
            None,
            description="What was achieved or expected as result of this thought",
        ),
    ] = None

    @field_validator("thought")
    @classmethod
    def validate_thought_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("thought must be a non-empty string")
        return v


class ThoughtResponse(BaseModel):
    """
    DTO: Response model for ultrathink tool (Interface layer)
    Represents output sent to MCP clients
    """

    session_id: Annotated[str, Field(description="Session identifier for continuation")]
    thought_number: Annotated[
        int, Field(ge=1, description="Current thought number in sequence")
    ]
    total_thoughts: Annotated[
        int, Field(ge=1, description="Total number of thoughts planned")
    ]
    next_thought_needed: Annotated[
        bool, Field(description="Whether another thought step is needed")
    ]
    branches: Annotated[
        list[str], Field(description="List of active branch identifiers")
    ]
    thought_history_length: Annotated[
        int, Field(ge=0, description="Total number of thoughts processed in session")
    ]
    confidence: Annotated[
        float | None,
        Field(
            None,
            ge=0.0,
            le=1.0,
            description="Confidence level of this thought (0.0-1.0)",
        ),
    ] = None
    uncertainty_notes: Annotated[
        str | None,
        Field(
            None,
            description="Optional explanation for uncertainty or doubts about this thought",
        ),
    ] = None
    outcome: Annotated[
        str | None,
        Field(
            None,
            description="What was achieved or expected as result of this thought",
        ),
    ] = None
