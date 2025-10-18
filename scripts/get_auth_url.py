#!/usr/bin/env python3
"""Get Google OAuth URL for manual authentication in WSL."""

import os
import sys

sys.path.append("src")

from google_auth_oauthlib.flow import InstalledAppFlow

from auth.google_auth import GoogleAuthManager


def get_auth_url():
    """Get authentication URL for manual browser opening."""
    credentials_path = "config/credentials.json"
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print(
            "Please download OAuth2 credentials from Google Cloud Console "
            "and save as config/credentials.json"
        )
        return

    # Same scopes as GoogleAuthManager
    scopes = GoogleAuthManager.SCOPES

    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
        flow.redirect_uri = "http://localhost:8080"  # Use a standard port

        auth_url, _ = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )

        print("🔗 GOOGLE AUTHENTICATION REQUIRED")
        print("=" * 50)
        print()
        print("1. Copy this URL and open it in your browser:")
        print()
        print(auth_url)
        print()
        print("2. Complete the authentication process")
        print("3. Copy the authorization code from the redirect URL")
        print("4. Run: python complete_auth.py <authorization_code>")
        print()
        print("💡 The redirect URL will look like:")
        print("   http://localhost:8080/?code=AUTHORIZATION_CODE&scope=...")
        print("   Copy just the AUTHORIZATION_CODE part")

    except Exception as e:
        print(f"❌ Error generating auth URL: {e}")


if __name__ == "__main__":
    get_auth_url()
