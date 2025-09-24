#!/usr/bin/env python3
"""Manual authentication script for Google Workspace MCP - No browser version."""

import os
import sys
import pickle
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send', 
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets', 
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive.file',
]

def main():
    """Manually authenticate with Google APIs without browser."""
    credentials_path = 'config/credentials.json'
    token_path = Path('config/token.pickle')
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return 1
    
    try:
        print("🔄 Starting manual OAuth2 authentication...")
        print("📋 Required scopes:")
        for i, scope in enumerate(SCOPES, 1):
            print(f"  {i}. {scope}")
        
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        
        # Get authorization URL with manual redirect URI
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Out-of-band flow
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )
        
        print(f"\n🌐 Please visit this URL in your browser:")
        print(f"\n{auth_url}\n")
        print("📋 Steps:")
        print("1. Copy the URL above")
        print("2. Open it in your browser")
        print("3. Sign in to your Google account")
        print("4. Grant permissions to all requested scopes")
        print("5. Copy the authorization code from the success page")
        print("6. Paste it below")
        
        # Get authorization code from user
        auth_code = input("\n🔑 Enter authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return 1
            
        print("🔄 Exchanging authorization code for tokens...")
        flow.fetch_token(code=auth_code)
        
        creds = flow.credentials
        
        # Save credentials
        token_path.parent.mkdir(exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
        print(f"✅ Authentication successful!")
        print(f"💾 Token saved to: {token_path}")
        print(f"🔑 Token valid: {creds.valid}")
        
        if hasattr(creds, 'refresh_token') and creds.refresh_token:
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