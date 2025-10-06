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

## Documentation Accuracy & Maintenance

**Critical**: Keep README claims aligned with actual implementation
- **Regular audits**: Check that README features match server.py tool registrations
- **Implementation vs Documentation**: If code has methods but they're not exposed as MCP tools, don't claim the functionality in README
- **User expectations**: Misleading documentation creates poor user experience when features don't work as advertised
- **Example**: Calendar had `update_event()`/`delete_event()` methods but no MCP tools registered → README claimed "update, and delete events" → Users couldn't actually do this

## GitHub Actions & Workflow Debugging

**Common Issues and Solutions**:
- **Workflow validation errors**: Claude Code Action requires identical workflow files between main and PR branches for security
- **Invalid CLI flags**: Remove unsupported flags like `--allowed-bots` that cause immediate failures
- **YAML syntax**: GitHub validation can be "lazy" - config errors may not surface until PR triggers validation
- **Workflow interdependencies**: Failed workflows can prevent other validations from running
- **Debugging approach**: Fix one workflow at a time, rebase/force-push to trigger fresh validation

## Current Status (Updated: 2025-10-06)

**Current Branch**: `main`

**Recent Work Completed**:
- PR #32: Removed redundant regex validation in date validation (Issue #30)
- PR #33: Added empty metadata edge case handling (Issue #20)
- PR #34: Extracted magic numbers to named constants (Issue #27)
- PR #35: Added edge case tests for date validation (Issue #31)
- Issue #36: Created for test organization improvements (low priority)

**Test Coverage**: 168 tests passing, ~85% coverage
- Unit tests for metadata validation
- Edge case coverage for date validation
- Empty metadata handling tests

**Known Issues & Improvements**:
- Issue #36: Test organization could be improved (low priority)
- Issue #21: TypedDict for metadata type safety (enhancement)
- Issues #11-13: Future features (Sheets, Slides, Gmail enhancements)

**Next Steps**:
- Consider Issue #21 (TypedDict) for improved type safety
- Address remaining low-priority refactoring issues
- Evaluate feature requests (Sheets, Slides, Gmail enhancements)

## Metadata Validation System

**Security Architecture** (src/tools/calendar.py):
- **Input Validation**: All metadata fields validated before storage
- **HTML Escaping**: Prevents XSS attacks via html.escape()
- **URL Whitelisting**: Only claude.ai domain allowed for chat_url
- **Length Limits**: Constants MAX_CHAT_TITLE_LENGTH (200), MAX_PROJECT_NAME_LENGTH (100)
- **Date Validation**: strptime enforces strict ISO format (YYYY-MM-DD)
- **Double-Escaping Prevention**: Metadata stripped before re-validation on updates

**Validation Methods**:
- `_validate_text_field()`: HTML escaping, length limits, non-empty checks
- `_validate_url_field()`: HTTPS enforcement, domain whitelisting
- `_validate_date_field()`: ISO format validation using strptime
- `_validate_metadata()`: Orchestrates validation for all fields
- `_format_metadata()`: Formats validated metadata with empty content check

**Critical Patterns**:
- Input must be raw, unescaped text (validation applies escaping)
- strptime provides strict validation (rejects Feb 30, day 0, negative values)
- Empty metadata returns empty string to avoid visual clutter
- Metadata section stripped before updates to prevent double-escaping