#!/usr/bin/env python3
"""Test script to verify Google Workspace MCP functionality."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auth.google_auth import GoogleAuthManager
from tools.calendar import GoogleCalendarTools
from tools.docs import GoogleDocsTools
from tools.gmail import GmailTools


async def test_authentication():
    """Test authentication setup."""
    print("Testing Authentication...")
    auth_manager = GoogleAuthManager()
    try:
        await auth_manager.initialize()
        print("✓ Authentication successful")
        return auth_manager
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return None


async def test_calendar(auth_manager):
    """Test calendar functionality."""
    print("\nTesting Calendar Tools...")
    calendar_tools = GoogleCalendarTools(auth_manager)

    try:
        # List calendars
        result = await calendar_tools.list_calendars({})
        print(f"✓ Found {result['count']} calendars")
        for cal in result["calendars"][:3]:  # Show first 3
            print(f"  - {cal['summary']} (ID: {cal['id']})")
    except Exception as e:
        print(f"✗ Calendar test failed: {e}")


async def test_gmail(auth_manager):
    """Test Gmail functionality."""
    print("\nTesting Gmail Tools...")
    gmail_tools = GmailTools(auth_manager)

    try:
        # Search for recent emails
        result = await gmail_tools.search_emails({"query": "is:sent", "max_results": 3})
        print(f"✓ Found {result['count']} sent emails")
        for msg in result["messages"]:
            print(f"  - {msg['subject']} (to: {msg['to']})")
    except Exception as e:
        print(f"✗ Gmail test failed: {e}")


async def test_docs(auth_manager):
    """Test Google Docs functionality."""
    print("\nTesting Google Docs Tools...")
    _ = GoogleDocsTools(auth_manager)  # noqa: F841

    try:
        # Note: This would actually create a document
        print("✓ Google Docs tools initialized")
        print("  (Skipping actual document creation in test)")
    except Exception as e:
        print(f"✗ Docs test failed: {e}")


async def main():
    """Run all tests."""
    print("Google Workspace MCP Test Suite")
    print("==============================")

    # Test authentication
    auth_manager = await test_authentication()
    if not auth_manager:
        print("\nAuthentication failed. Please run setup.sh first.")
        return

    # Test each service
    await test_calendar(auth_manager)
    await test_gmail(auth_manager)
    await test_docs(auth_manager)

    print("\n✓ All tests completed!")
    print("\nNext steps:")
    print("1. Configure Claude Desktop with the MCP server")
    print("2. Restart Claude Desktop")
    print("3. Try commands like:")
    print('   - "List my calendars"')
    print('   - "Search for emails from this week"')
    print('   - "Create a test document"')


if __name__ == "__main__":
    asyncio.run(main())
