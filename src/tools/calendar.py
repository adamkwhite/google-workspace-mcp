"""Google Calendar tools for MCP server."""

import html
import logging
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.date_helpers import add_computed_fields  # noqa: E402

logger = logging.getLogger(__name__)

# Default timezone constant
DEFAULT_TIMEZONE = "America/Toronto"


class GoogleCalendarTools:
    """Handles Google Calendar operations."""

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.service = None

    def _get_service(self):
        """Get or create the Google Calendar service."""
        if not self.service:
            creds = self.auth_manager.get_credentials()
            self.service = build("calendar", "v3", credentials=creds)
        return self.service

    def _validate_text_field(self, value: Any, field_name: str, max_length: int) -> str:
        """Validate and sanitize a text field.

        IMPORTANT: Input must be raw, unescaped text. Do not pass pre-escaped HTML
        as it will be double-escaped. The function handles all necessary escaping.

        Args:
            value: Field value to validate (must be raw, unescaped text)
            field_name: Name of the field (for error messages)
            max_length: Maximum allowed length

        Returns:
            Sanitized text value with HTML entities escaped

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        text = value.strip()
        if not text:
            raise ValueError(f"{field_name} cannot be empty")

        if len(text) > max_length:
            raise ValueError(f"{field_name} must be {max_length} characters or less")

        return html.escape(text)

    def _validate_url_field(self, value: Any) -> str:
        """Validate chat_url field.

        NOTE: URL validation is restricted to claude.ai domain for security.
        Only HTTPS URLs from *.claude.ai are permitted to prevent phishing
        and unauthorized data exfiltration.

        Args:
            value: URL value to validate

        Returns:
            Validated URL string

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, str):
            raise ValueError("chat_url must be a string")

        url = value.strip()
        if not url:
            raise ValueError("chat_url cannot be empty")

        # Parse and validate URL (urlparse doesn't raise for most inputs)
        parsed = urlparse(url)

        # Enforce HTTPS
        if parsed.scheme != "https":
            raise ValueError("chat_url must use HTTPS protocol")

        # Whitelist allowed domains (claude.ai and subdomains)
        allowed_pattern = r"^(.*\.)?claude\.ai$"
        if not re.match(allowed_pattern, parsed.netloc):
            raise ValueError("chat_url must be from claude.ai domain")

        return url

    def _validate_date_field(self, value: Any) -> str:
        """Validate created_date field.

        Args:
            value: Date value to validate

        Returns:
            Validated date string

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, str):
            raise ValueError("created_date must be a string")

        date_str = value.strip()
        if not date_str:
            raise ValueError("created_date cannot be empty")

        # Validate ISO date format with stricter parsing
        # strptime rejects invalid dates (e.g., 2025-02-30) and enforces YYYY-MM-DD format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"created_date must be in ISO format (YYYY-MM-DD): {e}")

        return date_str

    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize metadata fields.

        CRITICAL: All metadata input must be raw, unescaped text to prevent
        double-escaping on updates. This method applies HTML escaping and
        should be called every time metadata is provided, including updates.

        Args:
            metadata: Dictionary with optional fields: chat_title, chat_url,
                     project_name, created_date (all must be raw, unescaped)

        Returns:
            Validated and sanitized metadata dictionary

        Raises:
            ValueError: If any field fails validation
        """
        if not metadata:
            return {}

        if not isinstance(metadata, dict):
            raise ValueError("metadata must be a dictionary")

        validated = {}

        if "chat_title" in metadata:
            validated["chat_title"] = self._validate_text_field(
                metadata["chat_title"], "chat_title", 200
            )

        if "chat_url" in metadata:
            validated["chat_url"] = self._validate_url_field(metadata["chat_url"])

        if "project_name" in metadata:
            validated["project_name"] = self._validate_text_field(
                metadata["project_name"], "project_name", 100
            )

        if "created_date" in metadata:
            validated["created_date"] = self._validate_date_field(
                metadata["created_date"]
            )

        return validated

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a description section.

        Args:
            metadata: Dictionary with optional fields: created_date, project_name,
                     chat_title, chat_url

        Returns:
            Formatted metadata string to append to description, or empty string if no content
        """
        # Check if any metadata fields have actual values
        has_content = any(
            metadata.get(key)
            for key in ["created_date", "project_name", "chat_title", "chat_url"]
        )

        if not has_content:
            return ""

        metadata_section = "\n\n---\n📋 Context:\n"

        if metadata.get("created_date"):
            metadata_section += f"Created: {metadata['created_date']}\n"
        if metadata.get("project_name"):
            metadata_section += f"Project: {metadata['project_name']}\n"
        if metadata.get("chat_title"):
            metadata_section += f"Chat: {metadata['chat_title']}\n"
        if metadata.get("chat_url"):
            metadata_section += f"URL: {metadata['chat_url']}\n"

        return metadata_section.rstrip()

    async def create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event.

        Args:
            params: Dictionary containing:
                - calendar_id: Calendar ID (use 'primary' for main calendar)
                - summary: Event title (required)
                - start_time: Start time in ISO format (required)
                - end_time: End time in ISO format (required)
                - description: Event description (optional)
                - location: Event location (optional)
                - attendees: List of attendee emails (optional)
                - timezone: Timezone (defaults to America/Toronto)
                - metadata: Dict with chat_title, chat_url, project_name, created_date (optional)

        Returns:
            Dictionary with event information including ID and link
        """
        try:
            calendar_id = params.get("calendar_id", "primary")

            # Build event data
            event_data = {
                "summary": params["summary"],
                "start": {
                    "dateTime": params["start_time"],
                    "timeZone": params.get("timezone", DEFAULT_TIMEZONE),
                },
                "end": {
                    "dateTime": params["end_time"],
                    "timeZone": params.get("timezone", DEFAULT_TIMEZONE),
                },
            }

            # Add optional fields
            description = params.get("description", "")

            # Validate and append metadata to description if provided
            if "metadata" in params and params["metadata"]:
                validated_metadata = self._validate_metadata(params["metadata"])
                description += self._format_metadata(validated_metadata)

            if description:
                event_data["description"] = description

            if "location" in params:
                event_data["location"] = params["location"]

            if "attendees" in params:
                event_data["attendees"] = [
                    {"email": email} for email in params["attendees"]
                ]
                event_data["sendNotifications"] = True

            # Create the event
            service = self._get_service()
            event = (
                service.events()
                .insert(
                    calendarId=calendar_id,
                    body=event_data,
                    sendUpdates="all" if "attendees" in params else "none",
                )
                .execute()
            )

            logger.info(
                f"Successfully created event: {event.get('summary')} (ID: {event.get('id')})"
            )

            # Build response with basic fields
            response = {
                "id": event.get("id"),
                "summary": event.get("summary"),
                "htmlLink": event.get("htmlLink"),
                "start": event.get("start"),
                "end": event.get("end"),
                "status": event.get("status"),
                "created": event.get("created"),
            }

            # Add computed fields for day-of-week and date information
            try:
                response = add_computed_fields(response)
            except Exception as e:
                logger.warning(f"Failed to add computed fields to created event: {e}")
                # Return response without computed fields if calculation fails

            return response

        except HttpError as e:
            logger.error(f"Error creating event: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}")
            raise

    async def update_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event.

        Args:
            params: Dictionary containing:
                - calendar_id: Calendar ID (required)
                - event_id: Event ID to update (required)
                - Other fields same as create_event (all optional)

        Returns:
            Dictionary with updated event information
        """
        try:
            calendar_id = params["calendar_id"]
            event_id = params["event_id"]

            # Get existing event first
            service = self._get_service()
            event = (
                service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )

            # Update fields that were provided
            if "summary" in params:
                event["summary"] = params["summary"]

            if "start_time" in params and "end_time" in params:
                event["start"] = {
                    "dateTime": params["start_time"],
                    "timeZone": params.get(
                        "timezone", event["start"].get("timeZone", DEFAULT_TIMEZONE)
                    ),
                }
                event["end"] = {
                    "dateTime": params["end_time"],
                    "timeZone": params.get(
                        "timezone", event["end"].get("timeZone", DEFAULT_TIMEZONE)
                    ),
                }

            if "description" in params:
                event["description"] = params["description"]

            # Validate and replace metadata in description if provided
            if "metadata" in params and params["metadata"]:
                validated_metadata = self._validate_metadata(params["metadata"])
                # Get existing description or empty string
                description = event.get("description", "")

                # Remove existing metadata section if present to prevent double-escaping
                metadata_marker = "\n\n---\n📋 Context:\n"
                if metadata_marker in description:
                    description = description.split(metadata_marker)[0]

                # Append new validated metadata
                description += self._format_metadata(validated_metadata)
                event["description"] = description

            if "location" in params:
                event["location"] = params["location"]

            if "attendees" in params:
                event["attendees"] = [{"email": email} for email in params["attendees"]]

            # Update the event
            updated_event = (
                service.events()
                .update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event,
                    sendUpdates="all" if "attendees" in params else "none",
                )
                .execute()
            )

            logger.info(
                f"Successfully updated event: {updated_event.get('summary')} (ID: {event_id})"
            )

            # Build response with basic fields
            response = {
                "id": updated_event.get("id"),
                "summary": updated_event.get("summary"),
                "htmlLink": updated_event.get("htmlLink"),
                "start": updated_event.get("start"),
                "end": updated_event.get("end"),
                "status": updated_event.get("status"),
                "updated": updated_event.get("updated"),
            }

            # Add computed fields for day-of-week and date information
            try:
                response = add_computed_fields(response)
            except Exception as e:
                logger.warning(f"Failed to add computed fields to updated event: {e}")
                # Return response without computed fields if calculation fails

            return response

        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating event: {e}")
            raise

    async def delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event.

        Args:
            params: Dictionary containing:
                - calendar_id: Calendar ID (required)
                - event_id: Event ID to delete (required)

        Returns:
            Dictionary confirming deletion
        """
        try:
            calendar_id = params["calendar_id"]
            event_id = params["event_id"]

            service = self._get_service()
            service.events().delete(
                calendarId=calendar_id, eventId=event_id, sendUpdates="all"
            ).execute()

            logger.info(f"Successfully deleted event ID: {event_id}")

            return {
                "success": True,
                "message": f"Event {event_id} deleted successfully",
            }

        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting event: {e}")
            raise

    async def list_calendars(self) -> Dict[str, Any]:
        """List all available calendars.

        Returns:
            Dictionary with list of calendars
        """
        try:
            service = self._get_service()
            calendar_list = service.calendarList().list().execute()

            calendars = []
            for calendar in calendar_list.get("items", []):
                calendars.append(
                    {
                        "id": calendar.get("id"),
                        "summary": calendar.get("summary"),
                        "description": calendar.get("description", ""),
                        "accessRole": calendar.get("accessRole"),
                        "primary": calendar.get("primary", False),
                        "backgroundColor": calendar.get("backgroundColor"),
                        "foregroundColor": calendar.get("foregroundColor"),
                    }
                )

            logger.info(f"Found {len(calendars)} calendars")

            return {"calendars": calendars, "count": len(calendars)}

        except HttpError as e:
            logger.error(f"Error listing calendars: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing calendars: {e}")
            raise

    async def list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List calendar events.

        Args:
            params: Dictionary containing:
                - calendar_id: Calendar ID (defaults to 'primary')
                - time_min: Start time for events (ISO format)
                - time_max: End time for events (ISO format)
                - max_results: Maximum number of events to return
                - q: Search query

        Returns:
            Dictionary with list of events
        """
        try:
            calendar_id = params.get("calendar_id", "primary")

            # Build request parameters
            request_params = {
                "calendarId": calendar_id,
                "singleEvents": True,
                "orderBy": "startTime",
            }

            if "time_min" in params:
                request_params["timeMin"] = params["time_min"]
            if "time_max" in params:
                request_params["timeMax"] = params["time_max"]
            if "max_results" in params:
                request_params["maxResults"] = params["max_results"]
            if "q" in params:
                request_params["q"] = params["q"]

            service = self._get_service()
            events_result = service.events().list(**request_params).execute()
            events = events_result.get("items", [])

            # Format events for response with computed fields
            formatted_events = []
            for event in events:
                formatted_event = {
                    "id": event.get("id"),
                    "summary": event.get("summary", "No title"),
                    "start": event.get("start"),
                    "end": event.get("end"),
                    "location": event.get("location", ""),
                    "description": event.get("description", ""),
                    "htmlLink": event.get("htmlLink"),
                    "status": event.get("status"),
                    "attendees": event.get("attendees", []),
                }

                # Add computed fields for day-of-week and date information
                try:
                    formatted_event = add_computed_fields(formatted_event)
                except Exception as e:
                    logger.warning(
                        f"Failed to add computed fields to event {event.get('id', 'unknown')}: {e}"
                    )
                    # Continue without computed fields if calculation fails

                formatted_events.append(formatted_event)

            logger.info(f"Found {len(formatted_events)} events")

            return {"events": formatted_events, "count": len(formatted_events)}

        except HttpError as e:
            logger.error(f"Error listing events: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing events: {e}")
            raise
