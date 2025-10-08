# OAuth2 Refresh Token Implementation PRD

## Overview
Implement automatic OAuth2 token refresh to prevent authentication failures after the 1-hour access token expiration. Currently, users must manually re-authenticate every hour during active use, causing workflow disruption and Claude Desktop connection failures.

## Problem Statement
Google OAuth2 access tokens expire after 60 minutes. When the token expires, Claude Desktop enters a failure loop, attempting to reconnect 10 times before giving up with the error: `invalid_grant: Token has been expired or revoked`. This forces users to manually re-authenticate every hour, breaking their workflow and requiring them to restart Claude Desktop.

## Goals

### Primary Goals
• Eliminate manual re-authentication requirements during active work sessions
• Enable continuous operation for 8+ hours without user intervention
• Prevent Claude Desktop connection failure loops

### Secondary Goals  
• Implement transparent token refresh (no user notification)
• Support cross-platform operation (Windows, macOS, Linux/WSL)
• Maintain backward compatibility with existing token storage

## Success Criteria
- [ ] System operates for 8+ hours without manual re-authentication
- [ ] Token refresh occurs automatically before expiration
- [ ] Claude Desktop maintains stable connection without failure loops
- [ ] All existing Google Workspace MCP functionality continues working
- [ ] Automated tests verify token refresh behavior
- [ ] Cross-platform compatibility verified (Windows, macOS, Linux)

## Requirements

### Functional Requirements
1. **Automatic Token Refresh**: System must automatically refresh OAuth2 access tokens before they expire
2. **Proactive Refresh**: Refresh tokens when 50 minutes have elapsed (10 minutes before expiration)
3. **Fallback Reactive Refresh**: If proactive refresh fails, attempt refresh on authentication failure
4. **Token Persistence**: Store refresh tokens securely and persist across sessions
5. **Transparent Operation**: Token refresh must occur without user notification or intervention
6. **Error Recovery**: Handle refresh failures gracefully without crashing the MCP server

### Technical Requirements
1. **OAuth2 Compliance**: Use Google's OAuth2 refresh token flow correctly
2. **Thread Safety**: Ensure token refresh is thread-safe for concurrent API calls
3. **Token Storage**: Securely store refresh tokens with appropriate file permissions
4. **Expiration Tracking**: Track token expiration time accurately across timezones
5. **Cross-Platform Support**: Work on Windows, macOS, and Linux (WSL)

### Non-Functional Requirements
1. **Performance**: Token refresh must complete within 2 seconds
2. **Security**: Refresh tokens must be stored with restricted file permissions (600 on Unix)
3. **Reliability**: System must handle network interruptions during refresh attempts
4. **Maintainability**: Clear logging of token refresh events for debugging

## User Stories

**As a Google Workspace MCP user:**
• I want to work for a full day without re-authenticating, so my workflow isn't interrupted
• I want Claude Desktop to maintain a stable connection, so I don't lose context during conversations
• I want token refresh to be invisible, so I can focus on my work

**As a developer:**
• I want clear logs of token refresh events, so I can debug authentication issues
• I want automated tests for token refresh, so I can verify the implementation works correctly

## Technical Specifications

### Token Refresh Flow
```python
# Pseudocode for token refresh implementation
class GoogleAuthManager:
    def __init__(self):
        self.token_refresh_buffer = 600  # 10 minutes in seconds
        self.refresh_lock = threading.Lock()
    
    def should_refresh_token(self, creds: Credentials) -> bool:
        """Check if token should be refreshed proactively."""
        if not creds.expiry:
            return False
        time_until_expiry = (creds.expiry - datetime.now(timezone.utc)).total_seconds()
        return time_until_expiry <= self.token_refresh_buffer
    
    async def ensure_valid_credentials(self) -> Credentials:
        """Ensure credentials are valid, refreshing if necessary."""
        with self.refresh_lock:
            if self.should_refresh_token(self.creds):
                await self.refresh_token()
            elif not self.creds.valid:
                await self.refresh_token()
        return self.creds
    
    async def refresh_token(self):
        """Refresh the OAuth2 access token."""
        try:
            self.creds.refresh(Request())
            self.save_credentials()
            logger.info("Token refreshed successfully")
        except RefreshError as e:
            logger.error(f"Token refresh failed: {e}")
            # Trigger re-authentication flow
            await self.reauthenticate()
```

### Token Storage Structure
```python
# Enhanced token storage with metadata
{
    "access_token": "...",
    "refresh_token": "...",
    "expiry": "2025-01-06T15:30:00Z",
    "scopes": ["calendar", "gmail", "docs"],
    "token_version": "2.0",  # Version for migration support
    "last_refresh": "2025-01-06T14:30:00Z"
}
```

### API Integration Points
• Modify `google_auth.py`: Add refresh logic and expiration tracking
• Update all tool modules: Use `ensure_valid_credentials()` before API calls
• Enhance `server.py`: Add background refresh task (optional enhancement)

## Dependencies

### External Dependencies
• `google-auth >= 2.0.0`: Core authentication library with refresh support
• `google-auth-oauthlib >= 1.0.0`: OAuth2 flow implementation
• `google-auth-httplib2 >= 0.1.0`: HTTP transport for token refresh

### Internal Dependencies
• `src/auth/google_auth.py`: Primary implementation location
• `src/utils/scope_manager.py`: Scope validation during refresh
• All tool modules: Must use refreshed credentials

## Timeline

### Phase 1: Core Implementation (Week 1)
• Day 1-2: Implement token refresh logic in `GoogleAuthManager`
• Day 3: Add proactive refresh with timer
• Day 4: Implement reactive refresh on failure
• Day 5: Cross-platform testing

### Phase 2: Testing & Refinement (Week 2)
• Day 1-2: Write unit tests with mocked token expiration
• Day 3: Integration testing with real Google APIs
• Day 4: Error handling and edge cases
• Day 5: Documentation and deployment

## Risks and Mitigation

**Risk**: Refresh token might be revoked by Google
**Mitigation**: Implement graceful fallback to re-authentication flow

**Risk**: Concurrent API calls during token refresh
**Mitigation**: Use thread locks to ensure thread-safe refresh

**Risk**: Network failures during refresh attempt
**Mitigation**: Implement retry logic with exponential backoff

**Risk**: Cross-platform file permission issues
**Mitigation**: Use platform-specific permission settings

## Out of Scope
• Service account key rotation
• Multi-user/multi-account support within single installation
• Advanced retry logic with circuit breakers (can be added later)
• Token refresh for non-Google OAuth providers
• Refresh token rotation (Google doesn't require this)

## Acceptance Criteria

### Development Validation
- [ ] Token refresh occurs automatically at 50-minute mark
- [ ] Reactive refresh triggers on authentication failure
- [ ] Refresh tokens persist across server restarts
- [ ] Thread-safe refresh prevents race conditions
- [ ] Clear logs indicate refresh events

### Testing Requirements
- [ ] Unit test simulates token expiration and refresh
- [ ] Integration test verifies 8-hour continuous operation
- [ ] Cross-platform tests pass on Windows, macOS, Linux
- [ ] Error cases handled (network failure, revoked token)
- [ ] Load test with concurrent API calls during refresh

### User Validation
- [ ] No manual authentication required for 8+ hours
- [ ] Claude Desktop maintains stable connection
- [ ] All Google Workspace tools continue functioning
- [ ] No user-visible interruptions during refresh

## Implementation Approach
**Method**: Traditional (manual implementation with security focus)
**Estimated Completion**: 2 weeks
**Review Checkpoints**: After core implementation, after testing phase

## Related Work
- **Issue #TBD**: Implement OAuth2 refresh token handling (run `./create_refresh_token_issue.sh` to create)
- **PR #TBD**: Token refresh implementation

## GitHub Issue Creation
To create the GitHub issue for this PRD:

1. **From WSL/Linux/macOS:**
   ```bash
   cd /home/adam/Code/google-workspace-mcp
   chmod +x create_refresh_token_issue.sh
   ./create_refresh_token_issue.sh
   ```

2. **From Windows (Git Bash):**
   ```bash
   cd /c/Code/google-workspace-mcp
   bash create_refresh_token_issue.sh
   ```

3. **After creating the issue:**
   - Note the issue number from the output
   - Update the "Related Work" section above with the actual issue number
   - The issue will automatically link back to this PRD location

## References
- [Google OAuth2 Token Refresh Documentation](https://developers.google.com/identity/protocols/oauth2#refresh)
- [google-auth Python Library Refresh Guide](https://google-auth.readthedocs.io/en/latest/user-guide.html#refresh-tokens)
- Current implementation: `src/auth/google_auth.py`

## Open Questions
1. Should we implement a background thread for proactive refresh, or check on each API call?
2. What's the preferred logging level for refresh events (INFO vs DEBUG)?
3. Should we expose refresh metrics/status through an MCP tool for monitoring?
