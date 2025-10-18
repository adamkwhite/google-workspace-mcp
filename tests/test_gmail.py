"""Tests for Gmail tools."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from tools.gmail import GmailTools


@pytest.fixture
def mock_auth_manager():
    """Create a mock auth manager."""
    auth_manager = Mock()
    auth_manager.get_credentials.return_value = Mock()
    return auth_manager


@pytest.fixture
def gmail_tools(mock_auth_manager):
    """Create GmailTools instance with mocked auth."""
    return GmailTools(mock_auth_manager)


class TestGmailTools:
    """Test cases for Gmail tools."""

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_send_email_basic(self, mock_build, gmail_tools):
        """Test sending a basic email."""
        # Setup mocks
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock send response
        mock_send_response = {
            "id": "msg-123",
            "threadId": "thread-123",
            "labelIds": ["SENT"],
        }
        mock_service.users().messages().send().execute.return_value = mock_send_response

        # Test parameters
        params = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Test body",
        }

        # Execute
        result = gmail_tools.send_email(params)

        # Verify
        assert result["id"] == "msg-123"
        assert result["threadId"] == "thread-123"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_send_email_with_cc_bcc(self, mock_build, gmail_tools):
        """Test sending email with CC and BCC."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_send_response = {"id": "msg-123", "threadId": "thread-123"}
        mock_service.users().messages().send().execute.return_value = mock_send_response

        params = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
            "cc": "cc@example.com",
            "bcc": ["bcc1@example.com", "bcc2@example.com"],
        }

        result = gmail_tools.send_email(params)
        assert result["id"] == "msg-123"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_send_email_html(self, mock_build, gmail_tools):
        """Test sending HTML email."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_send_response = {"id": "msg-123"}
        mock_service.users().messages().send().execute.return_value = mock_send_response

        params = {
            "to": "test@example.com",
            "subject": "HTML Test",
            "body": "<h1>Hello</h1>",
            "html": True,
        }

        result = gmail_tools.send_email(params)
        assert result["id"] == "msg-123"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_search_emails_basic(self, mock_build, gmail_tools):
        """Test searching emails."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock search results
        mock_list_response = {
            "messages": [
                {"id": "msg1", "threadId": "thread1"},
                {"id": "msg2", "threadId": "thread2"},
            ]
        }
        mock_service.users().messages().list().execute.return_value = mock_list_response

        # Mock get message responses
        mock_message_1 = {
            "id": "msg1",
            "threadId": "thread1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Test Subject 1"},
                    {"name": "Date", "value": "2025-01-01"},
                ]
            },
            "snippet": "Message snippet 1",
        }
        mock_service.users().messages().get().execute.return_value = mock_message_1

        params = {"query": "from:sender@example.com", "max_results": 10}

        result = gmail_tools.search_emails(params)

        assert "messages" in result
        assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_search_emails_with_body(self, mock_build, gmail_tools):
        """Test searching emails with body included."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_list_response = {"messages": [{"id": "msg1", "threadId": "thread1"}]}
        mock_service.users().messages().list().execute.return_value = mock_list_response

        mock_message = {
            "id": "msg1",
            "threadId": "thread1",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "test@example.com"},
                    {"name": "Date", "value": "2025-01-01"},
                ],
                "parts": [{"mimeType": "text/plain", "body": {"data": "VGVzdCBib2R5"}}],
            },
            "snippet": "snippet",
        }
        mock_service.users().messages().get().execute.return_value = mock_message

        params = {"query": "test", "include_body": True}

        result = gmail_tools.search_emails(params)
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_create_draft_basic(self, mock_build, gmail_tools):
        """Test creating email draft."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_draft_response = {
            "id": "draft-123",
            "message": {"id": "msg-123", "threadId": "thread-123"},
        }
        mock_service.users().drafts().create().execute.return_value = (
            mock_draft_response
        )

        params = {
            "to": "test@example.com",
            "subject": "Draft Subject",
            "body": "Draft body",
        }

        result = gmail_tools.create_draft(params)

        assert result["id"] == "draft-123"
        assert result["message"]["id"] == "msg-123"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_create_draft_with_cc_bcc(self, mock_build, gmail_tools):
        """Test creating draft with CC and BCC."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_draft_response = {"id": "draft-123", "message": {"id": "msg-123"}}
        mock_service.users().drafts().create().execute.return_value = (
            mock_draft_response
        )

        params = {
            "to": ["to1@example.com", "to2@example.com"],
            "subject": "Test",
            "body": "Body",
            "cc": "cc@example.com",
            "bcc": "bcc@example.com",
        }

        result = gmail_tools.create_draft(params)
        assert result["id"] == "draft-123"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_send_email_error_handling(self, mock_build, gmail_tools):
        """Test error handling when sending email."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock HTTP error
        mock_service.users().messages().send().execute.side_effect = HttpError(
            resp=Mock(status=400), content=b"Bad Request"
        )

        params = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        with pytest.raises(HttpError):
            gmail_tools.send_email(params)

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_search_emails_error_handling(self, mock_build, gmail_tools):
        """Test error handling when searching emails."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock HTTP error
        mock_service.users().messages().list().execute.side_effect = HttpError(
            resp=Mock(status=403), content=b"Forbidden"
        )

        params = {"query": "test"}

        with pytest.raises(HttpError):
            gmail_tools.search_emails(params)

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_create_draft_error_handling(self, mock_build, gmail_tools):
        """Test error handling when creating draft."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock HTTP error
        mock_service.users().drafts().create().execute.side_effect = HttpError(
            resp=Mock(status=500), content=b"Internal Server Error"
        )

        params = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        with pytest.raises(HttpError):
            gmail_tools.create_draft(params)
