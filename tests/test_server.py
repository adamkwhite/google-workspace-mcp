import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.server import server, main

class TestMCPServer:

    def test_server_instance_exists(self):
        """Test that server instance is properly initialized"""
        assert server is not None
        assert server.name == "google-workspace-mcp"

    def test_main_function_exists(self):
        """Test that main function is defined"""
        assert callable(main)

    @pytest.mark.asyncio
    async def test_server_capabilities(self):
        """Test server has expected capabilities"""
        from mcp.server import NotificationOptions
        capabilities = server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
        assert capabilities is not None

class TestServerIntegration:
    """Integration tests for server functionality"""

    @pytest.mark.asyncio
    async def test_handle_list_tools_with_mock_auth(self):
        """Test list_tools handler with mocked authentication"""
        with patch('src.server.auth_manager') as mock_auth:
            mock_auth.get_enabled_services.return_value = ['calendar']

            # Import the handler function
            from src.server import handle_list_tools

            tools = await handle_list_tools()
            assert isinstance(tools, list)
            # Should at least have the configuration tool
            assert len(tools) >= 1

            # Check for configuration tool
            config_tool_found = any(tool.name == "get_mcp_configuration" for tool in tools)
            assert config_tool_found

    @pytest.mark.asyncio
    async def test_handle_call_tool_config(self):
        """Test calling the configuration tool"""
        with patch('src.server.auth_manager') as mock_auth:
            mock_scope_manager = Mock()
            mock_scope_manager.get_configuration_summary.return_value = {
                'config_file': 'config/scopes.json',
                'enabled_services': ['calendar'],
                'is_valid': True
            }
            mock_auth.get_scope_manager.return_value = mock_scope_manager

            from src.server import handle_call_tool

            result = await handle_call_tool("get_mcp_configuration", {})
            assert isinstance(result, list)
            assert len(result) > 0