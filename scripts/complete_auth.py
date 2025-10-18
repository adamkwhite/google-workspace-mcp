#!/usr/bin/env python3
"""Complete Google OAuth authentication with authorization code."""

import os
import pickle
import sys
from pathlib import Path

sys.path.append("src")

from google_auth_oauthlib.flow import InstalledAppFlow

from auth.google_auth import GoogleAuthManager


def complete_auth(auth_code):
    """Complete authentication with authorization code."""
    credentials_path = "config/credentials.json"
    token_path = Path("config/token.pickle")

    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return

    try:
        # Same scopes as GoogleAuthManager
        scopes = GoogleAuthManager.SCOPES

        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
        flow.redirect_uri = "http://localhost:8080"

        # Exchange authorization code for credentials
        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        # Save credentials
        token_path.parent.mkdir(exist_ok=True)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

        print("✅ Authentication completed successfully!")
        print(f"💾 Credentials saved to: {token_path}")
        print()
        print("🚀 You can now use the MCP server with Claude Desktop!")
        print("   The calendar tools should work properly now.")

    except Exception as e:
        print(f"❌ Error completing authentication: {e}")
        print()
        print("🔍 Make sure you:")
        print("   1. Copied the full authorization code correctly")
        print("   2. Didn't include extra characters or spaces")
        print("   3. Used the code quickly (they expire fast)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python complete_auth.py <authorization_code>")
        print()
        print("Example:")
        print("   python complete_auth.py 4/0AdQt8qhtest_authorization_code_here")
        sys.exit(1)

    auth_code = sys.argv[1].strip()
    complete_auth(auth_code)
