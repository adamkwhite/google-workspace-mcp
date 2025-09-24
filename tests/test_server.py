import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import GoogleCalendarMCP

class TestGoogleCalendarMCP:
    
    @pytest.fixture
    def mock_service(self):
        """Mock Google Calendar service"""
        service = Mock()
        return service
    
    @pytest.fixture
    def calendar_client(self, mock_service):
        """Create calendar client with mocked service"""
        with patch('server.build') as mock_build:
            mock_build.return_value = mock_service
            client = GoogleCalendarMCP()
            client.service = mock_service
            return client
    
    def test_create_event_success(self, calendar_client, mock_service):
        """Test successful event creation"""
        # Setup mock response
        mock_event = {
            'id': 'test-event-id',
            'htmlLink': 'https://calendar.google.com/test',
            'summary': 'Test Event'
        }
        mock_service.events().insert().execute.return_value = mock_event
        
        # Test data
        event_data = {
            'summary': 'Test Event',
            'start': {'dateTime': '2024-12-25T10:00:00', 'timeZone': 'America/New_York'},
            'end': {'dateTime': '2024-12-25T11:00:00', 'timeZone': 'America/New_York'}
        }
        
        # Execute
        result = calendar_client.create_event('primary', event_data)
        
        # Verify
        assert result['success'] is True
        assert result['event_id'] == 'test-event-id'
        assert result['html_link'] == 'https://calendar.google.com/test'
        mock_service.events().insert.assert_called_once_with(
            calendarId='primary',
            body=event_data
        )
    
    def test_create_event_failure(self, calendar_client, mock_service):
        """Test event creation failure"""
        from googleapiclient.errors import HttpError
        
        # Setup mock to raise HttpError
        mock_response = Mock()
        mock_response.status = 400
        mock_response.reason = 'Bad Request'
        
        error = HttpError(mock_response, b'{"error": "Invalid request"}')
        mock_service.events().insert().execute.side_effect = error
        
        # Execute
        result = calendar_client.create_event('primary', {})
        
        # Verify
        assert result['success'] is False
        assert 'error' in result
    
    def test_update_event_success(self, calendar_client, mock_service):
        """Test successful event update"""
        # Setup mock response
        mock_event = {
            'id': 'test-event-id',
            'htmlLink': 'https://calendar.google.com/test',
            'summary': 'Updated Event'
        }
        mock_service.events().update().execute.return_value = mock_event
        
        # Test data
        event_data = {'summary': 'Updated Event'}
        
        # Execute
        result = calendar_client.update_event('primary', 'test-event-id', event_data)
        
        # Verify
        assert result['success'] is True
        assert result['event_id'] == 'test-event-id'
        mock_service.events().update.assert_called_once_with(
            calendarId='primary',
            eventId='test-event-id',
            body=event_data
        )
    
    def test_delete_event_success(self, calendar_client, mock_service):
        """Test successful event deletion"""
        # Setup mock (delete returns None on success)
        mock_service.events().delete().execute.return_value = None
        
        # Execute
        result = calendar_client.delete_event('primary', 'test-event-id')
        
        # Verify
        assert result['success'] is True
        assert 'Event test-event-id deleted successfully' in result['message']
        mock_service.events().delete.assert_called_once_with(
            calendarId='primary',
            eventId='test-event-id'
        )
    
    def test_list_calendars_success(self, calendar_client, mock_service):
        """Test successful calendar listing"""
        # Setup mock response
        mock_calendars = {
            'items': [
                {
                    'id': 'primary',
                    'summary': 'Primary Calendar',
                    'description': 'Main calendar',
                    'accessRole': 'owner',
                    'primary': True
                },
                {
                    'id': 'secondary@gmail.com',
                    'summary': 'Work Calendar',
                    'accessRole': 'writer',
                    'primary': False
                }
            ]
        }
        mock_service.calendarList().list().execute.return_value = mock_calendars
        
        # Execute
        result = calendar_client.list_calendars()
        
        # Verify
        assert result['success'] is True
        assert len(result['calendars']) == 2
        assert result['calendars'][0]['id'] == 'primary'
        assert result['calendars'][0]['primary'] is True
        assert result['calendars'][1]['id'] == 'secondary@gmail.com'
        assert result['calendars'][1]['primary'] is False

class TestEventDataBuilder:
    """Test event data structure building"""
    
    def test_basic_event_structure(self):
        """Test basic event data structure"""
        event_data = {
            "summary": "Test Meeting",
            "start": {
                "dateTime": "2024-12-25T10:00:00",
                "timeZone": "America/New_York"
            },
            "end": {
                "dateTime": "2024-12-25T11:00:00",
                "timeZone": "America/New_York"
            }
        }
        
        assert event_data['summary'] == "Test Meeting"
        assert event_data['start']['dateTime'] == "2024-12-25T10:00:00"
        assert event_data['start']['timeZone'] == "America/New_York"
        assert event_data['end']['dateTime'] == "2024-12-25T11:00:00"
    
    def test_event_with_attendees(self):
        """Test event data with attendees"""
        attendees = ["user1@example.com", "user2@example.com"]
        attendee_objects = [{"email": email} for email in attendees]
        
        assert len(attendee_objects) == 2
        assert attendee_objects[0]["email"] == "user1@example.com"
        assert attendee_objects[1]["email"] == "user2@example.com"
    
    def test_event_with_optional_fields(self):
        """Test event data with all optional fields"""
        event_data = {
            "summary": "Team Meeting",
            "description": "Weekly team sync",
            "location": "Conference Room A",
            "start": {
                "dateTime": "2024-12-25T10:00:00",
                "timeZone": "America/New_York"
            },
            "end": {
                "dateTime": "2024-12-25T11:00:00",
                "timeZone": "America/New_York"
            },
            "attendees": [
                {"email": "team@example.com"}
            ]
        }
        
        assert event_data['description'] == "Weekly team sync"
        assert event_data['location'] == "Conference Room A"
        assert len(event_data['attendees']) == 1

if __name__ == "__main__":
    pytest.main([__file__])
