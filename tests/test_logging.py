import os
from typing import Generator
import pytest
from ultrathink.service import UltraThinkService
from ultrathink.dto import ThoughtRequest, ThoughtResponse


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
        request = ThoughtRequest(
            thought="Revised thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
        )

        response = server_with_logging.process_thought(request)
        assert isinstance(response, ThoughtResponse)

    def test_format_and_log_branch_thoughts(
        self, server_with_logging: UltraThinkService
    ) -> None:
        """Should format and log branch thoughts"""
        request = ThoughtRequest(
            thought="Branch thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            branch_from_thought=1,
            branch_id="branch-a",
        )

        response = server_with_logging.process_thought(request)
        assert isinstance(response, ThoughtResponse)
