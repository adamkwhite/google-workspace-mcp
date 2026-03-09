"""Gmail tools for MCP server."""

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailTools:
    """Handles Gmail operations."""

    def __init__(self, auth_manager, scope_manager=None):
        self.auth_manager = auth_manager
        self.scope_manager = scope_manager
        self.service = None
        self._label_cache: Optional[Dict[str, str]] = None
        self._restricted_label_id: Optional[str] = None
        self._label_initialized = False

    def _get_service(self):
        """Get or create the Gmail service."""
        if not self.service:
            creds = self.auth_manager.get_credentials()
            self.service = build("gmail", "v1", credentials=creds)
        return self.service

    def _initialize_labels(self):
        """Initialize label cache and resolve restricted label ID.

        Raises:
            ValueError: If configured label doesn't exist in Gmail
            HttpError: If Gmail API call fails
        """
        if self._label_initialized:
            return

        # Check if label restriction is configured
        if not self.scope_manager:
            self._label_initialized = True
            return

        restricted_label_name = self.scope_manager.get_restricted_label()
        if not restricted_label_name:
            self._label_initialized = True
            return

        try:
            service = self._get_service()
            response = service.users().labels().list(userId="me").execute()
            labels = response.get("labels", [])

            # Build cache: label name -> label ID
            self._label_cache = {label["name"]: label["id"] for label in labels}

            # Resolve restricted label
            if restricted_label_name not in self._label_cache:
                available_labels = sorted(self._label_cache.keys())
                raise ValueError(
                    f"Configured Gmail label '{restricted_label_name}' not found. "
                    f"Available labels: {', '.join(available_labels)}"
                )

            self._restricted_label_id = self._label_cache[restricted_label_name]
            self._label_initialized = True

            logger.info(
                "Gmail label filtering initialized: "
                f"'{restricted_label_name}' -> {self._restricted_label_id}"
            )

        except HttpError as e:
            logger.error(f"Failed to fetch Gmail labels: {e}")
            raise

    def _enhance_search_query(self, query: str) -> str:
        """Enhance search query with label filter if restriction is enabled.

        Args:
            query: Original search query

        Returns:
            Enhanced query with label filter appended
        """
        if not self._restricted_label_id:
            return query

        label_filter = f"label:{self.scope_manager.get_restricted_label()}"

        if not query or not query.strip():
            return label_filter

        return f"{query} {label_filter}"

    def _check_restriction_allows_operation(self, operation: str):
        """Check if label restriction blocks the requested operation.

        Args:
            operation: Operation name (e.g., "send_email", "create_draft")

        Raises:
            ValueError: If operation is blocked by label restriction
        """
        if not self._restricted_label_id:
            return

        restricted_label_name = self.scope_manager.get_restricted_label()
        raise ValueError(
            f"Cannot {operation.replace('_', ' ')} when Gmail is restricted "
            f"to label '{restricted_label_name}'. "
            "Only search_emails is allowed with label filtering enabled."
        )

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

    def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
            # Initialize labels and check restrictions
            self._initialize_labels()
            self._check_restriction_allows_operation("send_email")

            # Create message using shared method
            message = self._create_message(params)

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # Send the message
            service = self._get_service()
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

    def search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
            # Initialize labels and enhance query with label filter
            self._initialize_labels()
            query = self._enhance_search_query(params["query"])

            max_results = params.get("max_results", 10)
            include_body = params.get("include_body", False)

            service = self._get_service()

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

    def create_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an email draft.

        Args:
            params: Same as send_email

        Returns:
            Dictionary with draft information
        """
        try:
            # Initialize labels and check restrictions
            self._initialize_labels()
            self._check_restriction_allows_operation("create_draft")

            # Create message using shared method
            message = self._create_message(params)

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # Create draft
            service = self._get_service()
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
