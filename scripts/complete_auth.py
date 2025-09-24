#!/usr/bin/env python3
"""Complete authentication with authorization code."""

import os
import sys
import pickle
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_auth_oauthlib.flow import InstalledAppFlow

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
    """Complete authentication with authorization code."""
    if len(sys.argv) != 2:
        print("Usage: python complete_auth.py <authorization_code>")
        print("\nExample:")
        print("python complete_auth.py 4/0AanW9...")
        return 1
    
    auth_code = sys.argv[1].strip()
    credentials_path = 'config/credentials.json'
    token_path = Path('config/token.pickle')
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return 1
    
    try:
        print("🔄 Exchanging authorization code for tokens...")
        print(f"📁 Using credentials: {credentials_path}")
        print(f"🔑 Authorization code: {auth_code[:20]}...")
        
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Exchange code for tokens
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
        
        # Test the credentials
        print("\n🧪 Testing credentials...")
        from google.auth.transport.requests import Request
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print("🔄 Refreshing token...")
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
        
        print("✅ Credentials test passed!")
        print("🎉 Google Workspace MCP authentication complete!")
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())