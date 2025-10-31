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

    def test_auto_assign_thought_number_when_none(
        self, server: UltraThinkService
    ) -> None:
        """Should auto-assign thought_number when omitted"""
        request = ThoughtRequest(
            thought="First thought without explicit number",
            total_thoughts=3,
            next_thought_needed=True,
        )

        response = server.process_thought(request)
        assert response.thought_number == 1
        assert response.thought_history_length == 1

    def test_auto_assign_multiple_thoughts_sequential(
        self, server: UltraThinkService
    ) -> None:
        """Should auto-assign sequential numbers for multiple thoughts"""
        session_id = "test-auto-session"

        # First thought - should be auto-assigned as 1
        request1 = ThoughtRequest(
            thought="First auto thought",
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        response1 = server.process_thought(request1)
        assert response1.thought_number == 1

        # Second thought - should be auto-assigned as 2
        request2 = ThoughtRequest(
            thought="Second auto thought",
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        response2 = server.process_thought(request2)
        assert response2.thought_number == 2

        # Third thought - should be auto-assigned as 3
        request3 = ThoughtRequest(
            thought="Third auto thought",
            total_thoughts=3,
            next_thought_needed=False,
            session_id=session_id,
        )
        response3 = server.process_thought(request3)
        assert response3.thought_number == 3
        assert response3.thought_history_length == 3

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

    def test_auto_assign_next_thought_true_when_not_final(
        self, server: UltraThinkService
    ) -> None:
        """Should auto-assign next_thought_needed=True when thought_number < total_thoughts"""
        request = ThoughtRequest(
            thought="First thought",
            thought_number=1,
            total_thoughts=3,
            # next_thought_needed omitted - should be auto-assigned as True
        )

        response = server.process_thought(request)
        assert response.next_thought_needed is True
        assert response.thought_number == 1
        assert response.total_thoughts == 3

    def test_auto_assign_next_thought_false_when_final(
        self, server: UltraThinkService
    ) -> None:
        """Should auto-assign next_thought_needed=False when thought_number == total_thoughts"""
        request = ThoughtRequest(
            thought="Final thought",
            thought_number=3,
            total_thoughts=3,
            # next_thought_needed omitted - should be auto-assigned as False
        )

        response = server.process_thought(request)
        assert response.next_thought_needed is False
        assert response.thought_number == 3
        assert response.total_thoughts == 3

    def test_explicit_next_thought_overrides_auto(
        self, server: UltraThinkService
    ) -> None:
        """Should respect explicit next_thought_needed value over auto-assignment"""
        # Case 1: Explicitly set to False when not final (early termination)
        request1 = ThoughtRequest(
            thought="Ending early",
            thought_number=2,
            total_thoughts=5,
            next_thought_needed=False,  # Explicit False
        )
        response1 = server.process_thought(request1)
        assert response1.next_thought_needed is False

        # Case 2: Explicitly set to True when at final (extending)
        request2 = ThoughtRequest(
            thought="Continuing beyond estimate",
            thought_number=5,
            total_thoughts=5,
            next_thought_needed=True,  # Explicit True
        )
        response2 = server.process_thought(request2)
        assert response2.next_thought_needed is True

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

    def test_reject_confidence_below_zero(self, server: UltraThinkService) -> None:
        """Should reject confidence value below 0.0"""
        input_data = {
            "thought": "Test thought",
            "thought_number": 1,
            "total_thoughts": 3,
            "next_thought_needed": True,
            "confidence": -0.1,
        }

        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(**input_data)  # type: ignore[arg-type]
        assert "confidence" in str(exc_info.value).lower()

    def test_reject_confidence_above_one(self, server: UltraThinkService) -> None:
        """Should reject confidence value above 1.0"""
        input_data = {
            "thought": "Test thought",
            "thought_number": 1,
            "total_thoughts": 3,
            "next_thought_needed": True,
            "confidence": 1.5,
        }

        with pytest.raises(ValidationError) as exc_info:
            ThoughtRequest(**input_data)  # type: ignore[arg-type]
        assert "confidence" in str(exc_info.value).lower()

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
        # Create original thought first
        request1 = ThoughtRequest(
            thought="Original idea",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id="test-session",
        )
        server.process_thought(request1)

        # Now revise with optional fields
        request2 = ThoughtRequest(
            thought="Revising my earlier idea",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
            needs_more_thoughts=False,
            session_id="test-session",
        )

        response = server.process_thought(request2)
        assert isinstance(response, ThoughtResponse)
        assert response.thought_number == 2
        assert response.thought_history_length == 2

    def test_accept_thought_with_confidence(self, server: UltraThinkService) -> None:
        """Should accept thought with valid confidence value"""
        request = ThoughtRequest(
            thought="High confidence thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.85,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.confidence == 0.85
        assert response.thought_number == 1

    def test_track_multiple_thoughts_in_history(
        self, server: UltraThinkService
    ) -> None:
        """Should track multiple thoughts in history"""
        session_id = "test-session"
        request1 = ThoughtRequest(
            thought="First thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        request2 = ThoughtRequest(
            thought="Second thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        request3 = ThoughtRequest(
            thought="Final thought",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
            session_id=session_id,
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
        session_id = "test-session"
        request1 = ThoughtRequest(
            thought="Main thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        request2 = ThoughtRequest(
            thought="Branch A thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
            session_id=session_id,
        )
        request3 = ThoughtRequest(
            thought="Branch B thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-b",
            session_id=session_id,
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
        session_id = "test-session"
        # Create original thought first
        request0 = ThoughtRequest(
            thought="Original thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        server.process_thought(request0)

        # Now create multiple thoughts in same branch
        request1 = ThoughtRequest(
            thought="Branch thought 1",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
            session_id=session_id,
        )
        request2 = ThoughtRequest(
            thought="Branch thought 2",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-a",
            session_id=session_id,
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
        assert hasattr(response, "session_id")
        assert hasattr(response, "thought_number")
        assert hasattr(response, "total_thoughts")
        assert hasattr(response, "next_thought_needed")
        assert hasattr(response, "branches")
        assert hasattr(response, "thought_history_length")

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
        assert "session_id" in response_dict
        assert "thought_number" in response_dict
        assert "total_thoughts" in response_dict

    # Reference validation tests
    def test_accept_valid_revision_to_existing_thought(
        self, server: UltraThinkService
    ) -> None:
        """Should accept revision when referenced thought exists"""
        session_id = "test-session"
        # Add first thought
        request1 = ThoughtRequest(
            thought="Original thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        server.process_thought(request1)

        # Revise it - should succeed
        request2 = ThoughtRequest(
            thought="Revised thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
            session_id=session_id,
        )
        response = server.process_thought(request2)

        assert isinstance(response, ThoughtResponse)
        assert response.thought_history_length == 2

    def test_reject_revision_to_nonexistent_thought(
        self, server: UltraThinkService
    ) -> None:
        """Should reject revision when referenced thought does not exist"""
        request = ThoughtRequest(
            thought="Revising nonexistent thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=99,
        )

        with pytest.raises(ValueError) as exc_info:
            server.process_thought(request)

        assert "Cannot revise thought 99" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)

    def test_accept_valid_branch_from_existing_thought(
        self, server: UltraThinkService
    ) -> None:
        """Should accept branch when referenced thought exists"""
        session_id = "test-session"
        # Add first thought
        request1 = ThoughtRequest(
            thought="Main thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        server.process_thought(request1)

        # Branch from it - should succeed
        request2 = ThoughtRequest(
            thought="Branch thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
            session_id=session_id,
        )
        response = server.process_thought(request2)

        assert isinstance(response, ThoughtResponse)
        assert response.thought_history_length == 2
        assert "branch-a" in response.branches

    def test_reject_branch_from_nonexistent_thought(
        self, server: UltraThinkService
    ) -> None:
        """Should reject branch when referenced thought does not exist"""
        request = ThoughtRequest(
            thought="Branching from nonexistent thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=99,
            branch_id="branch-a",
        )

        with pytest.raises(ValueError) as exc_info:
            server.process_thought(request)

        assert "Cannot branch from thought 99" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)

    def test_accept_first_thought_without_references(
        self, server: UltraThinkService
    ) -> None:
        """Should accept first thought without revision or branch"""
        request = ThoughtRequest(
            thought="First thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.thought_history_length == 1

    def test_reject_first_thought_with_revision(
        self, server: UltraThinkService
    ) -> None:
        """Should reject first thought that tries to revise nonexistent thought"""
        request = ThoughtRequest(
            thought="First thought with revision",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
        )

        with pytest.raises(ValueError) as exc_info:
            server.process_thought(request)

        assert "Cannot revise thought 1" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)

    def test_allow_revision_and_branch_to_same_thought(
        self, server: UltraThinkService
    ) -> None:
        """Should allow multiple thoughts to reference the same thought"""
        session_id = "test-session"
        # Add first thought
        request1 = ThoughtRequest(
            thought="Main thought",
            thought_number=1,
            total_thoughts=4,
            next_thought_needed=True,
            session_id=session_id,
        )
        server.process_thought(request1)

        # Revise it
        request2 = ThoughtRequest(
            thought="Revision of main",
            thought_number=2,
            total_thoughts=4,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
            session_id=session_id,
        )
        server.process_thought(request2)

        # Branch from same thought - should succeed
        request3 = ThoughtRequest(
            thought="Branch from main",
            thought_number=3,
            total_thoughts=4,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="branch-a",
            session_id=session_id,
        )
        response = server.process_thought(request3)

        assert isinstance(response, ThoughtResponse)
        assert response.thought_history_length == 3

    # Multi-session tests
    def test_create_new_session_when_session_id_is_none(
        self, server: UltraThinkService
    ) -> None:
        """Should create new session with UUID when session_id is None"""
        request = ThoughtRequest(
            thought="First thought in new session",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=None,
        )

        response = server.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.session_id is not None
        assert len(response.session_id) == 36  # UUID format
        assert response.thought_history_length == 1

    def test_continue_existing_session_with_session_id(
        self, server: UltraThinkService
    ) -> None:
        """Should continue existing session when session_id is provided"""
        # Create first thought
        request1 = ThoughtRequest(
            thought="First thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=None,
        )
        response1 = server.process_thought(request1)
        session_id = response1.session_id

        # Continue session
        request2 = ThoughtRequest(
            thought="Second thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        response2 = server.process_thought(request2)

        assert response2.session_id == session_id
        assert response2.thought_history_length == 2

    def test_create_session_with_custom_session_id(
        self, server: UltraThinkService
    ) -> None:
        """Should create new session with custom session_id if not exists"""
        custom_id = "my-custom-session-123"
        request = ThoughtRequest(
            thought="First thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=custom_id,
        )

        response = server.process_thought(request)
        assert response.session_id == custom_id
        assert response.thought_history_length == 1

    def test_maintain_separate_sessions(self, server: UltraThinkService) -> None:
        """Should maintain separate thought histories for different sessions"""
        # Session 1
        request1a = ThoughtRequest(
            thought="Session 1 - Thought 1",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True,
            session_id="session-1",
        )
        response1a = server.process_thought(request1a)
        assert response1a.thought_history_length == 1

        # Session 2
        request2a = ThoughtRequest(
            thought="Session 2 - Thought 1",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True,
            session_id="session-2",
        )
        response2a = server.process_thought(request2a)
        assert response2a.thought_history_length == 1

        # Continue Session 1
        request1b = ThoughtRequest(
            thought="Session 1 - Thought 2",
            thought_number=2,
            total_thoughts=2,
            next_thought_needed=False,
            session_id="session-1",
        )
        response1b = server.process_thought(request1b)
        assert response1b.thought_history_length == 2

        # Continue Session 2
        request2b = ThoughtRequest(
            thought="Session 2 - Thought 2",
            thought_number=2,
            total_thoughts=2,
            next_thought_needed=False,
            session_id="session-2",
        )
        response2b = server.process_thought(request2b)
        assert response2b.thought_history_length == 2

    def test_session_resilience_create_if_not_exists(
        self, server: UltraThinkService
    ) -> None:
        """Should create new session if provided session_id doesn't exist (resilient recovery)"""
        # Try to continue a non-existent session
        request = ThoughtRequest(
            thought="Attempting to resume lost session",
            thought_number=5,
            total_thoughts=10,
            next_thought_needed=True,
            session_id="lost-session-id",
        )

        response = server.process_thought(request)
        # Should create new session with that ID
        assert response.session_id == "lost-session-id"
        # History length is 1 (new session), not 5
        assert response.thought_history_length == 1

    def test_multiple_sessions_maintain_separate_branches(
        self, server: UltraThinkService
    ) -> None:
        """Should maintain separate branches for different sessions"""
        # Session 1 - create branch
        request1a = ThoughtRequest(
            thought="Session 1 - Main",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id="session-1",
        )
        server.process_thought(request1a)

        request1b = ThoughtRequest(
            thought="Session 1 - Branch A",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            session_id="session-1",
            branch_from_thought=1,
            branch_id="branch-a",
        )
        response1 = server.process_thought(request1b)
        assert "branch-a" in response1.branches
        assert len(response1.branches) == 1

        # Session 2 - create different branch
        request2a = ThoughtRequest(
            thought="Session 2 - Main",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id="session-2",
        )
        server.process_thought(request2a)

        request2b = ThoughtRequest(
            thought="Session 2 - Branch B",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            session_id="session-2",
            branch_from_thought=1,
            branch_id="branch-b",
        )
        response2 = server.process_thought(request2b)
        assert "branch-b" in response2.branches
        assert len(response2.branches) == 1
        # Should not have branch-a
        assert "branch-a" not in response2.branches
