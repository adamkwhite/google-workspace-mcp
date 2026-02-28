# Google Workspace MCP Server

A configurable Model Context Protocol (MCP) server that enables Claude to manage your Google Workspace services. **Choose which services to enable** - Calendar, Gmail, Docs, or any combination. Works with regular Gmail accounts - no Google Workspace subscription required!

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_google-workspace-mcp&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=adamkwhite_google-workspace-mcp)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_google-workspace-mcp&metric=bugs)](https://sonarcloud.io/summary/new_code?id=adamkwhite_google-workspace-mcp)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_google-workspace-mcp&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=adamkwhite_google-workspace-mcp)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_google-workspace-mcp&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=adamkwhite_google-workspace-mcp)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_google-workspace-mcp&metric=coverage)](https://sonarcloud.io/summary/new_code?id=adamkwhite_google-workspace-mcp)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_google-workspace-mcp&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=adamkwhite_google-workspace-mcp)

## 🔧 User-Configurable Services

**You control which Google services are enabled:**
- ✅ Mix and match: Enable only Calendar + Docs, or Gmail only, etc.
- 🔒 **Minimal permissions**: Only request access to services you actually use
- 🔄 **Easy changes**: Reconfigure anytime with interactive tool
- 🛡️ **Secure**: No unnecessary broad permissions

## Features

### 📅 **Google Calendar**
- Create events with enhanced day-of-week calculations
- **🎉 NEW**: Smart holiday detection and scheduling
  - Automatically prevents scheduling on US and Canadian holidays
  - Suggests alternative working days when holidays detected
  - Optional force_holiday_booking parameter to override
- List calendars and events with **computed day-of-week information**
- Manage attendees and send invitations
- Search events by date or keywords
- Enhanced responses include accurate day-of-week, duration, and date calculations

### ✉️ **Gmail**
- Send emails with HTML support
- Search emails with Gmail's powerful query syntax
- Create drafts for later editing
- Support for CC/BCC recipients
- **🎯 NEW**: Label-based access restriction
  - Optional filtering to restrict access to emails with specific label (e.g., "Jobs")
  - When enabled: search_emails filters automatically, send/draft operations blocked
  - Configurable via interactive setup or config/scopes.json

### 📄 **Google Docs**
- Create documents with initial content
- Update existing documents with new content
- Organize in Drive folders
- Share with collaborators

### 📊 **Google Sheets** (Not Implemented)
- Create spreadsheets with data
- Add headers and formatting
- Import data arrays

### 📽️ **Google Slides** (Not Implemented)
- Create presentations
- Add slides with different layouts
- Insert content

## Security & Design Principles

**🛡️ Safe-by-Design: Intentionally Limited Operations**

This MCP server follows the principle of least privilege by intentionally excluding destructive operations:

### ✅ **Supported Operations:**
- **Read**: List calendars/events, search emails, view documents
- **Create**: New events, emails, drafts, documents
- **Update**: Modify existing documents
- **Send**: Send emails (with explicit user intent)

### ❌ **Intentionally Excluded:**
- **Delete**: No deletion of events, emails, or documents
- **Trash**: No moving items to trash
- **Permanent removal**: No irreversible data destruction

**Why?** This design provides an additional safety layer:
- Prevents accidental data loss through AI interaction
- Requires manual confirmation via Google UIs for destructive actions
- Aligns with security best practice: "AI can create and modify, humans confirm deletion"
- Reduces risk of unintended consequences from misunderstood prompts

**Manual Cleanup:** Test data created through the MCP server (calendar events, documents, emails) should be deleted manually through Google Calendar, Drive, or Gmail interfaces.

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
"Schedule a planning session next week" (automatically avoids holidays)
"Book a meeting on December 25th" (prompts: "This is Christmas. Continue? y/n")
"Show me all meetings this week with day-of-week information"
"List my calendar events for next Monday"
"Search for events with 'project review' in the title"
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
  },
  "gmail_settings": {
    "restricted_label": "Jobs"  # Optional: Restrict Gmail to specific label
  }
}
```

### Gmail Label Filtering

Restrict Gmail operations to emails with a specific label:

**Configuration**:
```json
{
  "enabled_services": {
    "gmail": true
  },
  "gmail_settings": {
    "restricted_label": "Jobs"
  }
}
```

**Behavior**:
- ✅ **search_emails**: Automatically filters to only show emails with "Jobs" label
- 🚫 **send_email**: Blocked with clear error message
- 🚫 **create_email_draft**: Blocked with clear error message

**Use Cases**:
- Job search: Only access emails related to job applications
- Client communications: Restrict to specific client label
- Privacy: Limit AI access to subset of emails

**Setup**:
1. Create label in Gmail (e.g., "Jobs")
2. Run `python scripts/configure_scopes.py` and enable Gmail label filtering
3. Or manually add `gmail_settings` to `config/scopes.json`
4. Restart MCP server

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
- `create_calendar_event` - Create new events with computed day-of-week fields
- `list_calendars` - Show all available calendars
- `list_calendar_events` - Search and list events with enhanced date information

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
│       ├── calendar.py    # Calendar operations
│       ├── gmail.py       # Email operations
│       └── docs.py        # Document creation
├── scripts/
│   └── configure_scopes.py # Interactive configuration tool
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── scripts/               # Setup and deployment
└── config/                # Configuration files
```

## Security

- OAuth2 authentication with secure token storage
- **User-configurable service permissions** - Enable only Calendar, Gmail, Docs, or any combination
- Minimal scope requests based on enabled services:
  - Calendar: `https://www.googleapis.com/auth/calendar` (if enabled)
  - Gmail: `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.readonly` (if enabled)
  - Docs: `https://www.googleapis.com/auth/documents`, `https://www.googleapis.com/auth/drive.file` (if enabled)
- Tokens stored locally, never transmitted
- Automatic token refresh
- All credentials in `.gitignore`

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

- [x] Calendar integration with computed date fields
- [x] Gmail integration (send, search, drafts)
- [x] Google Docs creation and updates
- [x] User-configurable service scoping
- [ ] Calendar event updates and deletion
- [ ] Google Sheets with data import
- [ ] Google Slides with templates
- [ ] Batch operations
- [ ] Advanced search features
- [ ] File attachments

## Contributing

See [todo.md](todo.md) for current tasks and priorities.

## License

MIT
