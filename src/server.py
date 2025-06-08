import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/adam/Code/calendar-mcp/mcp-server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleCalendarMCP:
    def __init__(self):
        self.service = None
        # Get directory where server.py is located
        script_dir = Path(__file__).parent.parent  # Go up one level from src/
        self.credentials_path = script_dir / "credentials.json"
        self.token_path = script_dir / "token.json"
        self.setup_auth()
    
    def setup_auth(self):
        """Handle Google Calendar API authentication"""
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Download from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Google Calendar service initialized")
    
    def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return {
                "success": True,
                "event_id": event.get('id'),
                "html_link": event.get('htmlLink'),
                "event": event
            }
        except HttpError as error:
            logger.error(f"Failed to create event: {error}")
            return {
                "success": False,
                "error": str(error)
            }
    
    def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            return {
                "success": True,
                "event_id": event.get('id'),
                "html_link": event.get('htmlLink'),
                "event": event
            }
        except HttpError as error:
            logger.error(f"Failed to update event: {error}")
            return {
                "success": False,
                "error": str(error)
            }
    
    def delete_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                "success": True,
                "message": f"Event {event_id} deleted successfully"
            }
        except HttpError as error:
            logger.error(f"Failed to delete event: {error}")
            return {
                "success": False,
                "error": str(error)
            }
    
    def list_calendars(self) -> Dict[str, Any]:
        """List all available calendars"""
        try:
            calendar_list = self.service.calendarList().list().execute()
            
            calendars = []
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    "id": calendar.get('id'),
                    "summary": calendar.get('summary'),
                    "description": calendar.get('description', ''),
                    "access_role": calendar.get('accessRole'),
                    "primary": calendar.get('primary', False)
                })
            
            return {
                "success": True,
                "calendars": calendars
            }
        except HttpError as error:
            logger.error(f"Failed to list calendars: {error}")
            return {
                "success": False,
                "error": str(error)
            }

# Initialize the MCP server
app = Server("google-calendar-mcp")
calendar_client = GoogleCalendarMCP()

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="create_calendar_event",
            description="Create a new event in Google Calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (use 'primary' for main calendar)"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Event title/summary"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description (optional)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format (e.g., '2024-12-25T10:00:00')"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format (e.g., '2024-12-25T11:00:00')"
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (e.g., 'America/New_York')",
                        "default": "America/New_York"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location (optional)"
                    }
                },
                "required": ["calendar_id", "summary", "start_time", "end_time"]
            }
        ),
        Tool(
            name="update_calendar_event",
            description="Update an existing calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID"
                    },
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to update"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Event title/summary"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description (optional)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format"
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone",
                        "default": "America/New_York"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location (optional)"
                    }
                },
                "required": ["calendar_id", "event_id"]
            }
        ),
        Tool(
            name="delete_calendar_event",
            description="Delete a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID"
                    },
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to delete"
                    }
                },
                "required": ["calendar_id", "event_id"]
            }
        ),
        Tool(
            name="list_calendars",
            description="List all available calendars",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    
    if name == "create_calendar_event":
        # Build event data structure
        event_data = {
            "summary": arguments["summary"],
            "start": {
                "dateTime": arguments["start_time"],
                "timeZone": arguments.get("timezone", "America/New_York")
            },
            "end": {
                "dateTime": arguments["end_time"],
                "timeZone": arguments.get("timezone", "America/New_York")
            }
        }
        
        # Add optional fields
        if "description" in arguments:
            event_data["description"] = arguments["description"]
        
        if "location" in arguments:
            event_data["location"] = arguments["location"]
        
        if "attendees" in arguments:
            event_data["attendees"] = [{"email": email} for email in arguments["attendees"]]
        
        result = calendar_client.create_event(arguments["calendar_id"], event_data)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_calendar_event":
        # Build event data structure for update
        event_data = {}
        
        if "summary" in arguments:
            event_data["summary"] = arguments["summary"]
        
        if "start_time" in arguments and "end_time" in arguments:
            event_data["start"] = {
                "dateTime": arguments["start_time"],
                "timeZone": arguments.get("timezone", "America/New_York")
            }
            event_data["end"] = {
                "dateTime": arguments["end_time"],
                "timeZone": arguments.get("timezone", "America/New_York")
            }
        
        if "description" in arguments:
            event_data["description"] = arguments["description"]
        
        if "location" in arguments:
            event_data["location"] = arguments["location"]
        
        if "attendees" in arguments:
            event_data["attendees"] = [{"email": email} for email in arguments["attendees"]]
        
        result = calendar_client.update_event(
            arguments["calendar_id"],
            arguments["event_id"],
            event_data
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "delete_calendar_event":
        result = calendar_client.delete_event(
            arguments["calendar_id"],
            arguments["event_id"]
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_calendars":
        result = calendar_client.list_calendars()
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the server using stdin/stdout streams"""
    logger.info("Starting MCP server...")
    try:
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP server streams established")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    import sys
    
    try:
        logger.info("Starting MCP server process...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"MCP server fatal error: {e}")
        sys.exit(1)
