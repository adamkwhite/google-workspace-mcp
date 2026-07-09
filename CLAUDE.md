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

## MCP Configuration Guidance (for AI agents)

When helping a user write their Claude Desktop `claude_desktop_config.json` for this project, do not copy example paths verbatim. The templates in `config/` use `<ABSOLUTE_PATH_TO_REPO>` as a placeholder that the user must replace with the absolute path to their clone. Previous agent-generated configs have failed by pasting `/home/user/google-workspace-mcp` (a placeholder) into the live config, which silently breaks the MCP connection because no such directory exists.

Before producing a config:
1. Get the user's actual absolute path — ask them, or run `pwd` from the repo root if you have shell access. Never guess.
2. Check which virtualenv directory exists: `ls -d .venv venv 2>/dev/null`. The setup script creates `.venv/`, but older clones may have `venv/`. The `scripts/run_server.sh` wrapper handles both; a direct config line must pick one.
3. For Windows Claude Desktop with WSL, use the `wsl.exe` form from `config/claude_desktop_config.json`. For native Linux/macOS, drop the `wsl.exe` wrapper and call the venv Python directly (see `config/claude_desktop_config_alternative.json`).
4. After the user updates the config, Claude Desktop must be fully quit and relaunched — MCP servers only load at startup.

### Do not insert `--` between `bash` and `-c`

The correct form is `"bash", "-c", "<command>"`. Do **not** write `"bash", "--", "-c", "<command>"` — the `--` ends bash's option parsing, so bash then treats `-c` as a script filename to open, yielding `bash: -c: No such file or directory` and an immediate MCP disconnect. This mistake appeared in an earlier iteration of the template and broke the live Claude Desktop config on startup.

### Claude Code on Linux: same venv pitfall applies to `~/.claude.json`

When this MCP is registered with Claude Code (not Claude Desktop), the config lives in `~/.claude.json` under `projects[<repo-path>].mcpServers["google-workspace"]`. The same `.venv` vs `venv` drift that breaks Claude Desktop configs breaks this one too — `source venv/bin/activate` silently no-ops, the system Python runs without deps, and the server fails to connect. The same entry often appears duplicated under multiple project scopes in `~/.claude.json`; fix all occurrences.

## Essential Commands

### Development Setup
```bash
# Initial setup (creates .venv, installs deps, guides OAuth2 setup)
./scripts/setup.sh

# Activate virtual environment (required for all development)
source .venv/bin/activate

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

- Always activate virtual environment: `source .venv/bin/activate`
- OAuth2 requires browser for initial authentication
- Use `python scripts/configure_scopes.py` for easy service configuration
- Tool registration is conditional based on config/scopes.json
- Scope changes require token deletion and re-authentication
- Error handling provides clear messages about disabled services
- Test configuration with `get_mcp_configuration` tool

### Gmail Label Filtering

**Implementation Pattern**:
- Lazy initialization: Labels fetched on first Gmail operation
- Label caching: Gmail API labels.list() called once per server instance
- Query enhancement: search_emails automatically appends a `label:"Name"` filter; `restricted_label` may be a single string or a list of names, which are OR-ed and quoted
- Operation blocking: send_email and create_draft raise ValueError when restricted
- Configuration validation: Empty/non-string labels rejected at startup

**Key Files**:
- `src/tools/gmail.py`: Label resolution, query enhancement, operation blocking
- `src/utils/scope_manager.py`: Gmail settings validation
- `config/scopes.json`: User configuration for restricted_label

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

## Current Status (Updated: 2026-03-28)

**Current Branch**: `main`

**Recent Work Completed**:
- PR #68: Refactored GoogleAuthManager.initialize() to reduce cognitive complexity
  - Extracted helper methods: _validate_scope_configuration, _load_existing_credentials, _resolve_credentials, _save_and_deploy_credentials
  - Replaced sync subprocess.run() with asyncio.create_subprocess_exec()
  - Resolved SonarCloud code smells (cognitive complexity + async subprocess)
- PR #67: Skip secret-dependent CI steps for Dependabot PRs
- PR #65: Gmail label-based access restriction

**Test Coverage**: 222 tests passing
- All existing tests continue to pass after auth refactor

**Known Issues & Improvements**:
- Issue #36: Test organization could be improved (low priority)
- Issue #6: Refactor duration formatting (refactoring)
- Issues #11-13: Future features (Sheets, Slides, Gmail enhancements)
- Issue #56: User-configurable holiday regions (future enhancement)

**Next Steps**:
- Address remaining low-priority refactoring issues (#36, #6)
- Evaluate feature requests (Sheets, Slides, Gmail enhancements)
- Consider user-configurable holiday regions (#56)

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
