# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Type**: Model Context Protocol (MCP) server for Google Workspace integration
**Purpose**: Configurable interface for Calendar, Gmail, and Google Docs operations
**Status**: User-configurable service scoping with granular permissions
**Security**: Uses minimal API scopes based on user-configured services

Works with regular Gmail accounts - no Google Workspace subscription required.

## IMPORTANT: User-Configurable Scope Policy

**Users control which Google services are enabled**:
- Services are configured via `config/scopes.json`
- Only enabled services require authentication permissions
- Users can enable/disable: Calendar, Gmail, Google Docs individually
- Dependencies are automatically handled (e.g., Docs requires Drive)
- Scope changes trigger automatic re-authentication

## Essential Commands

### Development Setup
```bash
# Initial setup (creates venv, installs deps, guides OAuth2 setup)
./scripts/setup.sh

# Activate virtual environment (required for all development)
source venv/bin/activate

# Run MCP server directly for testing
python src/server.py
```

### Testing & Development
```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_docs.py -v

# Test integration (requires valid credentials)
python scripts/test_integration.py

# Format code (if needed)
black src/
```

### Scope Configuration
```bash
# Interactive scope configuration
python scripts/configure_scopes.py

# View current configuration
cat config/scopes.json

# Reset to defaults (enables all services)
rm config/scopes.json
```

### Authentication Troubleshooting
```bash
# Remove cached tokens to re-authenticate
rm config/token.pickle

# Verify credentials file exists
ls -la config/credentials.json

# Check MCP configuration
# (Use get_mcp_configuration tool in Claude)
```

## Key Architecture

### Core Structure
- **src/server.py**: Main MCP server entry point, conditionally registers tools based on config
- **src/auth/google_auth.py**: Dynamic OAuth2/Service Account authentication based on enabled services
- **src/tools/**: Individual tool implementations, each handling a specific Google service
- **src/utils/scope_manager.py**: Manages service configuration and scope validation
- **config/scopes.json**: User configuration file for enabled services

### Critical Patterns
1. **Dynamic Authentication**: GoogleAuthManager loads scopes based on user configuration
2. **Conditional Tool Registration**: Only enabled services have tools registered
3. **Service Validation**: Tools check if service is enabled before execution
4. **Dependency Management**: Required services (e.g., Drive for Docs) are auto-enabled
5. **Scope Change Detection**: Forces re-authentication when configuration changes

### Authentication Flow
1. User configures services in config/scopes.json (or uses interactive script)
2. ScopeManager validates configuration and resolves dependencies
3. OAuth2 credentials from Google Cloud Console → config/credentials.json
4. First run opens browser for permission grant (only for enabled services)
5. Token cached in config/token.pickle for reuse
6. Auto-refresh handles token expiration
7. Scope changes detected and force re-authentication

## Available MCP Tools (Conditionally Registered)

### Configuration Tools (Always Available)
- `get_mcp_configuration`: Show current service configuration and status

### Calendar Tools (if 'calendar' enabled)
- `create_calendar_event`, `list_calendars`, `list_calendar_events`

### Gmail Tools (if 'gmail' enabled)
- `send_email`, `search_emails`, `create_email_draft`

### Document Tools (if 'docs' enabled)
- `create_google_doc`, `update_google_doc`

### Service Dependencies
- Google Docs tools require 'drive' service to be enabled
- Dependencies are automatically resolved during configuration

## Development Notes

- Always activate virtual environment: `source venv/bin/activate`
- OAuth2 requires browser for initial authentication
- Use `python scripts/configure_scopes.py` for easy service configuration
- Tool registration is conditional based on config/scopes.json
- Scope changes require token deletion and re-authentication
- Error handling provides clear messages about disabled services
- Test configuration with `get_mcp_configuration` tool