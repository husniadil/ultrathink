from typing import Annotated
from pydantic import BaseModel, Field, field_validator
from .assumption import Assumption


def _validate_thought_not_empty(value: str) -> str:
    """Helper function to validate thought is non-empty"""
    if not value or not value.strip():
        raise ValueError("thought must be a non-empty string")
    return value


class Thought(BaseModel):
    """
    Model: Represents a single thought in sequential thinking process
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
    assumptions: Annotated[
        list[Assumption] | None,
        Field(
            None,
            description="Assumptions made in this thought",
        ),
    ] = None
    depends_on_assumptions: Annotated[
        list[str] | None,
        Field(
            None,
            description="Assumption IDs from previous thoughts that this thought depends on",
        ),
    ] = None
    invalidates_assumptions: Annotated[
        list[str] | None,
        Field(
            None,
            description="Assumption IDs proven false by this thought",
        ),
    ] = None

    @field_validator("thought")
    @classmethod
    def validate_thought_not_empty(cls, v: str) -> str:
        return _validate_thought_not_empty(v)

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

    def validate_references(self, existing_thought_numbers: set[int]) -> None:
        """
        Validate that referenced thoughts exist in history

        Args:
            existing_thought_numbers: Set of thought numbers that exist in session

        Raises:
            ValueError: If referenced thought does not exist
        """
        if self.is_revision and self.revises_thought is not None:
            if self.revises_thought not in existing_thought_numbers:
                # Build helpful error message
                if not existing_thought_numbers:
                    # Empty session - likely forgot to pass session_id
                    raise ValueError(
                        f"Cannot revise thought {self.revises_thought}: no thoughts exist in this session yet. "
                        f"To continue an existing session, pass the session_id parameter."
                    )
                else:
                    # Session has thoughts, but referenced one doesn't exist
                    available = sorted(existing_thought_numbers)
                    raise ValueError(
                        f"Cannot revise thought {self.revises_thought}: thought not found in this session. "
                        f"Available thoughts: {available}"
                    )

        if self.is_branch and self.branch_from_thought is not None:
            if self.branch_from_thought not in existing_thought_numbers:
                # Build helpful error message
                if not existing_thought_numbers:
                    # Empty session - likely forgot to pass session_id
                    raise ValueError(
                        f"Cannot branch from thought {self.branch_from_thought}: no thoughts exist in this session yet. "
                        f"To continue an existing session, pass the session_id parameter."
                    )
                else:
                    # Session has thoughts, but referenced one doesn't exist
                    available = sorted(existing_thought_numbers)
                    raise ValueError(
                        f"Cannot branch from thought {self.branch_from_thought}: thought not found in this session. "
                        f"Available thoughts: {available}"
                    )

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

        # Add confidence display if present
        confidence_str = (
            f" [Confidence: {self.confidence:.0%}]"
            if self.confidence is not None
            else ""
        )
        header = f"{prefix} {self.thought_number}/{self.total_thoughts}{context}{confidence_str}"

        # Build content lines to calculate max width
        content_lines = []

        # Uncertainty notes line (if present)
        uncertainty_line = None
        if self.uncertainty_notes:
            uncertainty_line = f"⚠️  Uncertainty: {self.uncertainty_notes}"
            content_lines.append(uncertainty_line)

        # Main thought line
        content_lines.append(self.thought)

        # Outcome line (if present)
        outcome_line = None
        if self.outcome:
            outcome_line = f"✓ Outcome: {self.outcome}"
            content_lines.append(outcome_line)

        # Assumptions (if present)
        assumption_lines = []
        if self.assumptions:
            for assumption in self.assumptions:
                assumption_lines.append(f"    {assumption.format()}")
                content_lines.extend(assumption_lines)

        # Dependencies (if present)
        if self.depends_on_assumptions:
            dep_line = f"📎 Depends on: {', '.join(self.depends_on_assumptions)}"
            content_lines.append(dep_line)

        # Invalidations (if present)
        if self.invalidates_assumptions:
            inv_line = f"❌ Invalidates: {', '.join(self.invalidates_assumptions)}"
            content_lines.append(inv_line)

        # Calculate border length from longest line
        all_lines = [header] + content_lines
        border_length = max(len(line) for line in all_lines) + 4
        border = "─" * border_length

        # Build final formatted output
        lines = [f"┌{border}┐"]

        # Header (uses -2 padding for metadata lines)
        lines.append(f"│ {header}{' ' * (border_length - len(header) - 2)}│")

        # Uncertainty notes (if present, uses -2 padding for metadata lines)
        if uncertainty_line:
            lines.append(
                f"│ {uncertainty_line}{' ' * (border_length - len(uncertainty_line) - 2)}│"
            )

        # Separator
        lines.append(f"├{border}┤")

        # Main thought content (intentionally uses -1 padding for main content, different from -2 for metadata)
        lines.append(
            f"│ {self.thought}{' ' * (border_length - len(self.thought) - 1)}│"
        )

        # Outcome (if present, uses -2 padding for metadata lines)
        if outcome_line:
            lines.append(
                f"│ {outcome_line}{' ' * (border_length - len(outcome_line) - 2)}│"
            )

        # Assumptions (if present)
        if assumption_lines:
            lines.append(f"├{border}┤")
            lines.append(
                f"│ 📋 Assumptions:{' ' * (border_length - len('📋 Assumptions:') - 2)}│"
            )
            for assumption_line in assumption_lines:
                lines.append(
                    f"│ {assumption_line}{' ' * (border_length - len(assumption_line) - 2)}│"
                )

        # Dependencies (if present, uses -2 padding for metadata lines)
        if self.depends_on_assumptions:
            dep_line = f"📎 Depends on: {', '.join(self.depends_on_assumptions)}"
            lines.append(f"│ {dep_line}{' ' * (border_length - len(dep_line) - 2)}│")

        # Invalidations (if present, uses -2 padding for metadata lines)
        if self.invalidates_assumptions:
            inv_line = f"❌ Invalidates: {', '.join(self.invalidates_assumptions)}"
            lines.append(f"│ {inv_line}{' ' * (border_length - len(inv_line) - 2)}│")

        # Bottom border
        lines.append(f"└{border}┘")

        formatted = "\n".join(lines)
        return f"[{color}]{formatted}[/{color}]"


class ThoughtRequest(BaseModel):
    """
    Model: Request model for ultrathink tool
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
    assumptions: Annotated[
        list[Assumption] | None,
        Field(
            None,
            description="Assumptions made in this thought",
        ),
    ] = None
    depends_on_assumptions: Annotated[
        list[str] | None,
        Field(
            None,
            description="Assumption IDs from previous thoughts that this thought depends on",
        ),
    ] = None
    invalidates_assumptions: Annotated[
        list[str] | None,
        Field(
            None,
            description="Assumption IDs proven false by this thought",
        ),
    ] = None

    @field_validator("thought")
    @classmethod
    def validate_thought_not_empty(cls, v: str) -> str:
        return _validate_thought_not_empty(v)


class ThoughtResponse(BaseModel):
    """
    Model: Response model for ultrathink tool
    Represents output sent to MCP clients
    """

    model_config = {"strict": True}

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
    all_assumptions: Annotated[
        dict[str, Assumption],
        Field(
            description="All assumptions tracked in this session (keyed by assumption ID)",
        ),
    ] = {}
    risky_assumptions: Annotated[
        list[str],
        Field(
            description="IDs of assumptions that are risky (critical, low confidence, unverified)",
        ),
    ] = []
    falsified_assumptions: Annotated[
        list[str],
        Field(
            description="IDs of assumptions proven false",
        ),
    ] = []
