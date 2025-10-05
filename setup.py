#!/usr/bin/env python3
"""
Setup script for Google Calendar MCP Server
Handles initial configuration and testing
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.11+ is being used for MCP compatibility"""
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher is required for MCP server")
        print("Install with: sudo apt update && sudo apt install python3.11 python3.11-pip")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call(["python3.11", "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)

def check_credentials():
    """Check if credentials.json exists"""
    creds_path = Path("credentials.json")
    if not creds_path.exists():
        print("⚠ credentials.json not found")
        print("Download OAuth credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Navigate to APIs & Services > Credentials")
        print("4. Create OAuth 2.0 Client ID (Desktop application)")
        print("5. Download and save as 'credentials.json' in this directory")
        return False
    
    print("✓ credentials.json found")
    return True

def test_mcp_server():
    """Test if MCP server starts correctly"""
    print("Testing MCP server startup...")
    try:
        # Quick import test
        sys.path.insert(0, str(Path("src")))
        import server
        print("✓ MCP server imports successfully")
        return True
    except ImportError as e:
        print(f"Error: Failed to import server module: {e}")
        return False

def generate_claude_config():
    """Generate Claude MCP configuration for WSL"""
    # Use WSL path format for Claude configuration
    wsl_path = "/home/adam/Code/calendar-mcp/src/server.py"
    
    config = {
        "mcpServers": {
            "google-calendar": {
                "command": "python3.11",
                "args": [wsl_path],
                "cwd": "/home/adam/Code/calendar-mcp"
            }
        }
    }
    
    config_path = Path("claude-mcp-config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Claude configuration saved to {config_path}")
    print("Add this configuration to your Claude MCP settings")

def main():
    """Main setup routine"""
    print("Google Calendar MCP Server Setup (WSL)")
    print("=" * 40)
    
    check_python_version()
    install_dependencies()
    
    if not check_credentials():
        print("\nSetup incomplete. Please copy credentials.json to this directory and run setup again.")
        print("Remember to copy from Windows: cp /mnt/c/Code/calendar-mcp/credentials.json .")
        sys.exit(1)
    
    if test_mcp_server():
        generate_claude_config()
        print("\n✓ Setup complete!")
        print("\nNext steps:")
        print("1. Add claude-mcp-config.json to your Claude MCP configuration")
        print("2. Restart Claude")
        print("3. Test by asking Claude to create a calendar event")
    else:
        print("\nSetup incomplete. Please check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
