"""Tests for Google Docs tools."""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.docs import GoogleDocsTools  # noqa: E402


@pytest.fixture
def mock_auth_manager():
    """Create a mock auth manager."""
    auth_manager = Mock()
    auth_manager.get_credentials.return_value = Mock()
    return auth_manager


@pytest.fixture
def docs_tools(mock_auth_manager):
    """Create GoogleDocsTools instance with mocked auth."""
    return GoogleDocsTools(mock_auth_manager)


class TestGoogleDocsTools:
    """Test cases for Google Docs tools."""

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_create_document_basic(self, mock_build, docs_tools):
        """Test creating a basic document."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]

        # Mock document creation response
        mock_doc_response = {
            "documentId": "test-doc-id",
            "title": "Test Document",
            "revisionId": "rev-123",
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response

        # Test parameters
        params = {"title": "Test Document"}

        # Execute
        result = await docs_tools.create_document(params)

        # Verify basic functionality
        assert result["documentId"] == "test-doc-id"
        assert result["title"] == "Test Document"
        assert result["url"] == "https://docs.google.com/document/d/test-doc-id/edit"
        assert result["revisionId"] == "rev-123"

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_create_document_with_content(self, mock_build, docs_tools):
        """Test creating a document with initial content."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]

        # Mock responses
        mock_doc_response = {
            "documentId": "test-doc-id",
            "title": "Test Document",
            "revisionId": "rev-123",
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response
        mock_docs_service.documents().batchUpdate().execute.return_value = {}

        # Test parameters
        params = {"title": "Test Document", "content": "This is test content"}

        # Execute
        result = await docs_tools.create_document(params)

        # Verify
        assert result["documentId"] == "test-doc-id"
        assert result["title"] == "Test Document"

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_create_document_with_folder(self, mock_build, docs_tools):
        """Test creating a document in a specific folder."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]

        # Mock responses
        mock_doc_response = {
            "documentId": "test-doc-id",
            "title": "Test Document",
            "revisionId": "rev-123",
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response

        mock_file_response = {"parents": ["root"]}
        mock_drive_service.files().get().execute.return_value = mock_file_response
        mock_drive_service.files().update().execute.return_value = {"id": "test-doc-id"}

        # Test parameters
        params = {"title": "Test Document", "folder_id": "folder-123"}

        # Execute
        result = await docs_tools.create_document(params)

        # Verify
        assert result["documentId"] == "test-doc-id"
        assert result["folder_id"] == "folder-123"

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_create_document_with_sharing(self, mock_build, docs_tools):
        """Test creating a document and sharing it."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]

        # Mock document creation response
        mock_doc_response = {
            "documentId": "test-doc-id",
            "title": "Test Document",
            "revisionId": "rev-123",
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response

        # Mock sharing response
        mock_permission_response = {
            "id": "permission-id",
            "type": "user",
            "role": "writer",
        }
        mock_drive_service.permissions().create().execute.return_value = (
            mock_permission_response
        )

        # Test parameters
        params = {
            "title": "Test Document",
            "share_with": ["user1@example.com", "user2@example.com"],
        }

        # Execute
        result = await docs_tools.create_document(params)

        # Verify basic functionality
        assert result["documentId"] == "test-doc-id"
        assert result["shared_with"] == ["user1@example.com", "user2@example.com"]

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_update_document_append(self, mock_build, docs_tools):
        """Test updating a document by appending content."""
        mock_docs_service = MagicMock()
        mock_build.return_value = mock_docs_service

        # Mock existing document
        mock_doc = {
            "documentId": "doc-123",
            "body": {
                "content": [
                    {
                        "paragraph": {
                            "elements": [{"textRun": {"content": "Existing content\n"}}]
                        }
                    }
                ]
            },
        }
        mock_docs_service.documents().get().execute.return_value = mock_doc

        mock_update_response = {
            "documentId": "doc-123",
            "replies": [],
            "writeControl": {},
        }
        mock_docs_service.documents().batchUpdate().execute.return_value = (
            mock_update_response
        )

        params = {"document_id": "doc-123", "content": "New content"}

        result = await docs_tools.update_document(params)

        assert result["documentId"] == "doc-123"
        assert "replies" in result

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_update_document_at_index(self, mock_build, docs_tools):
        """Test updating a document at specific index."""
        mock_docs_service = MagicMock()
        mock_build.return_value = mock_docs_service

        mock_doc = {
            "documentId": "doc-456",
            "body": {
                "content": [
                    {
                        "paragraph": {
                            "elements": [{"textRun": {"content": "Existing content\n"}}]
                        }
                    }
                ]
            },
        }
        mock_docs_service.documents().get().execute.return_value = mock_doc

        mock_update_response = {"documentId": "doc-456", "replies": []}
        mock_docs_service.documents().batchUpdate().execute.return_value = (
            mock_update_response
        )

        params = {"document_id": "doc-456", "content": "Inserted text", "index": 5}

        result = await docs_tools.update_document(params)

        assert result["documentId"] == "doc-456"

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_update_document_replace_all(self, mock_build, docs_tools):
        """Test replacing all document content."""
        mock_docs_service = MagicMock()
        mock_build.return_value = mock_docs_service

        mock_doc = {
            "documentId": "doc-789",
            "body": {
                "content": [
                    {
                        "paragraph": {
                            "elements": [{"textRun": {"content": "Old content\n"}}]
                        }
                    }
                ]
            },
        }
        mock_docs_service.documents().get().execute.return_value = mock_doc

        mock_update_response = {"documentId": "doc-789", "replies": []}
        mock_docs_service.documents().batchUpdate().execute.return_value = (
            mock_update_response
        )

        params = {
            "document_id": "doc-789",
            "content": "Completely new content",
            "replace_all": True,
        }

        result = await docs_tools.update_document(params)

        assert result["documentId"] == "doc-789"
        assert "replies" in result

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_create_document_error_handling(self, mock_build, docs_tools):
        """Test error handling when creating document."""
        from googleapiclient.errors import HttpError

        mock_docs_service = MagicMock()
        mock_build.return_value = mock_docs_service

        # Mock HTTP error
        mock_docs_service.documents().create().execute.side_effect = HttpError(
            resp=Mock(status=403), content=b"Forbidden"
        )

        params = {"title": "Test Document"}

        with pytest.raises(HttpError):
            await docs_tools.create_document(params)

    @pytest.mark.asyncio
    @patch("src.tools.docs.build")
    async def test_update_document_error_handling(self, mock_build, docs_tools):
        """Test error handling when updating document."""
        from googleapiclient.errors import HttpError

        mock_docs_service = MagicMock()
        mock_build.return_value = mock_docs_service

        # Mock HTTP error on get
        mock_docs_service.documents().get().execute.side_effect = HttpError(
            resp=Mock(status=404), content=b"Not Found"
        )

        params = {"document_id": "nonexistent", "content": "New content"}

        with pytest.raises(HttpError):
            await docs_tools.update_document(params)
