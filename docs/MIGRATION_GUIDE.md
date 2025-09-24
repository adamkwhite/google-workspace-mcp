# Migration Guide: From Separate MCPs to Unified Google Workspace MCP

## Overview
The Google Workspace MCP consolidates multiple separate MCP servers into one unified solution:
- **calendar-mcp** → Now integrated as Calendar tools
- **Document creation tools** → Now integrated as Docs/Sheets/Slides tools
- **NEW: Gmail integration** → Send, search, and draft emails

## Benefits of Migration
1. **Single Authentication** - One OAuth2 flow for all Google services
2. **Unified Configuration** - One MCP server in Claude Desktop
3. **Integrated Workflows** - Create events, send emails, and generate documents in one flow
4. **Simplified Maintenance** - One codebase to update

## Migration Steps

### For calendar-mcp Users

1. **Backup Existing Token** (Optional)
   ```bash
   cp ~/Code/calendar-mcp/token.json ~/Code/calendar-mcp/token.json.backup
   ```

2. **Install Google Workspace MCP**
   ```bash
   cd ~/Code/google-workspace-mcp
   ./scripts/setup.sh
   ```

3. **Copy Existing Token** (Skip re-authentication)
   ```bash
   # If you want to reuse your existing authentication
   cp ~/Code/calendar-mcp/token.json ~/Code/google-workspace-mcp/config/token.pickle
   ```

4. **Update Claude Desktop Configuration**
   
   Replace this:
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
   
   With this:
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

5. **Restart Claude Desktop**

### Tool Name Mapping

The calendar tools have the same names and parameters:

| Old Tool (calendar-mcp) | New Tool (google-workspace-mcp) | Changes |
|------------------------|--------------------------------|---------|
| create_calendar_event | create_calendar_event | None |
| update_calendar_event | update_calendar_event | None |
| delete_calendar_event | delete_calendar_event | None |
| list_calendars | list_calendars | None |
| N/A | list_calendar_events | NEW |

### New Capabilities

With the unified MCP, you now have access to:

#### Gmail Tools
- `send_email` - Send emails with HTML support
- `search_emails` - Search using Gmail query syntax
- `create_email_draft` - Save drafts

#### Document Tools
- `create_google_doc` - Create documents with content
- `create_google_sheet` - Create spreadsheets (coming soon)
- `create_google_presentation` - Create presentations (coming soon)

## Example Workflows

### Before (Multiple Steps)
```
1. Use calendar-mcp: "Create a meeting for tomorrow at 2 PM"
2. Switch context: "Now I need to create a document for the agenda"
3. Manual: Copy meeting details and share via email
```

### After (Integrated)
```
"Schedule a team meeting tomorrow at 2 PM, create an agenda document, and email the team with the details"
```

## Troubleshooting

### Authentication Issues
- If you copied token.json to token.pickle and it doesn't work, delete it and re-authenticate
- The unified MCP requires additional scopes (Gmail, Docs, etc.), so re-authentication may be necessary

### Missing Tools
- All calendar tools are available with the same names
- If a tool seems missing, ensure you've restarted Claude Desktop

### Performance
- The unified MCP has the same performance as individual MCPs
- API quotas are per-service, not affected by consolidation

## Cleanup

After successful migration:
```bash
# Optional: Remove old calendar-mcp
rm -rf ~/Code/calendar-mcp

# Or archive it
mv ~/Code/calendar-mcp ~/Code/calendar-mcp.archived
```

## Need Help?

If you encounter issues:
1. Check that all Google APIs are enabled (Calendar, Gmail, Docs, Sheets, Slides, Drive)
2. Verify the MCP server starts without errors: `python src/server.py`
3. Review Claude Desktop logs for connection errors
4. Ensure you're using Python 3.11+

The unified Google Workspace MCP provides all the functionality of the separate MCPs plus much more, with simpler setup and maintenance.
