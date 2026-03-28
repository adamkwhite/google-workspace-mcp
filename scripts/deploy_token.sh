#!/bin/bash
# Deploy token.pickle to remote hosts after re-authentication
# Called automatically by google_auth.py after new token is saved

TOKEN="$HOME/Code/google-workspace-mcp/config/token.pickle"

if [ ! -f "$TOKEN" ]; then
    echo "Token not found: $TOKEN"
    exit 1
fi

echo "Deploying token to hostinger..."
scp "$TOKEN" hostinger:/app/calendar_token.pickle && echo "Done." || echo "Failed to deploy to hostinger."
