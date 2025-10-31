import sys
from rich.console import Console
from .thought import Thought

console = Console(file=sys.stderr)


class ThinkingSession:
    """
    Aggregate Root: Manages the sequential thinking session
    Enforces business rules and maintains consistency (Pure domain - no protocol knowledge)
    """

    def __init__(self, disable_logging: bool = False):
        self._thoughts: list[Thought] = []
        self._branches: dict[str, list[Thought]] = {}
        self._disable_logging = disable_logging

    @property
    def thought_count(self) -> int:
        """Get total number of thoughts in this session"""
        return len(self._thoughts)

    @property
    def branch_ids(self) -> list[str]:
        """Get list of all branch IDs"""
        return list(self._branches.keys())

    def add_thought(self, thought: Thought) -> None:
        """
        Add a thought to the session
        Enforces business rules and manages branches
        """
        # Auto-adjust total if needed
        thought.auto_adjust_total()

        # Validate references before adding (aggregate root enforces invariants)
        existing_numbers = {t.thought_number for t in self._thoughts}
        thought.validate_references(existing_numbers)

        # Add to history
        self._thoughts.append(thought)

        # Track branch if applicable
        if thought.is_branch and thought.branch_id is not None:
            if thought.branch_id not in self._branches:
                self._branches[thought.branch_id] = []
            self._branches[thought.branch_id].append(thought)

        # Log if enabled
        if not self._disable_logging:
            console.print(thought.format())
