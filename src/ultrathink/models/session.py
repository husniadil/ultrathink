import sys
from rich.console import Console
from .thought import Thought
from .assumption import Assumption


def _get_console() -> Console:
    """Lazy-load console only when needed"""
    return Console(file=sys.stderr)


class ThinkingSession:
    """
    Model: Manages the sequential thinking session
    Enforces business rules and maintains consistency
    """

    def __init__(self, disable_logging: bool = False):
        self._thoughts: list[Thought] = []
        self._branches: dict[str, list[Thought]] = {}
        self._assumptions: dict[str, Assumption] = {}
        self._disable_logging = disable_logging

    @property
    def thought_count(self) -> int:
        """Get total number of thoughts in this session"""
        return len(self._thoughts)

    @property
    def branch_ids(self) -> list[str]:
        """Get list of all branch IDs"""
        return list(self._branches.keys())

    @property
    def all_assumptions(self) -> dict[str, Assumption]:
        """Get all assumptions in this session"""
        return self._assumptions.copy()

    @property
    def risky_assumptions(self) -> list[str]:
        """Get IDs of risky assumptions (critical, low confidence, unverified)"""
        return [aid for aid, a in self._assumptions.items() if a.is_risky]

    @property
    def falsified_assumptions(self) -> list[str]:
        """Get IDs of assumptions proven false"""
        return [aid for aid, a in self._assumptions.items() if a.is_falsified]

    def verify_assumption(self, assumption_id: str, is_true: bool) -> Assumption | None:
        """
        Mark an assumption as verified (true or false)

        Args:
            assumption_id: ID of assumption to verify
            is_true: Whether the assumption is verified as true or false

        Returns:
            Updated assumption if found, None if not found
        """
        if assumption_id in self._assumptions:
            assumption = self._assumptions[assumption_id]
            assumption.verification_status = (
                "verified_true" if is_true else "verified_false"
            )
            return assumption
        return None

    def get_affected_thoughts(self, assumption_id: str) -> list[int]:
        """
        Find all thought numbers that depend on a given assumption

        Args:
            assumption_id: ID of assumption to check

        Returns:
            List of thought numbers that depend on this assumption
        """
        affected = []
        for thought in self._thoughts:
            if (
                thought.depends_on_assumptions
                and assumption_id in thought.depends_on_assumptions
            ):
                affected.append(thought.thought_number)
        return affected

    def add_thought(self, thought: Thought) -> None:
        """
        Add a thought to the session
        Enforces business rules and manages branches
        """
        # Auto-adjust total if needed
        thought.auto_adjust_total()

        # Validate references before adding
        existing_numbers = {t.thought_number for t in self._thoughts}
        thought.validate_references(existing_numbers)

        # Validate assumption dependencies
        if thought.depends_on_assumptions:
            for assumption_id in thought.depends_on_assumptions:
                if assumption_id not in self._assumptions:
                    available = sorted(self._assumptions.keys())
                    raise ValueError(
                        f"Cannot depend on assumption {assumption_id}: assumption not found in this session. "
                        f"Available assumptions: {available if available else 'none'}"
                    )

        # Add new assumptions from this thought
        if thought.assumptions:
            for assumption in thought.assumptions:
                if assumption.id in self._assumptions:
                    # Validate that core fields match when updating
                    existing = self._assumptions[assumption.id]
                    if existing.text != assumption.text:
                        raise ValueError(
                            f"Cannot update assumption {assumption.id}: text mismatch. "
                            f"Existing: '{existing.text}', New: '{assumption.text}'. "
                            f"Core assumption fields (text, critical) are immutable."
                        )
                    if existing.critical != assumption.critical:
                        raise ValueError(
                            f"Cannot update assumption {assumption.id}: critical flag mismatch. "
                            f"Existing: {existing.critical}, New: {assumption.critical}. "
                            f"Core assumption fields (text, critical) are immutable."
                        )
                    # Allow updating verification-related fields
                    if not self._disable_logging:
                        _get_console().print(
                            f"[yellow]⚠️  Updating assumption {assumption.id} (verification status or confidence)[/yellow]"
                        )
                    existing.confidence = assumption.confidence
                    existing.verifiable = assumption.verifiable
                    existing.evidence = assumption.evidence
                    existing.verification_status = assumption.verification_status
                else:
                    # Add new assumption
                    self._assumptions[assumption.id] = assumption

        # Handle assumption invalidations
        if thought.invalidates_assumptions:
            for assumption_id in thought.invalidates_assumptions:
                if assumption_id not in self._assumptions:
                    available = sorted(self._assumptions.keys())
                    raise ValueError(
                        f"Cannot invalidate assumption {assumption_id}: assumption not found in this session. "
                        f"Available assumptions: {available if available else 'none'}"
                    )
                self._assumptions[assumption_id].verification_status = "verified_false"

        # Add to history
        self._thoughts.append(thought)

        # Track branch if applicable
        if thought.is_branch and thought.branch_id is not None:
            if thought.branch_id not in self._branches:
                self._branches[thought.branch_id] = []
            self._branches[thought.branch_id].append(thought)

        # Log if enabled
        if not self._disable_logging:
            _get_console().print(thought.format())
