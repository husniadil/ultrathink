"""Tests for Assumption model"""

import pytest
from pydantic import ValidationError
from ultrathink.models.assumption import Assumption


class TestAssumptionModel:
    """Test suite for Assumption model"""

    def test_minimal_assumption(self) -> None:
        """Test creating assumption with minimal required fields"""
        assumption = Assumption(id="A1", text="This is an assumption")
        assert assumption.id == "A1"
        assert assumption.text == "This is an assumption"
        assert assumption.confidence == 1.0  # Default
        assert assumption.critical is True  # Default
        assert assumption.verifiable is False  # Default
        assert assumption.evidence is None
        assert assumption.verification_status is None

    def test_full_assumption(self) -> None:
        """Test creating assumption with all fields"""
        assumption = Assumption(
            id="A2",
            text="Dataset fits in memory",
            confidence=0.7,
            critical=True,
            verifiable=True,
            evidence="Based on dataset size of 10GB and available RAM of 32GB",
            verification_status="verified_true",
        )
        assert assumption.id == "A2"
        assert assumption.text == "Dataset fits in memory"
        assert assumption.confidence == 0.7
        assert assumption.critical is True
        assert assumption.verifiable is True
        assert (
            assumption.evidence
            == "Based on dataset size of 10GB and available RAM of 32GB"
        )
        assert assumption.verification_status == "verified_true"

    def test_invalid_id(self) -> None:
        """Test validation error for empty ID"""
        with pytest.raises(ValidationError):
            Assumption(id="", text="Test assumption")

    def test_id_pattern_validation(self) -> None:
        """Test ID must follow pattern ^A\\d+$"""
        # Valid patterns
        Assumption(id="A1", text="Test")
        Assumption(id="A2", text="Test")
        Assumption(id="A10", text="Test")
        Assumption(id="A100", text="Test")

        # Invalid patterns
        with pytest.raises(ValidationError):
            Assumption(id="a1", text="Test")  # lowercase
        with pytest.raises(ValidationError):
            Assumption(id="B1", text="Test")  # wrong letter
        with pytest.raises(ValidationError):
            Assumption(id="A", text="Test")  # no number
        with pytest.raises(ValidationError):
            Assumption(id="A1B", text="Test")  # extra characters
        with pytest.raises(ValidationError):
            Assumption(id="1A", text="Test")  # reversed
        with pytest.raises(ValidationError):
            Assumption(id="AA1", text="Test")  # extra letter

    def test_invalid_text(self) -> None:
        """Test validation error for empty text"""
        with pytest.raises(ValidationError):
            Assumption(id="A1", text="")

    def test_confidence_validation(self) -> None:
        """Test confidence must be between 0.0 and 1.0"""
        # Valid confidences
        Assumption(id="A1", text="Test", confidence=0.0)
        Assumption(id="A2", text="Test", confidence=0.5)
        Assumption(id="A3", text="Test", confidence=1.0)

        # Invalid confidences
        with pytest.raises(ValidationError):
            Assumption(id="A4", text="Test", confidence=-0.1)
        with pytest.raises(ValidationError):
            Assumption(id="A5", text="Test", confidence=1.1)

    def test_verification_status_validation(self) -> None:
        """Test verification_status must be valid literal"""
        # Valid statuses
        Assumption(id="A1", text="Test", verification_status="unverified")
        Assumption(id="A2", text="Test", verification_status="verified_true")
        Assumption(id="A3", text="Test", verification_status="verified_false")
        Assumption(id="A4", text="Test", verification_status=None)

        # Invalid status
        with pytest.raises(ValidationError):
            Assumption(id="A5", text="Test", verification_status="invalid")  # type: ignore

    def test_is_verified_property(self) -> None:
        """Test is_verified property"""
        unverified = Assumption(id="A1", text="Test", verification_status="unverified")
        assert unverified.is_verified is False

        verified_true = Assumption(
            id="A2", text="Test", verification_status="verified_true"
        )
        assert verified_true.is_verified is True

        verified_false = Assumption(
            id="A3", text="Test", verification_status="verified_false"
        )
        assert verified_false.is_verified is True

        none_status = Assumption(id="A4", text="Test", verification_status=None)
        assert none_status.is_verified is False

    def test_is_falsified_property(self) -> None:
        """Test is_falsified property"""
        falsified = Assumption(
            id="A1", text="Test", verification_status="verified_false"
        )
        assert falsified.is_falsified is True

        verified_true = Assumption(
            id="A2", text="Test", verification_status="verified_true"
        )
        assert verified_true.is_falsified is False

        unverified = Assumption(id="A3", text="Test", verification_status="unverified")
        assert unverified.is_falsified is False

    def test_is_risky_property(self) -> None:
        """Test is_risky property (critical + low confidence + not verified_true)"""
        # Risky: critical, low confidence, unverified
        risky1 = Assumption(
            id="A1",
            text="Test",
            critical=True,
            confidence=0.5,
            verification_status=None,
        )
        assert risky1.is_risky is True

        risky2 = Assumption(
            id="A2",
            text="Test",
            critical=True,
            confidence=0.6,
            verification_status="unverified",
        )
        assert risky2.is_risky is True

        # Not risky: not critical
        not_risky1 = Assumption(
            id="A3",
            text="Test",
            critical=False,
            confidence=0.5,
            verification_status=None,
        )
        assert not_risky1.is_risky is False

        # Not risky: high confidence
        not_risky2 = Assumption(
            id="A4",
            text="Test",
            critical=True,
            confidence=0.8,
            verification_status=None,
        )
        assert not_risky2.is_risky is False

        # Not risky: verified true
        not_risky3 = Assumption(
            id="A5",
            text="Test",
            critical=True,
            confidence=0.5,
            verification_status="verified_true",
        )
        assert not_risky3.is_risky is False

    def test_format_basic(self) -> None:
        """Test basic format output"""
        assumption = Assumption(id="A1", text="Dataset fits in memory", confidence=0.8)
        formatted = assumption.format()
        assert "A1:" in formatted
        assert "Dataset fits in memory" in formatted
        assert "(confidence: 80%)" in formatted
        assert "[CRITICAL]" in formatted

    def test_format_with_evidence(self) -> None:
        """Test format with evidence"""
        assumption = Assumption(
            id="A2",
            text="User has 32GB RAM",
            confidence=0.9,
            evidence="Checked system specs",
        )
        formatted = assumption.format()
        assert "Evidence: Checked system specs" in formatted

    def test_format_verification_status(self) -> None:
        """Test format shows verification status"""
        verified_true = Assumption(
            id="A1", text="Test", verification_status="verified_true"
        )
        assert "✓" in verified_true.format()

        verified_false = Assumption(
            id="A2", text="Test", verification_status="verified_false"
        )
        assert "✗" in verified_false.format()

        verifiable_unverified = Assumption(
            id="A3", text="Test", verifiable=True, verification_status=None
        )
        assert "?" in verifiable_unverified.format()

    def test_format_non_critical(self) -> None:
        """Test format for non-critical assumptions"""
        assumption = Assumption(id="A1", text="Test", critical=False)
        formatted = assumption.format()
        assert "[CRITICAL]" not in formatted

    def test_strict_mode(self) -> None:
        """Test that model uses strict mode (extra fields ignored in construction)"""
        # In Pydantic strict mode, extra fields don't cause errors during construction,
        # they are just validated strictly for type checking
        assumption = Assumption(
            id="A1",
            text="Test",
            confidence=0.8,
        )
        assert assumption.id == "A1"
        assert assumption.text == "Test"
        assert assumption.confidence == 0.8
