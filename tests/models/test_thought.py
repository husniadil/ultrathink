import pytest
from ultrathink.models.thought import Thought


class TestThought:
    """Test suite for Thought model"""

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

    def test_confidence_field(self) -> None:
        """Should accept valid confidence values"""
        thought = Thought(
            thought="High confidence thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.85,
        )
        assert thought.confidence == 0.85

    def test_confidence_none_by_default(self) -> None:
        """Should default confidence to None when not provided"""
        thought = Thought(
            thought="No confidence",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert thought.confidence is None

    def test_format_thought_with_confidence(self) -> None:
        """Should format thought with confidence percentage"""
        thought = Thought(
            thought="Confident thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.75,
        )

        formatted = thought.format()
        assert "Confidence: 75%" in formatted
        assert "💭 Thought" in formatted
        assert "1/3" in formatted

    def test_uncertainty_notes_field(self) -> None:
        """Should accept uncertainty_notes string values"""
        thought = Thought(
            thought="Uncertain thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            uncertainty_notes="Haven't tested all edge cases yet",
        )
        assert thought.uncertainty_notes == "Haven't tested all edge cases yet"

    def test_uncertainty_notes_none_by_default(self) -> None:
        """Should default uncertainty_notes to None when not provided"""
        thought = Thought(
            thought="No uncertainty notes",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert thought.uncertainty_notes is None

    def test_outcome_field(self) -> None:
        """Should accept outcome string values"""
        thought = Thought(
            thought="Testing authentication fix",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            outcome="All tests passing, bug fixed",
        )
        assert thought.outcome == "All tests passing, bug fixed"

    def test_outcome_none_by_default(self) -> None:
        """Should default outcome to None when not provided"""
        thought = Thought(
            thought="No outcome",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert thought.outcome is None

    def test_format_thought_with_uncertainty_notes(self) -> None:
        """Should format thought with uncertainty notes"""
        thought = Thought(
            thought="Uncertain approach",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            uncertainty_notes="Not sure about performance impact",
        )

        formatted = thought.format()
        assert "⚠️  Uncertainty: Not sure about performance impact" in formatted
        assert "💭 Thought" in formatted
        assert "1/3" in formatted

    def test_format_thought_with_outcome(self) -> None:
        """Should format thought with outcome"""
        thought = Thought(
            thought="Fixed the bug",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            outcome="Bug resolved successfully",
        )

        formatted = thought.format()
        assert "✓ Outcome: Bug resolved successfully" in formatted
        assert "💭 Thought" in formatted
        assert "1/3" in formatted

    def test_format_thought_with_both_new_fields(self) -> None:
        """Should format thought with both uncertainty_notes and outcome"""
        thought = Thought(
            thought="Testing the fix",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.8,
            uncertainty_notes="Haven't tested under load",
            outcome="Basic tests pass",
        )

        formatted = thought.format()
        assert "Confidence: 80%" in formatted
        assert "⚠️  Uncertainty: Haven't tested under load" in formatted
        assert "✓ Outcome: Basic tests pass" in formatted
        assert "💭 Thought" in formatted
        assert "1/3" in formatted

    def test_format_thought_without_new_fields(self) -> None:
        """Should format thought correctly when new fields are not provided (backward compat)"""
        thought = Thought(
            thought="Simple thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        formatted = thought.format()
        assert "💭 Thought" in formatted
        assert "1/3" in formatted
        assert "⚠️  Uncertainty" not in formatted
        assert "✓ Outcome" not in formatted


class TestThoughtJsonStringParsing:
    """Test suite for JSON string parsing in Thought model"""

    def test_assumptions_from_json_string(self) -> None:
        """Should parse assumptions from JSON string"""
        assumptions_json = (
            '[{"id": "A1", "text": "Test assumption", "confidence": 0.8}]'
        )

        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=assumptions_json,  # type: ignore[arg-type]
        )

        assert thought.assumptions is not None
        assert len(thought.assumptions) == 1
        assert thought.assumptions[0].id == "A1"
        assert thought.assumptions[0].text == "Test assumption"
        assert thought.assumptions[0].confidence == 0.8

    def test_assumptions_from_list(self) -> None:
        """Should accept assumptions as proper list"""
        from ultrathink.models.assumption import Assumption

        assumptions = [Assumption(id="A1", text="Test assumption", confidence=0.8)]

        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=assumptions,
        )

        assert thought.assumptions is not None
        assert len(thought.assumptions) == 1
        assert thought.assumptions[0].id == "A1"

    def test_depends_on_assumptions_from_json_string(self) -> None:
        """Should parse depends_on_assumptions from JSON string"""
        depends_json = '["A1", "A2", "A3"]'

        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions=depends_json,  # type: ignore[arg-type]
        )

        assert thought.depends_on_assumptions == ["A1", "A2", "A3"]

    def test_depends_on_assumptions_from_list(self) -> None:
        """Should accept depends_on_assumptions as proper list"""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions=["A1", "A2"],
        )

        assert thought.depends_on_assumptions == ["A1", "A2"]

    def test_invalidates_assumptions_from_json_string(self) -> None:
        """Should parse invalidates_assumptions from JSON string"""
        invalidates_json = '["A1", "A2"]'

        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            invalidates_assumptions=invalidates_json,  # type: ignore[arg-type]
        )

        assert thought.invalidates_assumptions == ["A1", "A2"]

    def test_invalidates_assumptions_from_list(self) -> None:
        """Should accept invalidates_assumptions as proper list"""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            invalidates_assumptions=["A1"],
        )

        assert thought.invalidates_assumptions == ["A1"]

    def test_assumptions_empty_string_treated_as_none(self) -> None:
        """Should treat empty string as None"""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions="",  # type: ignore[arg-type]
        )

        assert thought.assumptions is None

    def test_assumptions_null_string_treated_as_none(self) -> None:
        """Should treat 'null' string as None"""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions="null",  # type: ignore[arg-type]
        )

        assert thought.assumptions is None

    def test_assumptions_invalid_json_raises_error(self) -> None:
        """Should raise error for invalid JSON"""
        with pytest.raises(ValueError, match="assumptions must be valid JSON"):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                assumptions='{"invalid": json}',  # type: ignore[arg-type]
            )

    def test_assumptions_non_list_json_raises_error(self) -> None:
        """Should raise error when JSON is not a list"""
        with pytest.raises(
            ValueError, match="assumptions must be a list or valid JSON string"
        ):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                assumptions='{"id": "A1"}',  # type: ignore[arg-type]
            )

    def test_depends_on_invalid_json_raises_error(self) -> None:
        """Should raise error for invalid JSON in depends_on_assumptions"""
        with pytest.raises(
            ValueError, match="depends_on_assumptions must be valid JSON"
        ):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                depends_on_assumptions="[invalid json]",  # type: ignore[arg-type]
            )

    def test_invalidates_non_list_json_raises_error(self) -> None:
        """Should raise error when invalidates_assumptions JSON is not a list"""
        with pytest.raises(
            ValueError,
            match="invalidates_assumptions must be a list or valid JSON string",
        ):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                invalidates_assumptions='"A1"',  # type: ignore[arg-type]
            )

    def test_unexpected_type_raises_error(self) -> None:
        """Should raise error when value is unexpected type (not None, list, or string)"""
        with pytest.raises(ValueError, match="must be a list or JSON string"):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                assumptions=123,  # type: ignore[arg-type]
            )

    def test_format_thought_with_assumptions(self) -> None:
        """Should format thought with assumptions in output"""
        from ultrathink.models.assumption import Assumption

        thought = Thought(
            thought="Test with assumptions",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[
                Assumption(id="A1", text="First assumption", confidence=0.8),
                Assumption(id="A2", text="Second assumption", confidence=0.9),
            ],
        )

        formatted = thought.format()
        assert "📋 Assumptions:" in formatted
        assert "A1: First assumption" in formatted
        assert "A2: Second assumption" in formatted

    def test_format_thought_with_depends_on_assumptions(self) -> None:
        """Should format thought with depends_on_assumptions in output"""
        thought = Thought(
            thought="Depends on previous assumptions",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions=["A1", "A2"],
        )

        formatted = thought.format()
        assert "📎 Depends on: A1, A2" in formatted

    def test_format_thought_with_invalidates_assumptions(self) -> None:
        """Should format thought with invalidates_assumptions in output"""
        thought = Thought(
            thought="Invalidating previous assumptions",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            invalidates_assumptions=["A1"],
        )

        formatted = thought.format()
        assert "❌ Invalidates: A1" in formatted
