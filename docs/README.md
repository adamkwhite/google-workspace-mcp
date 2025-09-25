# Google Calendar MCP Server

A Model Context Protocol (MCP) server that provides write access to Google Calendar. This allows Claude to create, update, and delete calendar events through the MCP interface.

## Prerequisites

• Google Cloud Project with Calendar API enabled
• OAuth 2.0 credentials downloaded as `credentials.json`
• Python 3.11+ installed (required for MCP compatibility in Ubuntu WSL)

## Quick Start (25-minute setup)

### Environment Setup
This project is designed to run in **Ubuntu WSL** for optimal compatibility with the development workflow. While it can run on Windows, WSL provides better integration with the Linux-based toolchain.

### Pomodoro 1: Google API Setup (25 minutes)

1. **Create Google Cloud Project** (5 minutes)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one

2. **Enable Calendar API** (5 minutes)
   - Navigate to APIs & Services > Library
   - Search for "Google Calendar API"
   - Click Enable

3. **Create OAuth Credentials** (10 minutes)
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download credentials as `credentials.json`

4. **Setup Project** (5 minutes)
   ```bash
   cd ~/Code/calendar-mcp
   # Copy credentials from Windows if needed:
   cp /mnt/c/Code/calendar-mcp/credentials.json .
   python3.11 -m pip install -r requirements.txt
   ```

### Pomodoro 2: Configuration & Testing (25 minutes)

1. **Test Authentication** (10 minutes)
   ```bash
   cd src
   python3.11 server.py
   ```
   - First run will open browser for OAuth flow
   - Grant calendar permissions
   - `token.json` will be created automatically

2. **Configure Claude** (10 minutes)
   - Add MCP server to Claude configuration
   - Test basic calendar operations

3. **Verification** (5 minutes)
   - Create test event through Claude
   - Verify event appears in Google Calendar

## System Architecture

```
Claude Chat Interface
        ↓
MCP Protocol Communication
        ↓
Local MCP Server (Python/Ubuntu WSL)
        ↓ 
Google Calendar API
        ↓
Your Google Calendar
```

**Key Components:**
• **MCP Server**: Handles protocol communication and tool definitions
• **Google Auth**: OAuth2 flow for secure API access
• **Calendar Client**: Wraps Google Calendar API operations
• **Tool Interface**: Exposes calendar operations to Claude

## 🎯 Enhanced Calendar API Responses

### Day-of-Week Computed Fields

All calendar tools now return enhanced responses with computed date information to eliminate day-of-week calculation errors. Every calendar event includes a `computed` field with:

```json
{
  "computed": {
    "startDay": "Saturday",      // Day of the week for start date
    "endDay": "Saturday",        // Day of the week for end date
    "startDate": "2025-09-27",   // ISO date format (YYYY-MM-DD)
    "endDate": "2025-09-27",     // ISO date format (YYYY-MM-DD)
    "duration": "1 hour",        // Human-readable duration
    "spansMultipleDays": false   // Whether event spans multiple calendar days
  }
}
```

**Key Benefits:**
- ✅ **Timezone-aware calculations** using Python's `zoneinfo`
- ✅ **DST transition handling** for accurate time calculations
- ✅ **Backward compatibility** - all original fields preserved
- ✅ **Error resilience** - graceful fallback if computation fails

## Available Tools

### create_calendar_event
Creates new calendar events with full feature support and enhanced computed fields.

**Required Parameters:**
• `calendar_id`: Target calendar (use "primary" for main calendar)
• `summary`: Event title
• `start_time`: ISO format datetime (e.g., "2024-12-25T10:00:00")
• `end_time`: ISO format datetime

**Optional Parameters:**
• `description`: Event details
• `location`: Physical or virtual location
• `attendees`: Array of email addresses
• `timezone`: Timezone (defaults to EST)

**Enhanced Response:**
```json
{
  "id": "new-event-id",
  "summary": "Team Meeting",
  "start": {"dateTime": "2025-09-27T14:00:00-04:00", "timeZone": "America/Toronto"},
  "end": {"dateTime": "2025-09-27T15:00:00-04:00", "timeZone": "America/Toronto"},
  "computed": {
    "startDay": "Saturday",
    "duration": "1 hour",
    "spansMultipleDays": false
  }
}
```

### update_calendar_event
Modifies existing calendar events.

**Required Parameters:**
• `calendar_id`: Target calendar
• `event_id`: ID of event to update

**Optional Parameters:** (same as create, only specified fields are updated)

### delete_calendar_event
Removes calendar events.

**Required Parameters:**
• `calendar_id`: Target calendar
• `event_id`: ID of event to delete

### list_calendar_events
Lists calendar events with enhanced day-of-week information.

**Parameters:**
• `calendar_id`: Target calendar (defaults to "primary")
• `time_min`: Start time filter (ISO format)
• `time_max`: End time filter (ISO format)
• `max_results`: Maximum events to return
• `q`: Search query

**Enhanced Response Example:**
```json
{
  "events": [
    {
      "id": "event-id",
      "summary": "Weekly Standup",
      "start": {"dateTime": "2025-09-29T09:00:00-04:00", "timeZone": "America/Toronto"},
      "end": {"dateTime": "2025-09-29T09:30:00-04:00", "timeZone": "America/Toronto"},
      "location": "Conference Room B",
      "description": "Weekly team sync",
      "computed": {
        "startDay": "Monday",
        "endDay": "Monday",
        "startDate": "2025-09-29",
        "endDate": "2025-09-29",
        "duration": "30 minutes",
        "spansMultipleDays": false
      }
    }
  ],
  "count": 1
}
```

### list_calendars
Returns all accessible calendars with IDs and permissions.

## Configuration for Claude

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python3.11",
      "args": ["/home/adam/Code/calendar-mcp/src/server.py"],
      "cwd": "/home/adam/Code/calendar-mcp"
    }
  }
}
```

## Usage Examples

### Create Meeting
```
Claude, create a team meeting for tomorrow at 2 PM EST for 1 hour. 
Include john@company.com and jane@company.com. 
Set location as "Conference Room A".
```

### Update Event
```
Claude, move my 3 PM meeting today to 4 PM and add bob@company.com as an attendee.
```

### Delete Event
```
Claude, cancel my meeting with the client scheduled for Friday.
```

## Security & Privacy

• **Local Authentication**: OAuth tokens stored locally in WSL, never transmitted to Claude
• **Scope Limitation**: Only calendar access, no other Google services
• **User Control**: You authorize each calendar operation through Claude
• **Token Management**: Automatic refresh handling, manual revocation available

## Troubleshooting

### Authentication Issues
- Delete `token.json` and re-run server to re-authenticate
- Verify `credentials.json` is valid and in project root
- Check Google Cloud project has Calendar API enabled

### MCP Connection Issues
- Verify Python path in Claude configuration points to WSL location
- Check server starts without errors: `python3.11 src/server.py`
- Review Claude logs for connection errors
- Ensure WSL is running and accessible

### WSL-Specific Issues
- Verify WSL can access the internet for Google API calls
- Check Python 3.11 is installed: `python3.11 --version`
- Install Python 3.11: `sudo apt update && sudo apt install python3.11 python3.11-pip`

### Calendar Operation Failures
- Confirm calendar_id is correct (use list_calendars tool)
- Verify event_id exists for update/delete operations
- Check datetime format (ISO 8601 required)

### Day-of-Week Accuracy Issues
- **Issue resolved**: Calendar responses now include computed `startDay`/`endDay` fields
- If missing computed fields: Verify you're using the enhanced MCP server version
- For legacy responses: Update to latest server version with day-of-week enhancements
- Timezone issues: Check that event timezone matches expected region (EST/PST/UTC)

## Testing

Run unit tests in WSL:
```bash
cd ~/Code/calendar-mcp/tests
python3.11 -m pytest test_server.py -v
```

Tests cover:
• Event creation with various configurations
• Update and delete operations
• Error handling and edge cases
• Authentication flow simulation

## Development Notes

**Ubuntu WSL Environment:**
• Preferred development environment for better tool integration
• Native Linux Python environment
• Seamless integration with VSCode and Claude Code
• Better compatibility with MCP toolchain

**Modern Python Practices:**
• Type hints throughout
• Async/await pattern for MCP
• Proper error handling with try/catch
• Structured logging

**Code Organization:**
• Separation of concerns (auth, API, MCP)
• Tool definitions match Claude expectations
• Comprehensive input validation

This MCP bridges your Ubuntu WSL development environment with Google Calendar while maintaining security through local credential storage and explicit user authorization of each operation.
