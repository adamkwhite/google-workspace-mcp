"""Integration tests for enhanced calendar functionality with computed fields."""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tools.calendar import GoogleCalendarTools  # noqa: E402


class TestEnhancedCalendar:
    """Tests for enhanced calendar functionality with computed fields."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth_manager = Mock()
        self.calendar_tools = GoogleCalendarTools(self.mock_auth_manager)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_list_events_with_computed_fields(self, mock_build):
        """Test that list_events includes computed fields in response."""
        # Mock Google Calendar service response
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock calendar event from Google API
        mock_event = {
            "id": "test-event-id",
            "summary": "Test Event",
            "start": {
                "dateTime": "2025-09-27T12:30:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-27T13:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "location": "Test Location",
            "description": "Test Description",
            "htmlLink": "https://calendar.google.com/test",
            "status": "confirmed",
            "attendees": [],
        }

        mock_service.events().list().execute.return_value = {"items": [mock_event]}

        # Mock authentication
        self.mock_auth_manager.get_credentials.return_value = Mock()

        # Call list_events
        result = await self.calendar_tools.list_events({})

        # Verify basic response structure
        assert "events" in result
        assert "count" in result
        assert result["count"] == 1

        # Verify computed fields are added
        event = result["events"][0]
        assert "computed" in event

        computed = event["computed"]
        assert "startDay" in computed
        assert "endDay" in computed
        assert "startDate" in computed
        assert "endDate" in computed
        assert "duration" in computed
        assert "spansMultipleDays" in computed

        # Verify specific computed values
        assert computed["startDay"] == "Saturday"  # 2025-09-27 is Saturday
        assert computed["endDay"] == "Saturday"
        assert computed["startDate"] == "2025-09-27"
        assert computed["endDate"] == "2025-09-27"
        assert computed["duration"] == "30 minutes"
        assert computed["spansMultipleDays"] is False

        # Verify original fields are preserved
        assert event["id"] == "test-event-id"
        assert event["summary"] == "Test Event"
        assert event["location"] == "Test Location"

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_create_event_with_computed_fields(self, mock_build):
        """Test that create_event includes computed fields in response."""
        # Mock Google Calendar service response
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock created event response from Google API
        mock_created_event = {
            "id": "new-event-id",
            "summary": "New Event",
            "start": {
                "dateTime": "2025-09-28T14:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T15:30:00-04:00",
                "timeZone": "America/Toronto",
            },
            "htmlLink": "https://calendar.google.com/new-event",
            "status": "confirmed",
            "created": "2025-09-25T10:00:00Z",
        }

        mock_service.events().insert().execute.return_value = mock_created_event

        # Mock authentication
        self.mock_auth_manager.get_credentials.return_value = Mock()

        # Create event parameters
        params = {
            "summary": "New Event",
            "start_time": "2025-09-28T14:00:00-04:00",
            "end_time": "2025-09-28T15:30:00-04:00",
            "timezone": "America/Toronto",
        }

        # Call create_event
        result = await self.calendar_tools.create_event(params)

        # Verify computed fields are added
        assert "computed" in result

        computed = result["computed"]
        assert computed["startDay"] == "Sunday"  # 2025-09-28 is Sunday
        assert computed["endDay"] == "Sunday"
        assert computed["startDate"] == "2025-09-28"
        assert computed["endDate"] == "2025-09-28"
        assert computed["duration"] == "1 hour 30 minutes"
        assert computed["spansMultipleDays"] is False

        # Verify original fields are preserved
        assert result["id"] == "new-event-id"
        assert result["summary"] == "New Event"

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_multi_day_event_computed_fields(self, mock_build):
        """Test computed fields for multi-day events."""
        # Mock Google Calendar service response
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock multi-day event
        mock_event = {
            "id": "multi-day-event",
            "summary": "Conference",
            "start": {
                "dateTime": "2025-09-27T09:00:00-04:00",  # Saturday
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-29T17:00:00-04:00",  # Monday
                "timeZone": "America/Toronto",
            },
            "location": "Convention Center",
            "htmlLink": "https://calendar.google.com/conference",
            "status": "confirmed",
        }

        mock_service.events().list().execute.return_value = {"items": [mock_event]}

        # Mock authentication
        self.mock_auth_manager.get_credentials.return_value = Mock()

        # Call list_events
        result = await self.calendar_tools.list_events({})

        # Verify computed fields for multi-day event
        event = result["events"][0]
        computed = event["computed"]

        assert computed["startDay"] == "Saturday"
        assert computed["endDay"] == "Monday"
        assert computed["startDate"] == "2025-09-27"
        assert computed["endDate"] == "2025-09-29"
        assert computed["spansMultipleDays"] is True
        assert "days" in computed["duration"]  # Should include days in duration

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_basic(self, mock_build):
        """Test updating a calendar event."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock existing event
        existing_event = {
            "id": "event-123",
            "summary": "Old Title",
            "start": {
                "dateTime": "2025-09-28T10:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T11:00:00-04:00",
                "timeZone": "America/Toronto",
            },
        }

        # Mock updated event response
        updated_event = {
            "id": "event-123",
            "summary": "New Title",
            "start": {
                "dateTime": "2025-09-28T10:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T11:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "htmlLink": "https://calendar.google.com/event-123",
            "status": "confirmed",
            "updated": "2025-09-25T10:30:00Z",
        }

        mock_service.events().get().execute.return_value = existing_event
        mock_service.events().update().execute.return_value = updated_event

        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {
            "calendar_id": "primary",
            "event_id": "event-123",
            "summary": "New Title",
        }

        result = await self.calendar_tools.update_event(params)

        assert result["id"] == "event-123"
        assert result["summary"] == "New Title"
        assert "computed" in result

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_with_time_change(self, mock_build):
        """Test updating event with time changes."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        existing_event = {
            "id": "event-456",
            "summary": "Meeting",
            "start": {
                "dateTime": "2025-09-28T10:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T11:00:00-04:00",
                "timeZone": "America/Toronto",
            },
        }

        updated_event = {
            "id": "event-456",
            "summary": "Meeting",
            "start": {
                "dateTime": "2025-09-28T14:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T15:30:00-04:00",
                "timeZone": "America/Toronto",
            },
            "htmlLink": "https://calendar.google.com/event-456",
            "status": "confirmed",
            "updated": "2025-09-25T11:00:00Z",
        }

        mock_service.events().get().execute.return_value = existing_event
        mock_service.events().update().execute.return_value = updated_event

        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {
            "calendar_id": "primary",
            "event_id": "event-456",
            "start_time": "2025-09-28T14:00:00-04:00",
            "end_time": "2025-09-28T15:30:00-04:00",
        }

        result = await self.calendar_tools.update_event(params)

        assert result["id"] == "event-456"
        assert result["start"]["dateTime"] == "2025-09-28T14:00:00-04:00"

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_with_attendees(self, mock_build):
        """Test updating event with attendees."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        existing_event = {
            "id": "event-789",
            "summary": "Team Meeting",
            "start": {
                "dateTime": "2025-09-28T10:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T11:00:00-04:00",
                "timeZone": "America/Toronto",
            },
        }

        updated_event = {
            "id": "event-789",
            "summary": "Team Meeting",
            "start": {
                "dateTime": "2025-09-28T10:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T11:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "attendees": [
                {"email": "alice@example.com"},
                {"email": "bob@example.com"},
            ],
            "htmlLink": "https://calendar.google.com/event-789",
            "status": "confirmed",
            "updated": "2025-09-25T12:00:00Z",
        }

        mock_service.events().get().execute.return_value = existing_event
        mock_service.events().update().execute.return_value = updated_event

        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {
            "calendar_id": "primary",
            "event_id": "event-789",
            "attendees": ["alice@example.com", "bob@example.com"],
        }

        result = await self.calendar_tools.update_event(params)

        assert result["id"] == "event-789"
        assert "computed" in result

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_delete_event_success(self, mock_build):
        """Test deleting a calendar event."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_service.events().delete().execute.return_value = None

        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {"calendar_id": "primary", "event_id": "event-to-delete"}

        result = await self.calendar_tools.delete_event(params)

        assert result["success"] is True
        assert "deleted successfully" in result["message"]
        assert "event-to-delete" in result["message"]

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_update_event_error_handling(self, mock_build):
        """Test error handling when updating event."""
        from googleapiclient.errors import HttpError

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock HTTP error
        mock_service.events().get().execute.side_effect = HttpError(
            resp=Mock(status=404), content=b"Not Found"
        )

        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {
            "calendar_id": "primary",
            "event_id": "nonexistent",
            "summary": "New Title",
        }

        with pytest.raises(HttpError):
            await self.calendar_tools.update_event(params)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_delete_event_error_handling(self, mock_build):
        """Test error handling when deleting event."""
        from googleapiclient.errors import HttpError

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock HTTP error
        mock_service.events().delete().execute.side_effect = HttpError(
            resp=Mock(status=403), content=b"Forbidden"
        )

        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {"calendar_id": "primary", "event_id": "forbidden-event"}

        with pytest.raises(HttpError):
            await self.calendar_tools.delete_event(params)

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_create_event_with_metadata(self, mock_build):
        """Test creating event with metadata appended to description."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_created_event = {
            "id": "event-with-metadata",
            "summary": "Team Meeting",
            "start": {
                "dateTime": "2025-09-28T14:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-28T15:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "description": (
                "Discuss project updates\n\n---\n📋 Context:\n"
                "Created: 2025-09-28\nProject: Q4 Planning\n"
                "Chat: Team Sync Discussion\n"
                "URL: https://claude.ai/chat/abc123"
            ),
            "htmlLink": "https://calendar.google.com/event-with-metadata",
            "status": "confirmed",
            "created": "2025-09-28T10:00:00Z",
        }

        mock_service.events().insert().execute.return_value = mock_created_event
        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {
            "summary": "Team Meeting",
            "start_time": "2025-09-28T14:00:00-04:00",
            "end_time": "2025-09-28T15:00:00-04:00",
            "description": "Discuss project updates",
            "metadata": {
                "created_date": "2025-09-28",
                "project_name": "Q4 Planning",
                "chat_title": "Team Sync Discussion",
                "chat_url": "https://claude.ai/chat/abc123",
            },
        }

        result = await self.calendar_tools.create_event(params)

        assert result["id"] == "event-with-metadata"
        assert "computed" in result

        # Verify the event was created with metadata in description
        call_args = mock_service.events().insert.call_args
        event_body = call_args.kwargs["body"]
        assert "📋 Context:" in event_body["description"]
        assert "Created: 2025-09-28" in event_body["description"]
        assert "Project: Q4 Planning" in event_body["description"]
        assert "Chat: Team Sync Discussion" in event_body["description"]
        assert "URL: https://claude.ai/chat/abc123" in event_body["description"]

    @patch("tools.calendar.build")
    @pytest.mark.asyncio
    async def test_create_event_with_partial_metadata(self, mock_build):
        """Test creating event with partial metadata."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_created_event = {
            "id": "event-partial-meta",
            "summary": "Quick Task",
            "start": {
                "dateTime": "2025-09-29T10:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-29T10:30:00-04:00",
                "timeZone": "America/Toronto",
            },
            "description": "Task notes\n\n---\n📋 Context:\nChat: Daily Planning",
            "htmlLink": "https://calendar.google.com/event-partial-meta",
            "status": "confirmed",
            "created": "2025-09-29T09:00:00Z",
        }

        mock_service.events().insert().execute.return_value = mock_created_event
        self.mock_auth_manager.get_credentials.return_value = Mock()

        params = {
            "summary": "Quick Task",
            "start_time": "2025-09-29T10:00:00-04:00",
            "end_time": "2025-09-29T10:30:00-04:00",
            "description": "Task notes",
            "metadata": {
                "chat_title": "Daily Planning",
                # Only chat_title provided, others omitted
            },
        }

        result = await self.calendar_tools.create_event(params)

        assert result["id"] == "event-partial-meta"

        # Verify only chat_title was added
        call_args = mock_service.events().insert.call_args
        event_body = call_args.kwargs["body"]
        assert "📋 Context:" in event_body["description"]
        assert "Chat: Daily Planning" in event_body["description"]
        assert "Project:" not in event_body["description"]
        assert "Created:" not in event_body["description"]


if __name__ == "__main__":
    pytest.main([__file__])
