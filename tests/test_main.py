"""Tests for main module (tool function and CLI entry point)"""

import os
from unittest.mock import patch
from ultrathink.main import ultrathink
from ultrathink.dto import ThoughtRequest
from ultrathink.__main__ import main


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


class TestCLIEntryPoint:
    """Test suite for CLI entry point"""

    def test_main_function_calls_mcp_run(self) -> None:
        """Should call mcp.run() when main() is invoked"""
        with patch("ultrathink.main.mcp.run") as mock_run:
            main()
            mock_run.assert_called_once()
