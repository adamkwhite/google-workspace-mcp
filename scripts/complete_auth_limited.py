#!/usr/bin/env python3
"""Complete authentication with limited scopes that were actually granted."""

import os
import pickle
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from google_auth_oauthlib.flow import InstalledAppFlow

# Use only the scopes that were actually granted
GRANTED_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def main():
    """Complete authentication with the scopes that were actually granted."""
    if len(sys.argv) != 2:
        print("Usage: python complete_auth_limited.py <authorization_code>")
        return 1

    auth_code = sys.argv[1].strip()
    credentials_path = "config/credentials.json"
    token_path = Path("config/token.pickle")

    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return 1

    try:
        print("🔄 Exchanging authorization code for tokens...")
        print("📋 Using granted scopes:")
        for scope in GRANTED_SCOPES:
            print(f"  ✅ {scope}")

        # Create flow with only granted scopes
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, GRANTED_SCOPES
        )
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

        # Exchange code for tokens
        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        # Save credentials
        token_path.parent.mkdir(exist_ok=True)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

        print("✅ Authentication successful!")
        print(f"💾 Token saved to: {token_path}")
        print(f"🔑 Token valid: {creds.valid}")

        if hasattr(creds, "refresh_token") and creds.refresh_token:
            print("🔄 Refresh token available - automatic renewal enabled")
        else:
            print("⚠️  No refresh token - may need to re-authenticate periodically")

        print("\n📝 Note: Limited functionality available:")
        print("  ✅ Google Calendar - Full functionality")
        print("  ✅ Google Docs - Create documents")
        print("  ✅ Google Drive - File management")
        print("  ❌ Gmail - Not authorized (send/read emails)")
        print("  ❌ Google Sheets - Not authorized")
        print("  ❌ Google Slides - Not authorized")

        print("\n🔄 To enable Gmail/Sheets/Slides, you'll need to:")
        print("1. Re-run the OAuth flow")
        print("2. Grant ALL requested permissions")
        print("3. Make sure to click 'Allow' for Gmail access")

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
