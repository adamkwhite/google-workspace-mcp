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
def mock_scope_manager():
    """Create a mock scope manager."""
    scope_manager = Mock()
    scope_manager.get_restricted_label.return_value = None
    return scope_manager


@pytest.fixture
def mock_scope_manager_with_restriction():
    """Create a mock scope manager with label restriction."""
    scope_manager = Mock()
    scope_manager.get_restricted_label.return_value = "Jobs"
    return scope_manager


@pytest.fixture
def gmail_tools(mock_auth_manager):
    """Create GmailTools instance with mocked auth."""
    return GmailTools(mock_auth_manager)


@pytest.fixture
def gmail_tools_with_scope(mock_auth_manager, mock_scope_manager):
    """Create GmailTools instance with scope manager."""
    return GmailTools(mock_auth_manager, mock_scope_manager)


@pytest.fixture
def gmail_tools_restricted(mock_auth_manager, mock_scope_manager_with_restriction):
    """Create GmailTools instance with label restriction."""
    return GmailTools(mock_auth_manager, mock_scope_manager_with_restriction)


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


class TestGmailLabelFiltering:
    """Test cases for Gmail label-based access restriction."""

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_label_initialization_success(
        self, mock_build, gmail_tools_restricted
    ):
        """Test successful label resolution."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response
        mock_labels_response = {
            "labels": [
                {"id": "Label_1", "name": "Jobs"},
                {"id": "Label_2", "name": "Personal"},
                {"id": "INBOX", "name": "INBOX"},
            ]
        }
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        # Mock search response
        mock_list_response = {"messages": []}
        mock_service.users().messages().list().execute.return_value = mock_list_response

        # Execute search to trigger label initialization
        gmail_tools_restricted.search_emails({"query": "test"})

        # Verify label was resolved
        assert gmail_tools_restricted._restricted_label_id == "Label_1"
        assert gmail_tools_restricted._label_initialized is True

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_label_not_found_error(self, mock_build, gmail_tools_restricted):
        """Test error when configured label doesn't exist."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response without "Jobs" label
        mock_labels_response = {
            "labels": [
                {"id": "Label_2", "name": "Personal"},
                {"id": "INBOX", "name": "INBOX"},
            ]
        }
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        # Execute search to trigger label initialization
        with pytest.raises(ValueError) as exc_info:
            gmail_tools_restricted.search_emails({"query": "test"})

        assert "Configured Gmail label 'Jobs' not found" in str(exc_info.value)
        assert "Available labels:" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_no_restriction_configured(self, mock_build, gmail_tools_with_scope):
        """Test normal operation when no restriction is configured."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock search response
        mock_list_response = {"messages": []}
        mock_service.users().messages().list().execute.return_value = mock_list_response

        # Execute search
        gmail_tools_with_scope.search_emails({"query": "test"})

        # Verify no label filtering applied
        assert gmail_tools_with_scope._restricted_label_id is None
        assert gmail_tools_with_scope._label_initialized is True

        # Verify query passed through unchanged
        call_args = mock_service.users().messages().list.call_args
        assert call_args[1]["q"] == "test"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_label_caching(self, mock_build, gmail_tools_restricted):
        """Test that labels are cached and not fetched repeatedly."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response
        mock_labels_response = {
            "labels": [
                {"id": "Label_1", "name": "Jobs"},
            ]
        }
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        # Mock search response
        mock_list_response = {"messages": []}
        mock_service.users().messages().list().execute.return_value = mock_list_response

        # Execute search twice
        gmail_tools_restricted.search_emails({"query": "test1"})
        gmail_tools_restricted.search_emails({"query": "test2"})

        # Verify labels.list() was called only once
        assert mock_service.users().labels().list().execute.call_count == 1

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_search_query_enhancement_with_restriction(
        self, mock_build, gmail_tools_restricted
    ):
        """Test that search query is enhanced with label filter."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response
        mock_labels_response = {"labels": [{"id": "Label_1", "name": "Jobs"}]}
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        # Mock search response
        mock_list_response = {"messages": []}
        mock_service.users().messages().list().execute.return_value = mock_list_response

        # Execute search with query
        gmail_tools_restricted.search_emails({"query": "from:example@example.com"})

        # Verify query was enhanced with label filter
        call_args = mock_service.users().messages().list.call_args
        assert call_args[1]["q"] == "from:example@example.com label:Jobs"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_search_empty_query_becomes_label_filter(
        self, mock_build, gmail_tools_restricted
    ):
        """Test that empty query becomes just the label filter."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response
        mock_labels_response = {"labels": [{"id": "Label_1", "name": "Jobs"}]}
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        # Mock search response
        mock_list_response = {"messages": []}
        mock_service.users().messages().list().execute.return_value = mock_list_response

        # Execute search with empty query
        gmail_tools_restricted.search_emails({"query": ""})

        # Verify query is just the label filter
        call_args = mock_service.users().messages().list.call_args
        assert call_args[1]["q"] == "label:Jobs"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_send_email_blocked_with_restriction(
        self, mock_build, gmail_tools_restricted
    ):
        """Test that send_email is blocked when restriction is enabled."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response
        mock_labels_response = {"labels": [{"id": "Label_1", "name": "Jobs"}]}
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        params = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        # Execute send_email
        with pytest.raises(ValueError) as exc_info:
            gmail_tools_restricted.send_email(params)

        assert "Cannot send email when Gmail is restricted to label 'Jobs'" in str(
            exc_info.value
        )

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_create_draft_blocked_with_restriction(
        self, mock_build, gmail_tools_restricted
    ):
        """Test that create_draft is blocked when restriction is enabled."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock labels.list() response
        mock_labels_response = {"labels": [{"id": "Label_1", "name": "Jobs"}]}
        mock_service.users().labels().list().execute.return_value = mock_labels_response

        params = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        # Execute create_draft
        with pytest.raises(ValueError) as exc_info:
            gmail_tools_restricted.create_draft(params)

        assert "Cannot create draft when Gmail is restricted to label 'Jobs'" in str(
            exc_info.value
        )

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_send_email_allowed_without_restriction(
        self, mock_build, gmail_tools_with_scope
    ):
        """Test that send_email works when no restriction is configured."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_send_response = {
            "id": "msg-123",
            "threadId": "thread-123",
            "labelIds": ["SENT"],
        }
        mock_service.users().messages().send().execute.return_value = mock_send_response

        params = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        # Execute send_email
        result = gmail_tools_with_scope.send_email(params)

        # Should succeed
        assert result["id"] == "msg-123"

    @pytest.mark.asyncio
    @patch("tools.gmail.build")
    async def test_create_draft_allowed_without_restriction(
        self, mock_build, gmail_tools_with_scope
    ):
        """Test that create_draft works when no restriction is configured."""
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
            "subject": "Test",
            "body": "Body",
        }

        # Execute create_draft
        result = gmail_tools_with_scope.create_draft(params)

        # Should succeed
        assert result["id"] == "draft-123"
