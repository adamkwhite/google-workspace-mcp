#!/usr/bin/env python3
"""Helper script to create a folder and get its ID."""

import asyncio
import sys
from src.auth.google_auth import GoogleAuthManager
from googleapiclient.discovery import build

async def create_mcp_folder():
    """Create a dedicated folder for MCP documents."""
    
    # Initialize auth
    auth_manager = GoogleAuthManager()
    await auth_manager.initialize()
    
    # Get Drive service
    drive_service = build('drive', 'v3', credentials=auth_manager.get_credentials())
    
    # Create folder
    folder_metadata = {
        'name': 'Claude MCP Documents',
        'mimeType': 'application/vnd.google-apps.folder',
        'description': 'Documents created by Claude MCP integration'
    }
    
    try:
        folder = drive_service.files().create(body=folder_metadata).execute()
        folder_id = folder.get('id')
        
        print(f"✓ Created folder: 'Claude MCP Documents'")
        print(f"✓ Folder ID: {folder_id}")
        print(f"✓ Folder URL: https://drive.google.com/drive/folders/{folder_id}")
        print()
        print("Add this to your .env file:")
        print(f"GOOGLE_DEFAULT_FOLDER={folder_id}")
        print(f"GOOGLE_ALLOWED_FOLDERS={folder_id}")
        
        return folder_id
        
    except Exception as e:
        print(f"Error creating folder: {e}")
        return None

if __name__ == "__main__":
    folder_id = asyncio.run(create_mcp_folder())