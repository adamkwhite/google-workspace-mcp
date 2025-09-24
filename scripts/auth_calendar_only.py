#!/usr/bin/env python3
"""Generate OAuth URL for Calendar, Docs, and Drive only."""

import os
import sys
import pickle
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_auth_oauthlib.flow import InstalledAppFlow

# Only the scopes you want
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/documents', 
    'https://www.googleapis.com/auth/drive.file',
]

def generate_url():
    """Generate fresh OAuth URL for limited scopes."""
    credentials_path = 'config/credentials.json'
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return None
    
    try:
        print("🔄 Generating fresh OAuth URL...")
        print("📋 Requested scopes:")
        for i, scope in enumerate(SCOPES, 1):
            print(f"  {i}. {scope}")
        
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )
        
        print(f"\n🌐 Visit this URL in your browser:")
        print(f"\n{auth_url}\n")
        
        return flow
        
    except Exception as e:
        print(f"❌ Failed to generate URL: {e}")
        return None

def complete_auth(flow, auth_code):
    """Complete authentication with authorization code."""
    token_path = Path('config/token.pickle')
    
    try:
        print("🔄 Exchanging authorization code for tokens...")
        
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
        
        print("\n✅ Available services:")
        print("  📅 Google Calendar")  
        print("  📄 Google Docs")
        print("  📁 Google Drive")
        
        return True
        
    except Exception as e:
        print(f"❌ Token exchange failed: {e}")
        return False

def main():
    """Main authentication flow."""
    if len(sys.argv) == 1:
        # Generate URL
        flow = generate_url()
        if flow:
            print("📋 Steps:")
            print("1. Copy the URL above")
            print("2. Open it in your browser") 
            print("3. Grant permissions")
            print("4. Copy the authorization code")
            print("5. Run: python auth_calendar_only.py <code>")
    elif len(sys.argv) == 2:
        # Complete with auth code
        auth_code = sys.argv[1].strip()
        flow = generate_url()  # Need to recreate flow
        if flow:
            success = complete_auth(flow, auth_code)
            return 0 if success else 1
    else:
        print("Usage:")
        print("  python auth_calendar_only.py              # Generate OAuth URL")
        print("  python auth_calendar_only.py <code>       # Complete with auth code")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())