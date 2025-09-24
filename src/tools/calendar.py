"""Google Calendar tools for MCP server."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleCalendarTools:
    """Handles Google Calendar operations."""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.service = None
        
    def _get_service(self):
        """Get or create the Google Calendar service."""
        if not self.service:
            creds = self.auth_manager.get_credentials()
            self.service = build('calendar', 'v3', credentials=creds)
        return self.service
        
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
                
        Returns:
            Dictionary with event information including ID and link
        """
        try:
            calendar_id = params.get('calendar_id', 'primary')
            
            # Build event data
            event_data = {
                'summary': params['summary'],
                'start': {
                    'dateTime': params['start_time'],
                    'timeZone': params.get('timezone', 'America/Toronto')
                },
                'end': {
                    'dateTime': params['end_time'],
                    'timeZone': params.get('timezone', 'America/Toronto')
                }
            }
            
            # Add optional fields
            if 'description' in params:
                event_data['description'] = params['description']
                
            if 'location' in params:
                event_data['location'] = params['location']
                
            if 'attendees' in params:
                event_data['attendees'] = [{'email': email} for email in params['attendees']]
                event_data['sendNotifications'] = True
                
            # Create the event
            service = self._get_service()
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                sendUpdates='all' if 'attendees' in params else 'none'
            ).execute()
            
            logger.info(f"Successfully created event: {event.get('summary')} (ID: {event.get('id')})")
            
            return {
                'id': event.get('id'),
                'summary': event.get('summary'),
                'htmlLink': event.get('htmlLink'),
                'start': event.get('start'),
                'end': event.get('end'),
                'status': event.get('status'),
                'created': event.get('created')
            }
            
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
            calendar_id = params['calendar_id']
            event_id = params['event_id']
            
            # Get existing event first
            service = self._get_service()
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields that were provided
            if 'summary' in params:
                event['summary'] = params['summary']
                
            if 'start_time' in params and 'end_time' in params:
                event['start'] = {
                    'dateTime': params['start_time'],
                    'timeZone': params.get('timezone', event['start'].get('timeZone', 'America/Toronto'))
                }
                event['end'] = {
                    'dateTime': params['end_time'],
                    'timeZone': params.get('timezone', event['end'].get('timeZone', 'America/Toronto'))
                }
                
            if 'description' in params:
                event['description'] = params['description']
                
            if 'location' in params:
                event['location'] = params['location']
                
            if 'attendees' in params:
                event['attendees'] = [{'email': email} for email in params['attendees']]
                
            # Update the event
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all' if 'attendees' in params else 'none'
            ).execute()
            
            logger.info(f"Successfully updated event: {updated_event.get('summary')} (ID: {event_id})")
            
            return {
                'id': updated_event.get('id'),
                'summary': updated_event.get('summary'),
                'htmlLink': updated_event.get('htmlLink'),
                'start': updated_event.get('start'),
                'end': updated_event.get('end'),
                'status': updated_event.get('status'),
                'updated': updated_event.get('updated')
            }
            
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
            calendar_id = params['calendar_id']
            event_id = params['event_id']
            
            service = self._get_service()
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Successfully deleted event ID: {event_id}")
            
            return {
                'success': True,
                'message': f'Event {event_id} deleted successfully'
            }
            
        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting event: {e}")
            raise
            
    async def list_calendars(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available calendars.
        
        Returns:
            Dictionary with list of calendars
        """
        try:
            service = self._get_service()
            calendar_list = service.calendarList().list().execute()
            
            calendars = []
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar.get('id'),
                    'summary': calendar.get('summary'),
                    'description': calendar.get('description', ''),
                    'accessRole': calendar.get('accessRole'),
                    'primary': calendar.get('primary', False),
                    'backgroundColor': calendar.get('backgroundColor'),
                    'foregroundColor': calendar.get('foregroundColor')
                })
                
            logger.info(f"Found {len(calendars)} calendars")
            
            return {
                'calendars': calendars,
                'count': len(calendars)
            }
            
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
            calendar_id = params.get('calendar_id', 'primary')
            
            # Build request parameters
            request_params = {
                'calendarId': calendar_id,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if 'time_min' in params:
                request_params['timeMin'] = params['time_min']
            if 'time_max' in params:
                request_params['timeMax'] = params['time_max']
            if 'max_results' in params:
                request_params['maxResults'] = params['max_results']
            if 'q' in params:
                request_params['q'] = params['q']
                
            service = self._get_service()
            events_result = service.events().list(**request_params).execute()
            events = events_result.get('items', [])
            
            # Format events for response
            formatted_events = []
            for event in events:
                formatted_event = {
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No title'),
                    'start': event.get('start'),
                    'end': event.get('end'),
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                    'htmlLink': event.get('htmlLink'),
                    'status': event.get('status'),
                    'attendees': event.get('attendees', [])
                }
                formatted_events.append(formatted_event)
                
            logger.info(f"Found {len(formatted_events)} events")
            
            return {
                'events': formatted_events,
                'count': len(formatted_events)
            }
            
        except HttpError as e:
            logger.error(f"Error listing events: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing events: {e}")
            raise
