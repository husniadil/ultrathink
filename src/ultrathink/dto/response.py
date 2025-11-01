from typing import Annotated
from pydantic import BaseModel, Field


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
