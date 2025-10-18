# Git History Cleanup - Security Audit

**Date:** October 18, 2025
**Completed by:** Adam White (with Claude Code assistance)

## Summary

Successfully removed exposed OAuth credentials from git history and made repository public. All sensitive data scrubbed using BFG Repo Cleaner while preserving complete commit history (47 commits across 10 branches).

## Problem

Repository contained exposed OAuth credentials in commit history from initial commit (June 8, 2025):
- `credentials.json` - OAuth Client Secret: `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`
- `token.json` - Google refresh token with long-term account access
- Files were deleted in later commit but remained in git history

## Security Response

### Phase 1: Credential Revocation (CRITICAL)
1. **Deleted compromised OAuth client** in Google Cloud Console
   - Project: `idyllic-lattice-462219-p7`
   - Client ID: `58597593767-fbg4ogp12l8n065ef13gghk02s13pj1h.apps.googleusercontent.com`
   - This immediately invalidated client secret and all issued tokens
2. **Created new OAuth credentials** and downloaded fresh `config/credentials.json`
3. **Removed local tokens** (`config/token.pickle`) to force re-authentication
4. **Verified account permissions** - No unauthorized apps found

### Phase 2: Git History Cleaning (BFG Repo Cleaner)
1. **Created backup:** `/home/adam/Code/google-workspace-mcp-backup`
2. **Installed Java 21** for BFG execution
3. **Downloaded BFG 1.14.0** to `/home/adam/Code/bfg-1.14.0.jar`
4. **Ran BFG operations:**
   ```bash
   java -jar ../bfg-1.14.0.jar --delete-files credentials.json
   java -jar ../bfg-1.14.0.jar --delete-files token.json
   ```
   - Processed 92 commits
   - Removed credentials.json (413 B)
   - Removed token.json (704 B)
   - Updated 29 refs across 10 branches
5. **Cleaned repository:**
   ```bash
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```
6. **Verified removal:**
   - Old commit IDs (`83a7189d`) no longer accessible
   - Sensitive files completely removed from history
   - All 47 commits preserved with new SHA hashes

### Phase 3: Repository Publication
1. **Force pushed cleaned history:**
   ```bash
   git push --force origin --all
   ```
   - 10 branches updated successfully
   - All commit messages and authorship preserved
2. **Made repository public:**
   ```bash
   gh repo edit adamkwhite/google-workspace-mcp --visibility public
   ```
   - Live at: https://github.com/adamkwhite/google-workspace-mcp

## Verification

✅ **Security Checks Passed:**
- No forks existed (forkCount: 0)
- Repository was always private (no public caching)
- Old OAuth credentials are revoked and useless
- Git history verified clean locally and remotely
- `.gitignore` properly excludes sensitive files

✅ **History Integrity:**
- All 47 commits preserved
- All commit messages intact
- Complete authorship attribution maintained
- Branch structure unchanged (10 branches)
- PR references preserved (38 PRs)

## Key Lessons

1. **Layered Security:** Credential revocation (Phase 1) is the critical kill switch - even if history cleaning failed, dead credentials can't harm you
2. **Private Repos:** No 24-48 hour cache delay needed because repo was never public
3. **BFG Best Practice:** Keep `.jar` file outside repository for reusability
4. **Force Push Safety:** `--force-with-lease` fails after history rewrites; plain `--force` required

## Files Modified

- `.gitignore` - Already properly configured (no changes needed)
- Git history - Rewritten across all branches
- Remote branches - Force updated on GitHub

## Related Tools & Dependencies

- **BFG Repo Cleaner 1.14.0** - https://rephrase.net/box/bfg/
- **Java 21** - Required for BFG execution
- **GitHub CLI** - Repository visibility management

## Post-Cleanup State

- **Repository:** Public at https://github.com/adamkwhite/google-workspace-mcp
- **Local Backup:** `/home/adam/Code/google-workspace-mcp-backup`
- **New Credentials:** `config/credentials.json` (OAuth client created Oct 18, 2025)
- **BFG Reports:** `/home/adam/Code/google-workspace-mcp.bfg-report/2025-10-18/`

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
