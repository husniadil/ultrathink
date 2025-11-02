"""Tests for MCP server tool function"""

import os
from ultrathink.interface.mcp_server import ultrathink
from ultrathink.models.thought import ThoughtRequest


class TestUltraThinkTool:
    """Test suite for ultrathink tool function"""

    def test_ultrathink_tool_via_fn_attribute(self) -> None:
        """Should return ThoughtResponse when calling ultrathink.fn()"""
        os.environ["DISABLE_THOUGHT_LOGGING"] = "true"

        # Test with flat parameters (unpack from ThoughtRequest)
        request = ThoughtRequest(
            thought="Test thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
        )

        # Access the wrapped function via .fn attribute with unpacked parameters
        response = ultrathink.fn(**request.model_dump())
        assert response.thought_number == 1
        assert response.total_thoughts == 1
        assert response.next_thought_needed is False

    def test_ultrathink_tool_with_auto_assigned_next_thought(self) -> None:
        """Should auto-assign next_thought_needed when omitted"""
        os.environ["DISABLE_THOUGHT_LOGGING"] = "true"

        # Test without next_thought_needed - should auto-assign
        request = ThoughtRequest(
            thought="Test thought",
            thought_number=1,
            total_thoughts=3,
            # next_thought_needed omitted
        )

        response = ultrathink.fn(**request.model_dump())
        assert response.thought_number == 1
        assert response.total_thoughts == 3
        assert response.next_thought_needed is True  # Auto-assigned
