"""Tests for CLI entry point"""

from unittest.mock import patch
from ultrathink.__main__ import main


class TestCLIEntryPoint:
    """Test suite for CLI entry point"""

    def test_main_function_calls_mcp_run(self) -> None:
        """Should call mcp.run() when main() is invoked"""
        with patch("ultrathink.infrastructure.mcp.server.mcp.run") as mock_run:
            main()
            mock_run.assert_called_once()
