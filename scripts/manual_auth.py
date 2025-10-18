#!/usr/bin/env python3
"""Manual authentication script for Google Workspace MCP."""

import os
import pickle
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]


def main():
    """Manually authenticate with Google APIs."""
    credentials_path = "config/credentials.json"
    token_path = Path("config/token.pickle")

    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please download OAuth2 credentials from Google Cloud Console:")
        print("1. Go to APIs & Services > Credentials")
        print("2. Create OAuth client ID (Desktop application)")
        print("3. Download and save as config/credentials.json")
        return

    try:
        print("🔄 Starting OAuth2 authentication flow...")
        print(f"📁 Using credentials: {credentials_path}")
        print(f"💾 Token will be saved to: {token_path}")
        print(f"🔐 Required scopes: {len(SCOPES)} scopes")

        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)

        print("\n🌐 Opening browser for authentication...")
        print("⚠️  If browser doesn't open automatically, copy the URL from the console")

        # Run local server for OAuth callback
        creds = flow.run_local_server(
            port=0,  # Use random available port
            prompt="consent",  # Always show consent screen
            authorization_prompt_message=(
                "Please visit this URL to authorize the application: {url}"
            ),
            success_message="Authentication successful! You can close this browser tab.",
        )

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

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
