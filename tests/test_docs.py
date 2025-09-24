"""Tests for Google Docs tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.docs import GoogleDocsTools


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
    @patch('tools.docs.build')
    async def test_create_document_basic(self, mock_build, docs_tools):
        """Test creating a basic document."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]
        
        # Mock document creation response
        mock_doc_response = {
            'documentId': 'test-doc-id',
            'title': 'Test Document',
            'revisionId': 'rev-123'
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response
        
        # Test parameters
        params = {
            'title': 'Test Document'
        }
        
        # Execute
        result = await docs_tools.create_document(params)
        
        # Verify
        assert result['id'] == 'test-doc-id'
        assert result['title'] == 'Test Document'
        assert result['url'] == 'https://docs.google.com/document/d/test-doc-id/edit'
        assert result['revisionId'] == 'rev-123'
        
        # Verify API calls
        mock_docs_service.documents().create.assert_called_once_with(
            body={'title': 'Test Document'}
        )
        
    @pytest.mark.asyncio
    @patch('tools.docs.build')
    async def test_create_document_with_content(self, mock_build, docs_tools):
        """Test creating a document with initial content."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]
        
        # Mock document creation response
        mock_doc_response = {
            'documentId': 'test-doc-id',
            'title': 'Test Document',
            'revisionId': 'rev-123'
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response
        
        # Test parameters
        params = {
            'title': 'Test Document',
            'content': 'This is the initial content of the document.'
        }
        
        # Execute
        result = await docs_tools.create_document(params)
        
        # Verify batchUpdate was called with content
        expected_requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': 'This is the initial content of the document.'
            }
        }]
        
        mock_docs_service.documents().batchUpdate.assert_called_once_with(
            documentId='test-doc-id',
            body={'requests': expected_requests}
        )
        
    @pytest.mark.asyncio
    @patch('tools.docs.build')
    async def test_create_document_with_folder(self, mock_build, docs_tools):
        """Test creating a document in a specific folder."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]
        
        # Mock responses
        mock_doc_response = {
            'documentId': 'test-doc-id',
            'title': 'Test Document',
            'revisionId': 'rev-123'
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response
        
        mock_file_response = {'parents': ['root']}
        mock_drive_service.files().get().execute.return_value = mock_file_response
        
        # Test parameters
        params = {
            'title': 'Test Document',
            'folder_id': 'folder-123'
        }
        
        # Execute
        result = await docs_tools.create_document(params)
        
        # Verify folder operations
        mock_drive_service.files().get.assert_called_once_with(
            fileId='test-doc-id',
            fields='parents'
        )
        
        mock_drive_service.files().update.assert_called_once_with(
            fileId='test-doc-id',
            addParents='folder-123',
            removeParents='root',
            fields='id, parents'
        )
        
        assert result['folder_id'] == 'folder-123'
        
    @pytest.mark.asyncio
    @patch('tools.docs.build')
    async def test_create_document_with_sharing(self, mock_build, docs_tools):
        """Test creating a document and sharing it."""
        # Setup mocks
        mock_docs_service = MagicMock()
        mock_drive_service = MagicMock()
        mock_build.side_effect = [mock_docs_service, mock_drive_service]
        
        # Mock document creation response
        mock_doc_response = {
            'documentId': 'test-doc-id',
            'title': 'Test Document',
            'revisionId': 'rev-123'
        }
        mock_docs_service.documents().create().execute.return_value = mock_doc_response
        
        # Test parameters
        params = {
            'title': 'Test Document',
            'share_with': ['user1@example.com', 'user2@example.com']
        }
        
        # Execute
        result = await docs_tools.create_document(params)
        
        # Verify sharing
        assert mock_drive_service.permissions().create.call_count == 2
        
        # Check each share call
        calls = mock_drive_service.permissions().create.call_args_list
        for i, email in enumerate(['user1@example.com', 'user2@example.com']):
            assert calls[i][1]['fileId'] == 'test-doc-id'
            assert calls[i][1]['body']['emailAddress'] == email
            assert calls[i][1]['body']['role'] == 'writer'
            assert calls[i][1]['sendNotificationEmail'] is True
            
        assert result['shared_with'] == ['user1@example.com', 'user2@example.com']
