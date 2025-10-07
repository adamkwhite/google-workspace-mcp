"""Gmail tools for MCP server."""

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailTools:
    """Handles Gmail operations."""

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.service = None

    async def _get_service(self):
        """Get or create the Gmail service with refreshed credentials."""
        # Always ensure credentials are valid before API calls
        creds = await self.auth_manager.ensure_valid_credentials()

        # Only rebuild service if not cached
        # Note: Google's Credentials object is updated in-place during refresh
        if not self.service:
            self.service = build("gmail", "v1", credentials=creds)

        return self.service

    def _create_message(self, params: Dict[str, Any]) -> MIMEMultipart:
        """Create MIME message from parameters (shared by send and draft).

        Args:
            params: Dictionary containing email parameters

        Returns:
            MIME message ready to be encoded
        """
        # Create message
        message = MIMEMultipart("alternative")
        if params.get("html", False):
            message.attach(MIMEText(params["body"], "html"))
        else:
            message.attach(MIMEText(params["body"], "plain"))

        # Handle recipients
        to_addresses = (
            params["to"] if isinstance(params["to"], list) else [params["to"]]
        )
        message["to"] = ", ".join(to_addresses)
        message["subject"] = params["subject"]

        if "cc" in params:
            cc_addresses = (
                params["cc"] if isinstance(params["cc"], list) else [params["cc"]]
            )
            message["cc"] = ", ".join(cc_addresses)

        if "bcc" in params:
            bcc_addresses = (
                params["bcc"] if isinstance(params["bcc"], list) else [params["bcc"]]
            )
            message["bcc"] = ", ".join(bcc_addresses)

        return message

    async def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email.

        Args:
            params: Dictionary containing:
                - to: Recipient email address(es) - string or list
                - subject: Email subject (required)
                - body: Email body (required)
                - cc: CC recipients (optional) - string or list
                - bcc: BCC recipients (optional) - string or list
                - html: Whether body is HTML (default: False)

        Returns:
            Dictionary with sent message information
        """
        try:
            # Create message using shared method
            message = self._create_message(params)

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # Send the message
            service = await self._get_service()
            sent_message = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            logger.info(
                f"Successfully sent email to {message['to']} with subject: {params['subject']}"
            )

            return {
                "id": sent_message.get("id"),
                "threadId": sent_message.get("threadId"),
                "labelIds": sent_message.get("labelIds", []),
                "to": message["to"],
                "subject": params["subject"],
            }

        except HttpError as e:
            logger.error(f"Error sending email: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise

    async def search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for emails.

        Args:
            params: Dictionary containing:
                - query: Gmail search query (required)
                - max_results: Maximum number of results (default: 10)
                - include_body: Whether to include message bodies (default: False)

        Returns:
            Dictionary with search results
        """
        try:
            query = params["query"]
            max_results = params.get("max_results", 10)
            include_body = params.get("include_body", False)

            service = await self._get_service()

            # Search for messages
            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])

            # Get detailed information for each message
            detailed_messages = []
            for msg in messages:
                try:
                    # Get message details
                    message = (
                        service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=msg["id"],
                            format="full" if include_body else "metadata",
                        )
                        .execute()
                    )

                    # Extract key information
                    headers = {
                        h["name"]: h["value"]
                        for h in message["payload"].get("headers", [])
                    }

                    msg_info = {
                        "id": message["id"],
                        "threadId": message["threadId"],
                        "subject": headers.get("Subject", "No subject"),
                        "from": headers.get("From", ""),
                        "to": headers.get("To", ""),
                        "date": headers.get("Date", ""),
                        "snippet": message.get("snippet", ""),
                        "labelIds": message.get("labelIds", []),
                    }

                    # Include body if requested
                    if include_body:
                        body = self._extract_body(message["payload"])
                        msg_info["body"] = body

                    detailed_messages.append(msg_info)

                except Exception as e:
                    logger.warning(f"Error retrieving message {msg['id']}: {e}")

            logger.info(
                f"Found {len(detailed_messages)} messages matching query: {query}"
            )

            return {
                "messages": detailed_messages,
                "count": len(detailed_messages),
                "query": query,
            }

        except HttpError as e:
            logger.error(f"Error searching emails: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching emails: {e}")
            raise

    async def create_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an email draft.

        Args:
            params: Same as send_email

        Returns:
            Dictionary with draft information
        """
        try:
            # Create message using shared method
            message = self._create_message(params)

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # Create draft
            service = await self._get_service()
            draft = (
                service.users()
                .drafts()
                .create(userId="me", body={"message": {"raw": raw_message}})
                .execute()
            )

            logger.info(f"Successfully created draft with subject: {params['subject']}")

            return {
                "id": draft.get("id"),
                "message": {
                    "id": draft["message"].get("id"),
                    "threadId": draft["message"].get("threadId"),
                    "labelIds": draft["message"].get("labelIds", []),
                },
                "to": message["to"],
                "subject": params["subject"],
            }

        except HttpError as e:
            logger.error(f"Error creating draft: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating draft: {e}")
            raise

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract body from email payload."""
        body = ""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"]["data"]
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
                elif part["mimeType"] == "text/html" and not body:
                    data = part["body"]["data"]
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            if payload["body"].get("data"):
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

        return body
