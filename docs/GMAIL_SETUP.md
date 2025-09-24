# Google Workspace MCP - Gmail Account Setup

## Using with Regular Gmail Account

This MCP server works perfectly with regular Gmail accounts. Here's how to set it up:

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign in with your Gmail account
3. Create a new project (or select existing)
4. Note: You get $300 free credits, but the APIs we use are free anyway

### 2. Enable Required APIs
In your project, enable these APIs:
- Google Docs API
- Google Sheets API  
- Google Slides API
- Google Drive API

Navigate to "APIs & Services" > "Library" and search for each API to enable.

### 3. Create OAuth2 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure consent screen:
   - Choose "External" user type
   - Fill in basic app information
   - Add your Gmail address as a test user
   - You can skip most optional fields
4. For Application type, choose "Desktop app"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place in `config/` folder

### 4. Authentication Flow
When you first run the server:
1. It will open a browser window
2. Sign in with your Gmail account
3. Grant permissions to access Docs, Sheets, Slides, and Drive
4. The token will be saved locally for future use

### Free Tier Limits
With a regular Gmail account:
- **Docs API**: 300 requests per minute
- **Sheets API**: 300 requests per minute
- **Slides API**: 300 requests per minute
- **Drive API**: 1,000 requests per 100 seconds

These limits are more than sufficient for personal use.

### What You Can Do
- Create unlimited documents, sheets, and presentations
- Share with anyone (they'll need Google accounts to edit)
- Organize in Drive folders
- Use all API features

### OAuth Consent Screen Notes
- For personal use, you can leave the app in "Testing" mode
- No need to verify the app unless sharing with others
- Test users (including yourself) can use it indefinitely
