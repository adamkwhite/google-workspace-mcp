#!/bin/bash
# Deploy token.pickle to remote hosts after re-authentication.
# Called automatically by google_auth.py after a new token is saved.
#
# NOTE: all diagnostic output is written to stderr. This script is invoked
# from a process whose stdout is the MCP JSON-RPC channel — writing to
# stdout corrupts the protocol and causes client-side parse errors.

TOKEN="$HOME/Code/google-workspace-mcp/config/token.pickle"

if [ ! -f "$TOKEN" ]; then
    echo "Token not found: $TOKEN" >&2
    exit 1
fi

echo "Deploying token to hostinger..." >&2
if scp "$TOKEN" hostinger:/app/calendar_token.pickle >&2; then
    echo "Done." >&2
else
    echo "Failed to deploy to hostinger." >&2
fi
