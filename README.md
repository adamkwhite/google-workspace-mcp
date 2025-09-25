# Google Workspace MCP Server

A configurable Model Context Protocol (MCP) server that enables Claude to manage your Google Workspace services. **Choose which services to enable** - Calendar, Gmail, Docs, or any combination. Works with regular Gmail accounts - no Google Workspace subscription required!

## 🔧 User-Configurable Services

**You control which Google services are enabled:**
- ✅ Mix and match: Enable only Calendar + Docs, or Gmail only, etc.
- 🔒 **Minimal permissions**: Only request access to services you actually use
- 🔄 **Easy changes**: Reconfigure anytime with interactive tool
- 🛡️ **Secure**: No unnecessary broad permissions

## Features

### 📅 **Google Calendar**
- Create, update, and delete events
- List calendars and events with **computed day-of-week information**
- Manage attendees and send invitations
- Search events by date or keywords
- **🎯 NEW**: Enhanced responses include accurate day-of-week, duration, and date calculations

### ✉️ **Gmail**
- Send emails with HTML support
- Search emails with Gmail's powerful query syntax
- Create drafts for later editing
- Support for CC/BCC recipients

### 📄 **Google Docs** 
- Create documents with initial content
- Organize in Drive folders
- Share with collaborators

### 📊 **Google Sheets** (Coming Soon)
- Create spreadsheets with data
- Add headers and formatting
- Import data arrays

### 📽️ **Google Slides** (Coming Soon)
- Create presentations
- Add slides with different layouts
- Insert content

## Quick Start

### Prerequisites
- Python 3.11+
- Gmail account
- Google Cloud project (free)

### Setup (5 minutes)

1. **Clone and setup**:
   ```bash
   cd google-workspace-mcp
   ./scripts/setup.sh
   ```

2. **Configure services** (choose which to enable):
   ```bash
   python scripts/configure_scopes.py
   ```

3. **Enable Google APIs** (only for services you selected):
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable APIs for your selected services:
     - Google Calendar API (if Calendar enabled)
     - Gmail API (if Gmail enabled)
     - Google Docs API (if Docs enabled)
     - Google Drive API (if Docs enabled - required dependency)

4. **Create OAuth2 credentials**:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Choose "Desktop app"
   - Download as `config/credentials.json`

5. **Configure Claude Desktop**:
   Add to your Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "google-workspace": {
         "command": "python",
         "args": ["/home/adam/Code/google-workspace-mcp/src/server.py"],
         "env": {
           "PYTHONPATH": "/home/adam/Code/google-workspace-mcp/src"
         }
       }
     }
   }
   ```

6. **First run** will open browser for authentication (only for enabled services)

## 🎯 Enhanced Calendar Features

### Day-of-Week Accuracy
Calendar events now include computed fields that eliminate day-of-week calculation errors:

```json
{
  "summary": "Team Meeting",
  "start": {"dateTime": "2025-09-27T14:00:00-04:00", "timeZone": "America/Toronto"},
  "end": {"dateTime": "2025-09-27T15:00:00-04:00", "timeZone": "America/Toronto"},
  "computed": {
    "startDay": "Saturday",
    "endDay": "Saturday",
    "startDate": "2025-09-27",
    "endDate": "2025-09-27",
    "duration": "1 hour",
    "spansMultipleDays": false
  }
}
```

**Benefits:**
- ✅ **Accurate day-of-week** - No more "Friday the 27th" when it's actually Saturday
- ⏰ **Human-readable duration** - "2 hours 30 minutes" instead of manual calculation
- 📅 **Date consistency** - Reliable YYYY-MM-DD format
- 🌐 **Timezone-aware** - Proper handling of EST, PST, UTC, and DST transitions

## Usage Examples

### Calendar Management
```
"Schedule a team meeting tomorrow at 2 PM for 1 hour with john@example.com and jane@example.com"
"Move my 3 PM meeting today to 4 PM"
"Show me all meetings this week"
"Find a free slot for a 30-minute call with the marketing team"
```

### Email Operations
```
"Send an email to the team about the project update"
"Search for emails from John about the budget"
"Create a draft email for the monthly newsletter"
"Find all unread emails from this week"
```

### Document Creation
```
"Create a meeting notes document for today's standup"
"Make a project proposal document and share it with sarah@example.com"
"Generate a report template in my Reports folder"
```

### Integrated Workflows
```
"Schedule a project review meeting next Monday at 10 AM, create an agenda document, and email the invite to the team"
"Find all emails about Q4 planning and create a summary document"
"Create a presentation about our new feature and schedule a demo meeting"
```

## 🔧 Managing Service Configuration

### Interactive Configuration
```bash
# Run the configuration wizard
python scripts/configure_scopes.py
```

The interactive tool helps you:
- ✅ See current configuration
- 🔧 Enable/disable services
- ⚠️ Handle dependencies automatically
- 🗑️ Clean up authentication tokens when needed

### Manual Configuration
Edit `config/scopes.json` directly:
```json
{
  "enabled_services": {
    "calendar": true,   # Enable Google Calendar
    "gmail": false,    # Disable Gmail
    "docs": true,      # Enable Google Docs
    "drive": true      # Auto-enabled (required for Docs)
  }
}
```

### Checking Configuration
In Claude, use: `get_mcp_configuration` to see:
- Which services are enabled
- Required API scopes
- Configuration errors
- Available tools

## Available Tools (Conditional)

**Note**: Only tools for enabled services are available

### Configuration Tools (Always Available)
- `get_mcp_configuration` - Show current service configuration

### Calendar Tools (if enabled)
- `create_calendar_event` - Create new events with full details and computed fields
- `list_calendars` - Show all available calendars
- `list_calendar_events` - Search and list events with enhanced day-of-week information

### Gmail Tools (if enabled)
- `send_email` - Send emails with HTML support
- `search_emails` - Search with Gmail query syntax
- `create_email_draft` - Save drafts for later

### Document Tools (if enabled)
- `create_google_doc` - Create documents with content
- `update_google_doc` - Add content to existing documents

## Project Structure

```
google-workspace-mcp/
├── config/
│   ├── scopes.json        # Service configuration (user-editable)
│   ├── credentials.json   # OAuth2 credentials from Google
│   └── token.pickle      # Cached authentication token
├── src/                    # Application source code
│   ├── server.py          # Main MCP server (conditional tool registration)
│   ├── utils/
│   │   ├── scope_manager.py # Service configuration management
│   │   └── date_helpers.py  # Enhanced timezone-aware date calculations
│   ├── auth/
│   │   └── google_auth.py # Dynamic authentication
│   └── tools/             # Service-specific implementations
├── scripts/
│   └── configure_scopes.py # Interactive configuration tool
│   ├── auth/              # Shared authentication
│   └── tools/             # Tool implementations
│       ├── calendar.py    # Calendar operations
│       ├── gmail.py       # Email operations
│       ├── docs.py        # Document creation
│       ├── sheets.py      # Spreadsheet creation
│       └── slides.py      # Presentation creation
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── scripts/               # Setup and deployment
└── config/                # Configuration files
```

## Security

- OAuth2 authentication with secure token storage
- **Calendar-only permissions** - this MCP only requests Google Calendar access
- Tokens stored locally, never transmitted
- Automatic token refresh
- All credentials in `.gitignore`

### Permission Scope
This MCP uses minimal Google API permissions:
- `https://www.googleapis.com/auth/calendar` - Full calendar access for add/edit/delete operations

**Note**: Previous versions requested broader permissions (Gmail, Docs, etc.) but this has been restricted to calendar-only for security. If you need other Google services, use separate dedicated MCPs.

## API Quotas (Free Tier)

All quotas are per-user and more than sufficient for personal use:

- Calendar API: 1,000,000 queries/day
- Gmail API: 250 quota units/user/second
- Docs API: 300 requests/minute
- Sheets API: 300 requests/minute
- Slides API: 300 requests/minute
- Drive API: 1,000 requests/100 seconds

## Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest tests/

# Run server manually
python src/server.py

# Format code
black src/
```

## Troubleshooting

### Authentication Issues
- Delete `config/token.pickle` and re-authenticate
- Verify all APIs are enabled in Google Cloud Console
- Check `config/credentials.json` exists and is valid

### Permission Errors
- Ensure all required scopes are included
- Re-authenticate after adding new scopes
- Check API quotas haven't been exceeded

### Tool Errors
- Use `list_calendars` to get correct calendar IDs
- Verify email addresses are valid
- Check datetime formats (ISO 8601)

## Roadmap

- [x] Calendar integration
- [x] **Day-of-week enhancement with computed fields**
- [x] Gmail integration
- [x] Google Docs creation
- [ ] Google Sheets with data import
- [ ] Google Slides with templates
- [ ] Batch operations
- [ ] Advanced search features
- [ ] File attachments

## Contributing

See [todo.md](todo.md) for current tasks and priorities.

## License

MIT
