#!/bin/bash

# Google Workspace MCP Setup Script

echo "Google Workspace MCP Setup"
echo "==========================="
echo ""
echo "Unified MCP for Calendar, Gmail, Docs, Sheets, and Slides!"
echo "Works with regular Gmail accounts - no subscription required."
echo ""

# Check if running in WSL
if grep -q Microsoft /proc/version; then
    echo "✓ Running in WSL environment"
else
    echo "⚠ Not running in WSL - some paths may need adjustment"
fi

echo ""
echo "Prerequisites:"
echo "1. Google Cloud Project created (free with Gmail account)"
echo "2. APIs enabled: Calendar, Gmail, Docs, Sheets, Slides, Drive"
echo "3. OAuth2 credentials downloaded (Desktop app type)"
echo ""
echo "Note: Service accounts require Google Workspace, but OAuth2 works with Gmail!"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup Google Cloud authentication
echo ""
echo "Google Cloud Authentication Setup"
echo "================================"
echo ""
echo "Please choose authentication method:"
echo "1. OAuth2 (for personal use)"
echo "2. Service Account (for automation)"
echo ""
read -p "Enter your choice (1 or 2): " auth_choice

case $auth_choice in
    1)
        echo ""
        echo "OAuth2 Setup Instructions:"
        echo "1. Go to Google Cloud Console"
        echo "2. Navigate to APIs & Services > Credentials"
        echo "3. Create OAuth2 Client ID (Desktop application)"
        echo "4. Download credentials.json"
        echo "5. Place it in config/credentials.json"
        ;;
    2)
        echo ""
        echo "Service Account Setup Instructions:"
        echo "1. Go to Google Cloud Console"
        echo "2. Navigate to IAM & Admin > Service Accounts"
        echo "3. Create new service account"
        echo "4. Create and download JSON key"
        echo "5. Place it in config/credentials.json"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
read -p "Press Enter when credentials.json is in place..."

# Verify credentials file
if [ -f "config/credentials.json" ]; then
    echo "✓ Credentials file found"
else
    echo "✗ Credentials file not found at config/credentials.json"
    echo "Please place your credentials file and run this script again"
    exit 1
fi

# Create .env file
echo ""
echo "Creating .env file..."
cat > .env << EOF
GOOGLE_CREDENTIALS_PATH=config/credentials.json
LOG_LEVEL=INFO
EOF

echo "✓ .env file created"

# MCP Configuration
echo ""
echo "MCP Configuration for Claude Desktop"
echo "==================================="
echo ""
echo "Add the following to your Claude Desktop config:"
echo "(Usually at ~/AppData/Roaming/Claude/claude_desktop_config.json on Windows)"
echo ""
cat << EOF
{
  "mcpServers": {
    "google-workspace": {
      "command": "python",
      "args": [
        "/home/adam/Code/google-workspace-mcp/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/adam/Code/google-workspace-mcp/src"
      }
    }
  }
}
EOF

echo ""
echo "Setup complete! Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the server: python src/server.py"
echo "3. Configure Claude Desktop with the above settings"
echo "4. Restart Claude Desktop"

# Make scripts executable
chmod +x setup.sh
chmod +x scripts/test_integration.py
