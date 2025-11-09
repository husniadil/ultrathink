from typing import Annotated, Literal
from pydantic import BaseModel, Field


class Assumption(BaseModel):
    """
    Model: Represents an assumption made during thinking process
    Tracks what is being taken for granted in reasoning
    """

    model_config = {"strict": True}

    id: Annotated[
        str,
        Field(
            pattern=r"^A\d+$",
            description="Unique identifier for this assumption (e.g., 'A1', 'A2')",
        ),
    ]
    text: Annotated[
        str,
        Field(min_length=1, description="The assumption being made"),
    ]
    confidence: Annotated[
        float,
        Field(
            ge=0.0,
            le=1.0,
            description="Confidence level (0.0-1.0) in this assumption being true",
        ),
    ] = 1.0
    critical: Annotated[
        bool,
        Field(
            description="If false, does the reasoning collapse? (default: True)",
        ),
    ] = True
    verifiable: Annotated[
        bool,
        Field(
            description="Can this assumption be verified through testing or research? (default: False)",
        ),
    ] = False
    evidence: Annotated[
        str | None,
        Field(
            None, description="Why you believe this assumption (reference, reasoning)"
        ),
    ] = None
    verification_status: Annotated[
        Literal["unverified", "verified_true", "verified_false"] | None,
        Field(None, description="Whether this assumption has been verified"),
    ] = None

    @property
    def is_verified(self) -> bool:
        """Check if this assumption has been verified (true or false)"""
        return self.verification_status in ("verified_true", "verified_false")

    @property
    def is_falsified(self) -> bool:
        """Check if this assumption has been proven false"""
        return self.verification_status == "verified_false"

    @property
    def is_risky(self) -> bool:
        """Check if this is a risky assumption (critical, low confidence, unverified)"""
        return (
            self.critical
            and self.confidence < 0.7
            and self.verification_status != "verified_true"
        )

    def format(self) -> str:
        """Format this assumption for display"""
        # Status indicator
        status = ""
        if self.verification_status == "verified_true":
            status = " ✓"
        elif self.verification_status == "verified_false":
            status = " ✗"
        elif self.verifiable and not self.is_verified:
            status = " ?"

        # Critical indicator
        critical_marker = " [CRITICAL]" if self.critical else ""

        # Confidence display
        confidence_str = f" (confidence: {self.confidence:.0%})"

        # Evidence
        evidence_str = f"\n    Evidence: {self.evidence}" if self.evidence else ""

        return f"{self.id}: {self.text}{status}{critical_marker}{confidence_str}{evidence_str}"
