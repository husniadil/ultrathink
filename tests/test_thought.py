import pytest
from ultrathink.thought import Thought


class TestThought:
    """Test suite for Thought entity"""

    def test_thought_is_final_property(self) -> None:
        """Should correctly identify final thoughts via is_final property"""
        # Create final thought
        final_thought = Thought(
            thought="This is final",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
        )
        assert final_thought.is_final is True

        # Create non-final thought
        ongoing_thought = Thought(
            thought="Not final yet",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert ongoing_thought.is_final is False

    def test_thought_is_branch_property(self) -> None:
        """Should correctly identify branch thoughts via is_branch property"""
        # Create branch thought
        branch_thought = Thought(
            thought="Branch thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
        )
        assert branch_thought.is_branch is True

        # Create regular thought
        regular_thought = Thought(
            thought="Regular thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert regular_thought.is_branch is False

    def test_auto_adjust_total(self) -> None:
        """Should auto-adjust total_thoughts when thought_number exceeds it"""
        thought = Thought(
            thought="Thought 5",
            thought_number=5,
            total_thoughts=3,
            next_thought_needed=True,
        )

        # Before adjustment
        assert thought.total_thoughts == 3

        # After adjustment
        thought.auto_adjust_total()
        assert thought.total_thoughts == 5

    def test_auto_adjust_total_no_change_when_within_range(self) -> None:
        """Should not adjust total_thoughts when thought_number is within range"""
        thought = Thought(
            thought="Thought 2",
            thought_number=2,
            total_thoughts=5,
            next_thought_needed=True,
        )

        thought.auto_adjust_total()
        assert thought.total_thoughts == 5

    def test_format_regular_thought(self) -> None:
        """Should format regular thoughts with correct emoji and color"""
        thought = Thought(
            thought="Regular thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        formatted = thought.format()
        assert "💭 Thought" in formatted
        assert "1/3" in formatted
        assert "[blue]" in formatted
        assert "[/blue]" in formatted

    def test_format_revision_thought(self) -> None:
        """Should format revision thoughts with correct emoji and color"""
        thought = Thought(
            thought="Revised thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
        )

        formatted = thought.format()
        assert "🔄 Revision" in formatted
        assert "revising thought 1" in formatted
        assert "[yellow]" in formatted
        assert "[/yellow]" in formatted

    def test_format_branch_thought(self) -> None:
        """Should format branch thoughts with correct emoji and color"""
        thought = Thought(
            thought="Branch thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-a",
        )

        formatted = thought.format()
        assert "🌿 Branch" in formatted
        assert "from thought 1" in formatted
        assert "ID: branch-a" in formatted
        assert "[green]" in formatted
        assert "[/green]" in formatted

    def test_reject_whitespace_thought(self) -> None:
        """Should reject whitespace-only thought via validator"""
        with pytest.raises(ValueError) as exc_info:
            Thought(
                thought="   ",
                thought_number=1,
                total_thoughts=1,
                next_thought_needed=False,
            )
        assert "non-empty" in str(exc_info.value).lower()
