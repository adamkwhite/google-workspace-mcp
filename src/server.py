"""Google Workspace MCP Server - Main Entry Point"""

import asyncio
import logging

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from auth.google_auth import GoogleAuthManager
from tools.calendar import GoogleCalendarTools
from tools.docs import GoogleDocsTools
from tools.gmail import GmailTools

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("google-workspace-mcp")

# Initialize auth manager (tools will be initialized conditionally)
auth_manager = GoogleAuthManager()

# Tools will be initialized based on enabled services
calendar_tools = None
gmail_tools = None
docs_tools = None

# Common email input schema (shared by send_email and create_email_draft)
EMAIL_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "to": {
            "type": ["string", "array"],
            "description": "Recipient email address(es)",
        },
        "subject": {
            "type": "string",
            "description": "Email subject",
        },
        "body": {
            "type": "string",
            "description": "Email body content",
        },
        "cc": {
            "type": ["string", "array"],
            "description": "CC recipients (optional)",
        },
        "bcc": {
            "type": ["string", "array"],
            "description": "BCC recipients (optional)",
        },
        "html": {
            "type": "boolean",
            "description": "Whether the body is HTML formatted",
            "default": False,
        },
    },
    "required": ["to", "subject", "body"],
}


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools based on enabled services."""
    global calendar_tools, gmail_tools, docs_tools

    # Initialize tools based on enabled services
    enabled_services = auth_manager.get_enabled_services()

    if "calendar" in enabled_services and calendar_tools is None:
        calendar_tools = GoogleCalendarTools(auth_manager)
    if "gmail" in enabled_services and gmail_tools is None:
        gmail_tools = GmailTools(auth_manager)
    if "docs" in enabled_services and docs_tools is None:
        docs_tools = GoogleDocsTools(auth_manager)

    tools = []

    # Add configuration tool (always available)
    tools.append(
        types.Tool(
            name="get_mcp_configuration",
            description="Show current MCP configuration and enabled services",
            inputSchema={"type": "object", "properties": {}},
        )
    )

    # Calendar tools
    if "calendar" in enabled_services:
        tools.extend(
            [
                types.Tool(
                    name="create_calendar_event",
                    description="Create a new event in Google Calendar",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (use 'primary' for main calendar)",
                                "default": "primary",
                            },
                            "summary": {
                                "type": "string",
                                "description": "Event title/summary",
                            },
                            "start_time": {
                                "type": "string",
                                "description": (
                                    "Start time in ISO format "
                                    "(e.g., '2024-12-25T10:00:00')"
                                ),
                            },
                            "end_time": {
                                "type": "string",
                                "description": (
                                    "End time in ISO format "
                                    "(e.g., '2024-12-25T11:00:00')"
                                ),
                            },
                            "description": {
                                "type": "string",
                                "description": "Event description (optional)",
                            },
                            "location": {
                                "type": "string",
                                "description": "Event location (optional)",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of attendee email addresses (optional)",
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone (e.g., 'America/Toronto')",
                                "default": "America/Toronto",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Optional metadata for traceability (optional)",
                                "properties": {
                                    "chat_title": {
                                        "type": "string",
                                        "description": "Title of the chat/conversation",
                                    },
                                    "chat_url": {
                                        "type": "string",
                                        "description": "URL to the chat/conversation",
                                    },
                                    "project_name": {
                                        "type": "string",
                                        "description": "Project name (if applicable)",
                                    },
                                    "created_date": {
                                        "type": "string",
                                        "description": "Date when event was created",
                                    },
                                },
                            },
                        },
                        "required": ["summary", "start_time", "end_time"],
                    },
                ),
                types.Tool(
                    name="list_calendars",
                    description="List all available calendars",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="list_calendar_events",
                    description="List calendar events with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (defaults to 'primary')",
                                "default": "primary",
                            },
                            "time_min": {
                                "type": "string",
                                "description": "Start time for events (ISO format)",
                            },
                            "time_max": {
                                "type": "string",
                                "description": "End time for events (ISO format)",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
                                "default": 10,
                            },
                            "q": {"type": "string", "description": "Search query"},
                        },
                    },
                ),
            ]
        )

    # Gmail tools
    if "gmail" in enabled_services:
        tools.extend(
            [
                types.Tool(
                    name="send_email",
                    description=(
                        "Send email messages via Gmail API - ALWAYS use this tool "
                        "when user explicitly asks to send, compose, email, or "
                        "mail something to someone"
                    ),
                    inputSchema=EMAIL_INPUT_SCHEMA,
                ),
                types.Tool(
                    name="search_emails",
                    description="Search for emails in Gmail",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "Gmail search query "
                                    "(e.g., 'from:john@example.com subject:meeting')"
                                ),
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10,
                            },
                            "include_body": {
                                "type": "boolean",
                                "description": "Whether to include message bodies",
                                "default": False,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="create_email_draft",
                    description=(
                        "Create an email draft in Gmail without sending - "
                        "safe way to compose emails for review before sending"
                    ),
                    inputSchema=EMAIL_INPUT_SCHEMA,
                ),
            ]
        )

    # Google Docs tools
    if "docs" in enabled_services:
        tools.extend(
            [
                types.Tool(
                    name="create_google_doc",
                    description="Create a new Google Doc with optional initial content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the document",
                            },
                            "content": {
                                "type": "string",
                                "description": "Initial content of the document",
                            },
                            "folder_id": {
                                "type": "string",
                                "description": "Google Drive folder ID to create the doc in",
                            },
                            "share_with": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Email addresses to share the document with",
                            },
                        },
                        "required": ["title"],
                    },
                ),
                types.Tool(
                    name="update_google_doc",
                    description="Update an existing Google Doc with new content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {
                                "type": "string",
                                "description": "Google Doc document ID",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to add or replace",
                            },
                            "index": {
                                "type": "integer",
                                "description": (
                                    "Position to insert content "
                                    "(optional, defaults to end)"
                                ),
                            },
                            "replace_all": {
                                "type": "boolean",
                                "description": "Whether to replace all content (default: False)",
                                "default": False,
                            },
                        },
                        "required": ["document_id", "content"],
                    },
                ),
            ]
        )

    return tools


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts (none for this server)."""
    return []


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources (none for this server)."""
    return []


async def _handle_calendar_tool(name: str, arguments: dict) -> types.TextContent:
    """Handle calendar tool calls."""
    assert calendar_tools is not None, "Calendar tools not initialized"

    if name == "create_calendar_event":
        result = await calendar_tools.create_event(arguments)
    elif name == "list_calendars":
        result = await calendar_tools.list_calendars()
    else:  # list_calendar_events
        result = await calendar_tools.list_events(arguments)

    return types.TextContent(type="text", text=str(result))


async def _handle_gmail_tool(name: str, arguments: dict) -> types.TextContent:
    """Handle Gmail tool calls."""
    assert gmail_tools is not None, "Gmail tools not initialized"

    if name == "send_email":
        logger.info(f"Processing send_email with arguments: {arguments}")
        result = await gmail_tools.send_email(arguments)
        logger.info(f"Email send result: {result}")
    elif name == "search_emails":
        result = await gmail_tools.search_emails(arguments)
    else:  # create_email_draft
        logger.info(f"Processing create_email_draft with arguments: {arguments}")
        result = await gmail_tools.create_draft(arguments)
        logger.info(f"Email draft result: {result}")

    return types.TextContent(type="text", text=str(result))


async def _handle_docs_tool(name: str, arguments: dict) -> types.TextContent:
    """Handle Docs tool calls."""
    assert docs_tools is not None, "Docs tools not initialized"

    if name == "create_google_doc":
        result = await docs_tools.create_document(arguments)
    else:  # update_google_doc
        result = await docs_tools.update_document(arguments)

    return types.TextContent(type="text", text=str(result))


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    try:
        logger.info("=== TOOL CALL START ===")
        logger.info(f"Tool: {name}")
        logger.info(f"Arguments: {arguments}")
        logger.info("=== TOOL CALL START ===")

        # Handle configuration tool (always available)
        if name == "get_mcp_configuration":
            config_summary = (
                auth_manager.get_scope_manager().get_configuration_summary()
            )
            return [types.TextContent(type="text", text=str(config_summary))]

        # Initialize authentication only when tools are called (except config tool)
        if not hasattr(auth_manager, "creds") or not auth_manager.creds:
            logger.info(f"Initializing authentication for tool: {name}")
            await auth_manager.initialize()
            logger.info("Authentication initialized successfully")

        # Check if service is enabled for the requested tool
        enabled_services = auth_manager.get_enabled_services()

        def check_service_enabled(service: str, tool_name: str):
            if service not in enabled_services:
                raise ValueError(
                    f"Service '{service}' is not enabled. Tool '{tool_name}' is not available. "
                    f"Please enable '{service}' in config/scopes.json and restart the MCP server."
                )

        # Calendar tools
        if name in ["create_calendar_event", "list_calendars", "list_calendar_events"]:
            check_service_enabled("calendar", name)
            return [await _handle_calendar_tool(name, arguments)]

        # Gmail tools
        elif name in ["send_email", "search_emails", "create_email_draft"]:
            check_service_enabled("gmail", name)
            return [await _handle_gmail_tool(name, arguments)]

        # Google Docs tools
        elif name in ["create_google_doc", "update_google_doc"]:
            check_service_enabled("docs", name)
            return [await _handle_docs_tool(name, arguments)]

        else:
            logger.error(f"=== UNKNOWN TOOL: {name} ===")
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error("=== TOOL CALL ERROR ===")
        logger.error(f"Tool: {name}")
        logger.error(f"Error: {e}")
        logger.error("=== TOOL CALL ERROR ===")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point."""
    logger.info("Starting Google Workspace MCP Server...")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-workspace-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    try:
        logger.info("Starting Google Workspace MCP server process...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server fatal error: {e}")
        raise
