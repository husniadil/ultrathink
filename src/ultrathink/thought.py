from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class Thought(BaseModel):
    """
    Entity: Represents a single thought in sequential thinking process
    Encapsulates data and behaviors of a thought
    """

    model_config = {"strict": True}

    thought: Annotated[
        str, Field(min_length=1, description="Your current thinking step")
    ]
    thought_number: Annotated[
        int,
        Field(
            ge=1, description="Current thought number (numeric value, e.g., 1, 2, 3)"
        ),
    ]
    total_thoughts: Annotated[
        int,
        Field(
            ge=1,
            description="Estimated total thoughts needed (numeric value, e.g., 3, 5, 10)",
        ),
    ]
    next_thought_needed: Annotated[
        bool, Field(description="Whether another thought step is needed")
    ]
    is_revision: Annotated[
        bool | None,
        Field(None, description="Whether this revises previous thinking"),
    ] = None
    revises_thought: Annotated[
        int | None,
        Field(None, ge=1, description="Which thought is being reconsidered"),
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

    @field_validator("thought")
    @classmethod
    def validate_thought_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("thought must be a non-empty string")
        return v

    @property
    def is_branch(self) -> bool:
        """Check if this thought is a branch"""
        return bool(self.branch_from_thought and self.branch_id)

    @property
    def is_final(self) -> bool:
        """Check if this is the final thought"""
        return not self.next_thought_needed

    def auto_adjust_total(self) -> None:
        """Auto-adjust total thoughts if current number exceeds it"""
        if self.thought_number > self.total_thoughts:
            self.total_thoughts = self.thought_number

    def format(self) -> str:
        """Format this thought for display with colors and borders"""
        prefix = ""
        context = ""

        if self.is_revision:
            prefix = "🔄 Revision"
            context = f" (revising thought {self.revises_thought})"
            color = "yellow"
        elif self.is_branch:
            prefix = "🌿 Branch"
            context = (
                f" (from thought {self.branch_from_thought}, ID: {self.branch_id})"
            )
            color = "green"
        else:
            prefix = "💭 Thought"
            context = ""
            color = "blue"

        header = f"{prefix} {self.thought_number}/{self.total_thoughts}{context}"
        border_length = max(len(header), len(self.thought)) + 4
        border = "─" * border_length

        lines = [
            f"┌{border}┐",
            f"│ {header}{' ' * (border_length - len(header) - 2)}│",
            f"├{border}┤",
            f"│ {self.thought}{' ' * (border_length - len(self.thought) - 1)}│",
            f"└{border}┘",
        ]

        formatted = "\n".join(lines)
        return f"[{color}]{formatted}[/{color}]"
