"""Integration tests for enhanced calendar functionality with computed fields."""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.tools.calendar import GoogleCalendarTools


class TestEnhancedCalendar:
    """Tests for enhanced calendar functionality with computed fields."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth_manager = Mock()
        self.calendar_tools = GoogleCalendarTools(self.mock_auth_manager)

    @patch('src.tools.calendar.build')
    @pytest.mark.asyncio
    async def test_list_events_with_computed_fields(self, mock_build):
        """Test that list_events includes computed fields in response."""
        # Mock Google Calendar service response
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock calendar event from Google API
        mock_event = {
            'id': 'test-event-id',
            'summary': 'Test Event',
            'start': {
                'dateTime': '2025-09-27T12:30:00-04:00',
                'timeZone': 'America/Toronto'
            },
            'end': {
                'dateTime': '2025-09-27T13:00:00-04:00',
                'timeZone': 'America/Toronto'
            },
            'location': 'Test Location',
            'description': 'Test Description',
            'htmlLink': 'https://calendar.google.com/test',
            'status': 'confirmed',
            'attendees': []
        }

        mock_service.events().list().execute.return_value = {
            'items': [mock_event]
        }

        # Mock authentication
        self.mock_auth_manager.get_credentials.return_value = Mock()

        # Call list_events
        result = await self.calendar_tools.list_events({})

        # Verify basic response structure
        assert 'events' in result
        assert 'count' in result
        assert result['count'] == 1

        # Verify computed fields are added
        event = result['events'][0]
        assert 'computed' in event

        computed = event['computed']
        assert 'startDay' in computed
        assert 'endDay' in computed
        assert 'startDate' in computed
        assert 'endDate' in computed
        assert 'duration' in computed
        assert 'spansMultipleDays' in computed

        # Verify specific computed values
        assert computed['startDay'] == 'Saturday'  # 2025-09-27 is Saturday
        assert computed['endDay'] == 'Saturday'
        assert computed['startDate'] == '2025-09-27'
        assert computed['endDate'] == '2025-09-27'
        assert computed['duration'] == '30 minutes'
        assert computed['spansMultipleDays'] == False

        # Verify original fields are preserved
        assert event['id'] == 'test-event-id'
        assert event['summary'] == 'Test Event'
        assert event['location'] == 'Test Location'

    @patch('src.tools.calendar.build')
    @pytest.mark.asyncio
    async def test_create_event_with_computed_fields(self, mock_build):
        """Test that create_event includes computed fields in response."""
        # Mock Google Calendar service response
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock created event response from Google API
        mock_created_event = {
            'id': 'new-event-id',
            'summary': 'New Event',
            'start': {
                'dateTime': '2025-09-28T14:00:00-04:00',
                'timeZone': 'America/Toronto'
            },
            'end': {
                'dateTime': '2025-09-28T15:30:00-04:00',
                'timeZone': 'America/Toronto'
            },
            'htmlLink': 'https://calendar.google.com/new-event',
            'status': 'confirmed',
            'created': '2025-09-25T10:00:00Z'
        }

        mock_service.events().insert().execute.return_value = mock_created_event

        # Mock authentication
        self.mock_auth_manager.get_credentials.return_value = Mock()

        # Create event parameters
        params = {
            'summary': 'New Event',
            'start_time': '2025-09-28T14:00:00-04:00',
            'end_time': '2025-09-28T15:30:00-04:00',
            'timezone': 'America/Toronto'
        }

        # Call create_event
        result = await self.calendar_tools.create_event(params)

        # Verify computed fields are added
        assert 'computed' in result

        computed = result['computed']
        assert computed['startDay'] == 'Sunday'  # 2025-09-28 is Sunday
        assert computed['endDay'] == 'Sunday'
        assert computed['startDate'] == '2025-09-28'
        assert computed['endDate'] == '2025-09-28'
        assert computed['duration'] == '1 hour 30 minutes'
        assert computed['spansMultipleDays'] == False

        # Verify original fields are preserved
        assert result['id'] == 'new-event-id'
        assert result['summary'] == 'New Event'

    @patch('src.tools.calendar.build')
    @pytest.mark.asyncio
    async def test_multi_day_event_computed_fields(self, mock_build):
        """Test computed fields for multi-day events."""
        # Mock Google Calendar service response
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock multi-day event
        mock_event = {
            'id': 'multi-day-event',
            'summary': 'Conference',
            'start': {
                'dateTime': '2025-09-27T09:00:00-04:00',  # Saturday
                'timeZone': 'America/Toronto'
            },
            'end': {
                'dateTime': '2025-09-29T17:00:00-04:00',  # Monday
                'timeZone': 'America/Toronto'
            },
            'location': 'Convention Center',
            'htmlLink': 'https://calendar.google.com/conference',
            'status': 'confirmed'
        }

        mock_service.events().list().execute.return_value = {
            'items': [mock_event]
        }

        # Mock authentication
        self.mock_auth_manager.get_credentials.return_value = Mock()

        # Call list_events
        result = await self.calendar_tools.list_events({})

        # Verify computed fields for multi-day event
        event = result['events'][0]
        computed = event['computed']

        assert computed['startDay'] == 'Saturday'
        assert computed['endDay'] == 'Monday'
        assert computed['startDate'] == '2025-09-27'
        assert computed['endDate'] == '2025-09-29'
        assert computed['spansMultipleDays'] == True
        assert 'days' in computed['duration']  # Should include days in duration


if __name__ == '__main__':
    pytest.main([__file__])