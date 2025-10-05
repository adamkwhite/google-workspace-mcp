import os
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.server import main, server  # noqa: E402


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
            notification_options=NotificationOptions(), experimental_capabilities={}
        )
        assert capabilities is not None


class TestServerIntegration:
    """Integration tests for server functionality"""

    @pytest.mark.asyncio
    async def test_handle_list_tools_with_mock_auth(self):
        """Test list_tools handler with mocked authentication"""
        with patch("src.server.auth_manager") as mock_auth:
            mock_auth.get_enabled_services.return_value = ["calendar"]

            # Import the handler function
            from src.server import handle_list_tools

            tools = await handle_list_tools()
            assert isinstance(tools, list)
            # Should at least have the configuration tool
            assert len(tools) >= 1

            # Check for configuration tool
            config_tool_found = any(
                tool.name == "get_mcp_configuration" for tool in tools
            )
            assert config_tool_found

    @pytest.mark.asyncio
    async def test_handle_call_tool_config(self):
        """Test calling the configuration tool"""
        with patch("src.server.auth_manager") as mock_auth:
            mock_scope_manager = Mock()
            mock_scope_manager.get_configuration_summary.return_value = {
                "config_file": "config/scopes.json",
                "enabled_services": ["calendar"],
                "is_valid": True,
            }
            mock_auth.get_scope_manager.return_value = mock_scope_manager

            from src.server import handle_call_tool

            result = await handle_call_tool("get_mcp_configuration", {})
            assert isinstance(result, list)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_handle_call_tool_calendar_disabled(self):
        """Test calendar tool when service is disabled"""
        with patch("src.server.auth_manager") as mock_auth:
            mock_auth.get_enabled_services.return_value = ["gmail"]  # Only Gmail
            mock_auth.creds = Mock()

            from src.server import handle_call_tool

            result = await handle_call_tool("create_calendar_event", {})
            assert isinstance(result, list)
            assert "not enabled" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_call_tool_gmail_disabled(self):
        """Test Gmail tool when service is disabled"""
        with patch("src.server.auth_manager") as mock_auth:
            mock_auth.get_enabled_services.return_value = ["calendar"]
            mock_auth.creds = Mock()

            from src.server import handle_call_tool

            result = await handle_call_tool("send_email", {})
            assert "not enabled" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_call_tool_docs_disabled(self):
        """Test Docs tool when service is disabled"""
        with patch("src.server.auth_manager") as mock_auth:
            mock_auth.get_enabled_services.return_value = ["calendar"]
            mock_auth.creds = Mock()

            from src.server import handle_call_tool

            result = await handle_call_tool("create_google_doc", {})
            assert "not enabled" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown(self):
        """Test handling of unknown tool"""
        from src.server import handle_call_tool

        result = await handle_call_tool("nonexistent_tool", {})
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_calendar_create_event(self):
        """Test calendar create event handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.calendar_tools"
        ) as mock_calendar:
            mock_auth.get_enabled_services.return_value = ["calendar"]
            mock_auth.creds = Mock()
            mock_calendar.create_event = AsyncMock(
                return_value={"id": "event-123", "summary": "Test"}
            )

            from src.server import handle_call_tool

            params = {
                "summary": "Test",
                "start_time": "2025-09-28T10:00:00",
                "end_time": "2025-09-28T11:00:00",
            }

            result = await handle_call_tool("create_calendar_event", params)
            assert "event-123" in result[0].text

    @pytest.mark.asyncio
    async def test_calendar_list_calendars(self):
        """Test calendar list calendars handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.calendar_tools"
        ) as mock_calendar:
            mock_auth.get_enabled_services.return_value = ["calendar"]
            mock_auth.creds = Mock()
            mock_calendar.list_calendars = AsyncMock(
                return_value={
                    "calendars": [{"id": "primary", "summary": "My Calendar"}]
                }
            )

            from src.server import handle_call_tool

            result = await handle_call_tool("list_calendars", {})
            assert "primary" in result[0].text

    @pytest.mark.asyncio
    async def test_calendar_list_events(self):
        """Test calendar list events handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.calendar_tools"
        ) as mock_calendar:
            mock_auth.get_enabled_services.return_value = ["calendar"]
            mock_auth.creds = Mock()
            mock_calendar.list_events = AsyncMock(
                return_value={"events": [{"id": "event-1", "summary": "Meeting"}]}
            )

            from src.server import handle_call_tool

            result = await handle_call_tool("list_calendar_events", {})
            assert "event-1" in result[0].text

    @pytest.mark.asyncio
    async def test_gmail_send_email(self):
        """Test Gmail send email handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.gmail_tools"
        ) as mock_gmail:
            mock_auth.get_enabled_services.return_value = ["gmail"]
            mock_auth.creds = Mock()
            mock_gmail.send_email = AsyncMock(
                return_value={"id": "msg-123", "to": "test@example.com"}
            )

            from src.server import handle_call_tool

            params = {"to": "test@example.com", "subject": "Test", "body": "Body"}

            result = await handle_call_tool("send_email", params)
            assert "msg-123" in result[0].text

    @pytest.mark.asyncio
    async def test_gmail_search_emails(self):
        """Test Gmail search emails handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.gmail_tools"
        ) as mock_gmail:
            mock_auth.get_enabled_services.return_value = ["gmail"]
            mock_auth.creds = Mock()
            mock_gmail.search_emails = AsyncMock(
                return_value={
                    "messages": [{"id": "msg-1", "subject": "Test"}],
                    "count": 1,
                }
            )

            from src.server import handle_call_tool

            result = await handle_call_tool("search_emails", {"query": "test"})
            assert "msg-1" in result[0].text

    @pytest.mark.asyncio
    async def test_gmail_create_draft(self):
        """Test Gmail create draft handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.gmail_tools"
        ) as mock_gmail:
            mock_auth.get_enabled_services.return_value = ["gmail"]
            mock_auth.creds = Mock()
            mock_gmail.create_draft = AsyncMock(
                return_value={"id": "draft-123", "subject": "Draft"}
            )

            from src.server import handle_call_tool

            params = {"to": "test@example.com", "subject": "Draft", "body": "Body"}

            result = await handle_call_tool("create_email_draft", params)
            assert "draft-123" in result[0].text

    @pytest.mark.asyncio
    async def test_docs_create_document(self):
        """Test Docs create document handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.docs_tools"
        ) as mock_docs:
            mock_auth.get_enabled_services.return_value = ["docs"]
            mock_auth.creds = Mock()
            mock_docs.create_document = AsyncMock(
                return_value={"documentId": "doc-123", "title": "Test"}
            )

            from src.server import handle_call_tool

            result = await handle_call_tool("create_google_doc", {"title": "Test"})
            assert "doc-123" in result[0].text

    @pytest.mark.asyncio
    async def test_docs_update_document(self):
        """Test Docs update document handler"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.docs_tools"
        ) as mock_docs:
            mock_auth.get_enabled_services.return_value = ["docs"]
            mock_auth.creds = Mock()
            mock_docs.update_document = AsyncMock(
                return_value={"documentId": "doc-123", "replies": []}
            )

            from src.server import handle_call_tool

            result = await handle_call_tool(
                "update_google_doc",
                {"document_id": "doc-123", "content": "New content"},
            )
            assert "doc-123" in result[0].text

    @pytest.mark.asyncio
    async def test_auth_initialization_on_first_call(self):
        """Test that auth initializes on first tool call"""
        with patch("src.server.auth_manager") as mock_auth, patch(
            "src.server.calendar_tools"
        ) as mock_calendar:
            mock_auth.get_enabled_services.return_value = ["calendar"]
            mock_auth.creds = None  # Not initialized
            mock_auth.initialize = AsyncMock()
            mock_calendar.create_event = AsyncMock(
                return_value={"id": "event-123", "summary": "Test"}
            )

            from src.server import handle_call_tool

            params = {
                "summary": "Test",
                "start_time": "2025-09-28T10:00:00",
                "end_time": "2025-09-28T11:00:00",
            }

            await handle_call_tool("create_calendar_event", params)

            # Auth should have been initialized
            mock_auth.initialize.assert_called_once()
