import os
from typing import Generator
import pytest
from pydantic import ValidationError
from ultrathink.service import UltraThinkService
from ultrathink.dto import ThoughtRequest, ThoughtResponse


class TestUltraThinkService:
    """Test suite for UltraThinkService"""

    @pytest.fixture
    def server(self) -> Generator[UltraThinkService, None, None]:
        """Create a server instance with logging disabled for tests"""
        os.environ["DISABLE_THOUGHT_LOGGING"] = "true"
        yield UltraThinkService()

    # Validation tests
    def test_reject_missing_thought(self, server: UltraThinkService) -> None:
        """Should reject input with missing thought"""
        input_data = {
            "thought_number": 1,
            "total_thoughts": 3,
            "next_thought_needed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(**input_data)  # type: ignore[arg-type]
        assert "thought" in str(exc_info.value).lower()

    def test_reject_non_string_thought(self, server: UltraThinkService) -> None:
        """Should reject input with non-string thought"""
        input_data = {
            "thought": 123,
            "thought_number": 1,
            "total_thoughts": 3,
            "next_thought_needed": True,
        }

        with pytest.raises(ValidationError):
            ThoughtRequest(**input_data)  # type: ignore[arg-type]

    def test_reject_missing_thought_number(self, server: UltraThinkService) -> None:
        """Should reject input with missing thought_number"""
        input_data = {
            "thought": "Test thought",
            "total_thoughts": 3,
            "next_thought_needed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(**input_data)  # type: ignore[arg-type]
        assert "thought_number" in str(exc_info.value).lower()

    def test_reject_non_number_thought_number(self, server: UltraThinkService) -> None:
        """Should reject input with non-number thought_number"""
        input_data = {
            "thought": "Test thought",
            "thought_number": "1",
            "total_thoughts": 3,
            "next_thought_needed": True,
        }

        with pytest.raises(ValidationError):
            ThoughtRequest(**input_data)  # type: ignore[arg-type]

    def test_reject_missing_total_thoughts(self, server: UltraThinkService) -> None:
        """Should reject input with missing total_thoughts"""
        input_data = {
            "thought": "Test thought",
            "thought_number": 1,
            "next_thought_needed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(**input_data)  # type: ignore[arg-type]
        assert "total_thoughts" in str(exc_info.value).lower()

    def test_reject_non_number_total_thoughts(self, server: UltraThinkService) -> None:
        """Should reject input with non-number total_thoughts"""
        input_data = {
            "thought": "Test thought",
            "thought_number": 1,
            "total_thoughts": "3",
            "next_thought_needed": True,
        }

        with pytest.raises(ValidationError):
            ThoughtRequest(**input_data)  # type: ignore[arg-type]

    def test_reject_missing_next_thought_needed(
        self, server: UltraThinkService
    ) -> None:
        """Should reject input with missing next_thought_needed"""
        input_data = {
            "thought": "Test thought",
            "thought_number": 1,
            "total_thoughts": 3,
        }

        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(**input_data)  # type: ignore[arg-type]
        assert "next_thought_needed" in str(exc_info.value).lower()

    def test_reject_non_boolean_next_thought_needed(
        self, server: UltraThinkService
    ) -> None:
        """Should reject input with non-boolean next_thought_needed"""
        input_data = {
            "thought": "Test thought",
            "thought_number": 1,
            "total_thoughts": 3,
            "next_thought_needed": "true",
        }

        with pytest.raises(ValidationError):
            ThoughtRequest(**input_data)  # type: ignore[arg-type]

    # Valid input tests
    def test_accept_valid_basic_thought(self, server: UltraThinkService) -> None:
        """Should accept valid basic thought"""
        request = ThoughtRequest(
            thought="This is my first thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.thought_number == 1
        assert response.total_thoughts == 3
        assert response.next_thought_needed is True
        assert response.thought_history_length == 1

    def test_accept_thought_with_optional_fields(
        self, server: UltraThinkService
    ) -> None:
        """Should accept thought with optional fields"""
        request = ThoughtRequest(
            thought="Revising my earlier idea",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
            needs_more_thoughts=False,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.thought_number == 2
        assert response.thought_history_length == 1

    def test_track_multiple_thoughts_in_history(
        self, server: UltraThinkService
    ) -> None:
        """Should track multiple thoughts in history"""
        request1 = ThoughtRequest(
            thought="First thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        request2 = ThoughtRequest(
            thought="Second thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
        )
        request3 = ThoughtRequest(
            thought="Final thought",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
        )

        server.process_thought(request1)
        server.process_thought(request2)
        response = server.process_thought(request3)

        assert response.thought_history_length == 3
        assert response.next_thought_needed is False

    def test_auto_adjust_total_thoughts(self, server: UltraThinkService) -> None:
        """Should auto-adjust total_thoughts if thought_number exceeds it"""
        request = ThoughtRequest(
            thought="Thought 5",
            thought_number=5,
            total_thoughts=3,
            next_thought_needed=True,
        )

        response = server.process_thought(request)
        assert response.total_thoughts == 5

    # Branching tests
    def test_track_branches_correctly(self, server: UltraThinkService) -> None:
        """Should track branches correctly"""
        request1 = ThoughtRequest(
            thought="Main thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        request2 = ThoughtRequest(
            thought="Branch A thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
        )
        request3 = ThoughtRequest(
            thought="Branch B thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-b",
        )

        server.process_thought(request1)
        server.process_thought(request2)
        response = server.process_thought(request3)

        assert "branch-a" in response.branches
        assert "branch-b" in response.branches
        assert len(response.branches) == 2
        assert response.thought_history_length == 3

    def test_allow_multiple_thoughts_in_same_branch(
        self, server: UltraThinkService
    ) -> None:
        """Should allow multiple thoughts in same branch"""
        request1 = ThoughtRequest(
            thought="Branch thought 1",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
        )
        request2 = ThoughtRequest(
            thought="Branch thought 2",
            thought_number=2,
            total_thoughts=2,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-a",
        )

        server.process_thought(request1)
        response = server.process_thought(request2)

        assert "branch-a" in response.branches
        assert len(response.branches) == 1

    # Edge case tests
    def test_reject_empty_thought_string(self, server: UltraThinkService) -> None:
        """Should reject empty thought string"""
        with pytest.raises(ValidationError):
            ThoughtRequest(
                thought="",
                thought_number=1,
                total_thoughts=1,
                next_thought_needed=False,
            )

    def test_reject_whitespace_only_thought_string(
        self, server: UltraThinkService
    ) -> None:
        """Should reject whitespace-only thought string"""
        with pytest.raises(ValueError) as exc_info:
            ThoughtRequest(
                thought="   ",
                thought_number=1,
                total_thoughts=1,
                next_thought_needed=False,
            )
        assert "non-empty" in str(exc_info.value).lower()

    def test_handle_very_long_thought_strings(self, server: UltraThinkService) -> None:
        """Should handle very long thought strings"""
        request = ThoughtRequest(
            thought="a" * 10000,
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)

    def test_handle_single_thought(self, server: UltraThinkService) -> None:
        """Should handle thought_number = 1, total_thoughts = 1"""
        request = ThoughtRequest(
            thought="Only thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.thought_number == 1
        assert response.total_thoughts == 1

    def test_handle_next_thought_needed_false(self, server: UltraThinkService) -> None:
        """Should handle next_thought_needed = false"""
        request = ThoughtRequest(
            thought="Final thought",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
        )

        response = server.process_thought(request)
        assert response.next_thought_needed is False

    # Response format tests
    def test_return_correct_response_structure_on_success(
        self, server: UltraThinkService
    ) -> None:
        """Should return ThoughtResponse object on success"""
        request = ThoughtRequest(
            thought="Test thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
        )

        response = server.process_thought(request)

        assert isinstance(response, ThoughtResponse)
        assert hasattr(response, "thought_number")
        assert hasattr(response, "total_thoughts")
        assert hasattr(response, "next_thought_needed")
        assert hasattr(response, "branches")
        assert hasattr(response, "thought_history_length")

    def test_raise_validation_error_on_invalid_request(
        self, server: UltraThinkService
    ) -> None:
        """Should raise ValidationError on invalid request"""
        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(  # type: ignore[call-arg]
                thought="Test",
                thought_number=1,
                total_thoughts=1,
                # missing next_thought_needed
            )
        assert "next_thought_needed" in str(exc_info.value).lower()

    def test_return_pydantic_model_instance(self, server: UltraThinkService) -> None:
        """Should return Pydantic model instance"""
        request = ThoughtRequest(
            thought="Test thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
        )

        response = server.process_thought(request)

        # Can serialize to dict
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert "thought_number" in response_dict
        assert "total_thoughts" in response_dict
