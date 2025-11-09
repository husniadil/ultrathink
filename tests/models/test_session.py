import os
from typing import Generator
import pytest
from ultrathink.services.thinking_service import UltraThinkService
from ultrathink.models.thought import ThoughtRequest, ThoughtResponse
from ultrathink.models.assumption import Assumption


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


class TestAssumptionTracking:
    """Test suite for assumption tracking functionality"""

    @pytest.fixture
    def service(self) -> UltraThinkService:
        """Create a service instance"""
        return UltraThinkService()

    def test_add_assumption_to_thought(self, service: UltraThinkService) -> None:
        """Should track assumptions added to thoughts"""
        assumption = Assumption(
            id="A1", text="Dataset fits in memory", confidence=0.8, critical=True
        )

        request = ThoughtRequest(
            thought="We can use in-memory processing",
            total_thoughts=3,
            assumptions=[assumption],
        )

        response = service.process_thought(request)
        assert "A1" in response.all_assumptions
        assert response.all_assumptions["A1"].text == "Dataset fits in memory"
        assert response.all_assumptions["A1"].confidence == 0.8

    def test_multiple_assumptions_in_thought(self, service: UltraThinkService) -> None:
        """Should track multiple assumptions from single thought"""
        assumptions = [
            Assumption(id="A1", text="Dataset fits in memory", confidence=0.8),
            Assumption(id="A2", text="Low latency network", confidence=0.9),
        ]

        request = ThoughtRequest(
            thought="We can use distributed caching",
            total_thoughts=3,
            assumptions=assumptions,
        )

        response = service.process_thought(request)
        assert len(response.all_assumptions) == 2
        assert "A1" in response.all_assumptions
        assert "A2" in response.all_assumptions

    def test_assumptions_persist_across_thoughts(
        self, service: UltraThinkService
    ) -> None:
        """Should persist assumptions across multiple thoughts in same session"""
        session_id = "test-session"

        # First thought with assumption
        request1 = ThoughtRequest(
            thought="Initial thought",
            total_thoughts=3,
            session_id=session_id,
            assumptions=[Assumption(id="A1", text="Test assumption", confidence=0.7)],
        )
        response1 = service.process_thought(request1)
        assert "A1" in response1.all_assumptions

        # Second thought without new assumptions
        request2 = ThoughtRequest(
            thought="Second thought",
            total_thoughts=3,
            session_id=session_id,
        )
        response2 = service.process_thought(request2)
        assert "A1" in response2.all_assumptions  # Should still be there

    def test_depends_on_assumptions(self, service: UltraThinkService) -> None:
        """Should track assumption dependencies"""
        session_id = "test-session"

        # First thought with assumptions
        request1 = ThoughtRequest(
            thought="Initial thought",
            total_thoughts=3,
            session_id=session_id,
            assumptions=[Assumption(id="A1", text="Test assumption")],
        )
        service.process_thought(request1)

        # Second thought depending on A1
        request2 = ThoughtRequest(
            thought="Building on A1",
            total_thoughts=3,
            session_id=session_id,
            depends_on_assumptions=["A1"],
        )
        response2 = service.process_thought(request2)
        assert "A1" in response2.all_assumptions

    def test_depends_on_nonexistent_assumption_error(
        self, service: UltraThinkService
    ) -> None:
        """Should raise error when depending on non-existent assumption"""
        request = ThoughtRequest(
            thought="Test thought",
            total_thoughts=3,
            depends_on_assumptions=["A99"],  # Doesn't exist
        )

        with pytest.raises(ValueError) as exc_info:
            service.process_thought(request)
        assert "Cannot depend on assumption A99" in str(exc_info.value)
        assert "assumption not found" in str(exc_info.value)

    def test_invalidate_assumption(self, service: UltraThinkService) -> None:
        """Should mark assumptions as falsified when invalidated"""
        session_id = "test-session"

        # First thought with assumption
        request1 = ThoughtRequest(
            thought="Assuming dataset is small",
            total_thoughts=3,
            session_id=session_id,
            assumptions=[Assumption(id="A1", text="Dataset < 1GB", confidence=0.6)],
        )
        response1 = service.process_thought(request1)
        assert response1.all_assumptions["A1"].verification_status is None

        # Second thought invalidates the assumption
        request2 = ThoughtRequest(
            thought="Actually, dataset is 10GB",
            total_thoughts=3,
            session_id=session_id,
            invalidates_assumptions=["A1"],
        )
        response2 = service.process_thought(request2)
        assert response2.all_assumptions["A1"].verification_status == "verified_false"
        assert "A1" in response2.falsified_assumptions

    def test_risky_assumptions_detection(self, service: UltraThinkService) -> None:
        """Should detect risky assumptions (critical + low confidence + unverified)"""
        risky = Assumption(
            id="A1",
            text="API will respond in <100ms",
            confidence=0.5,  # Low confidence
            critical=True,  # Critical
            verification_status=None,  # Unverified
        )

        request = ThoughtRequest(
            thought="Building low-latency system",
            total_thoughts=3,
            assumptions=[risky],
        )

        response = service.process_thought(request)
        assert "A1" in response.risky_assumptions

    def test_non_risky_assumptions(self, service: UltraThinkService) -> None:
        """Should not flag non-risky assumptions"""
        # High confidence
        assumption1 = Assumption(
            id="A1",
            text="Test",
            confidence=0.9,
            critical=True,
            verification_status=None,
        )

        # Not critical
        assumption2 = Assumption(
            id="A2",
            text="Test",
            confidence=0.5,
            critical=False,
            verification_status=None,
        )

        # Verified
        assumption3 = Assumption(
            id="A3",
            text="Test",
            confidence=0.5,
            critical=True,
            verification_status="verified_true",
        )

        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            assumptions=[assumption1, assumption2, assumption3],
        )

        response = service.process_thought(request)
        assert len(response.risky_assumptions) == 0

    def test_update_existing_assumption(self, service: UltraThinkService) -> None:
        """Should update assumption if same ID appears again"""
        session_id = "test-session"

        # First thought with assumption
        request1 = ThoughtRequest(
            thought="Initial thought",
            total_thoughts=3,
            session_id=session_id,
            assumptions=[Assumption(id="A1", text="Original text", confidence=0.5)],
        )
        response1 = service.process_thought(request1)
        assert response1.all_assumptions["A1"].text == "Original text"
        assert response1.all_assumptions["A1"].confidence == 0.5

        # Second thought updates the assumption
        request2 = ThoughtRequest(
            thought="Updated thought",
            total_thoughts=3,
            session_id=session_id,
            assumptions=[Assumption(id="A1", text="Updated text", confidence=0.9)],
        )
        response2 = service.process_thought(request2)
        assert response2.all_assumptions["A1"].text == "Updated text"
        assert response2.all_assumptions["A1"].confidence == 0.9

    def test_verify_assumption(self, service: UltraThinkService) -> None:
        """Should mark assumption as verified when explicitly set"""
        request = ThoughtRequest(
            thought="Verified assumption",
            total_thoughts=3,
            assumptions=[
                Assumption(
                    id="A1",
                    text="Dataset fits in memory",
                    verification_status="verified_true",
                )
            ],
        )

        response = service.process_thought(request)
        assert response.all_assumptions["A1"].verification_status == "verified_true"
        assert "A1" not in response.falsified_assumptions

    def test_multiple_sessions_isolated_assumptions(
        self, service: UltraThinkService
    ) -> None:
        """Should keep assumptions isolated between different sessions"""
        # Session 1
        request1 = ThoughtRequest(
            thought="Session 1 thought",
            total_thoughts=3,
            session_id="session-1",
            assumptions=[Assumption(id="A1", text="Session 1 assumption")],
        )
        response1 = service.process_thought(request1)
        assert "A1" in response1.all_assumptions

        # Session 2
        request2 = ThoughtRequest(
            thought="Session 2 thought",
            total_thoughts=3,
            session_id="session-2",
            assumptions=[Assumption(id="A2", text="Session 2 assumption")],
        )
        response2 = service.process_thought(request2)
        assert "A2" in response2.all_assumptions
        assert "A1" not in response2.all_assumptions  # Should not have A1

    def test_assumption_logging(self, service: UltraThinkService) -> None:
        """Should log thoughts with assumptions properly"""
        assumption = Assumption(
            id="A1",
            text="Test assumption",
            confidence=0.8,
            critical=True,
            evidence="Based on testing",
        )

        request = ThoughtRequest(
            thought="Thought with assumption",
            total_thoughts=3,
            assumptions=[assumption],
        )

        # Should not raise any errors
        response = service.process_thought(request)
        assert isinstance(response, ThoughtResponse)
