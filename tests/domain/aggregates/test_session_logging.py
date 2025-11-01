import os
from typing import Generator
import pytest
from ultrathink.application.services.thinking_service import UltraThinkService
from ultrathink.dto.request import ThoughtRequest
from ultrathink.dto.response import ThoughtResponse


class TestLogging:
    """Test suite for logging and formatting functionality"""

    @pytest.fixture
    def server_with_logging(self) -> Generator[UltraThinkService, None, None]:
        """Create a server instance with logging enabled"""
        if "DISABLE_THOUGHT_LOGGING" in os.environ:
            del os.environ["DISABLE_THOUGHT_LOGGING"]
        server = UltraThinkService()
        os.environ["DISABLE_THOUGHT_LOGGING"] = "true"
        yield server

    def test_format_and_log_regular_thoughts(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log regular thoughts"""
        request = ThoughtRequest(
            thought="Test thought with logging",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        response = server_with_logging.process_thought(request)
        assert isinstance(response, ThoughtResponse)

    def test_format_and_log_revision_thoughts(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log revision thoughts"""
        session_id = "test-session"
        # Create original thought first
        request1 = ThoughtRequest(
            thought="Original thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        server_with_logging.process_thought(request1)

        # Now revise it
        request2 = ThoughtRequest(
            thought="Revised thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
            session_id=session_id,
        )

        response = server_with_logging.process_thought(request2)
        assert isinstance(response, ThoughtResponse)

    def test_format_and_log_branch_thoughts(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log branch thoughts"""
        session_id = "test-session"
        # Create original thought first
        request1 = ThoughtRequest(
            thought="Original thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            session_id=session_id,
        )
        server_with_logging.process_thought(request1)

        # Now branch from it
        request2 = ThoughtRequest(
            thought="Branch thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-a",
            session_id=session_id,
        )

        response = server_with_logging.process_thought(request2)
        assert isinstance(response, ThoughtResponse)

    def test_format_and_log_with_uncertainty_notes(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log thoughts with uncertainty_notes"""
        request = ThoughtRequest(
            thought="Test thought with uncertainty",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.7,
            uncertainty_notes="Not sure about edge cases",
        )

        response = server_with_logging.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.uncertainty_notes == "Not sure about edge cases"

    def test_format_and_log_with_outcome(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log thoughts with outcome"""
        request = ThoughtRequest(
            thought="Test thought with outcome",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            outcome="Bug fixed successfully",
        )

        response = server_with_logging.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.outcome == "Bug fixed successfully"

    def test_format_and_log_with_both_new_fields(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log thoughts with both uncertainty_notes and outcome"""
        request = ThoughtRequest(
            thought="Test thought with both new fields",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.85,
            uncertainty_notes="Need more testing",
            outcome="Partial success",
        )

        response = server_with_logging.process_thought(request)
        assert isinstance(response, ThoughtResponse)
        assert response.confidence == 0.85
        assert response.uncertainty_notes == "Need more testing"
        assert response.outcome == "Partial success"
