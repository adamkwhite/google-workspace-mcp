"""Google Docs tools for MCP server."""

import logging
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDocsTools:
    """Handles Google Docs operations."""

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.docs_service = None
        self.drive_service = None

    def _get_docs_service(self):
        """Get or create the Google Docs service."""
        if not self.docs_service:
            creds = self.auth_manager.get_credentials()
            self.docs_service = build("docs", "v1", credentials=creds)
        return self.docs_service

    def _get_drive_service(self):
        """Get or create the Google Drive service."""
        if not self.drive_service:
            creds = self.auth_manager.get_credentials()
            self.drive_service = build("drive", "v3", credentials=creds)
        return self.drive_service

    async def create_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Google Doc.

        Args:
            params: Dictionary containing:
                - title: Document title (required)
                - content: Initial content (optional)
                - folder_id: Google Drive folder ID (optional)
                - share_with: List of email addresses to share with (optional)

        Returns:
            Dictionary with document information
        """
        try:
            title = params["title"]
            content = params.get("content", "")
            folder_id = params.get("folder_id")
            share_with = params.get("share_with", [])

            docs_service = self._get_docs_service()
            drive_service = self._get_drive_service()

            # Create the document
            document = docs_service.documents().create(body={"title": title}).execute()

            document_id = document["documentId"]
            logger.info(f"Created document with ID: {document_id}")

            # Add content if provided
            if content:
                requests = [{"insertText": {"location": {"index": 1}, "text": content}}]

                docs_service.documents().batchUpdate(
                    documentId=document_id, body={"requests": requests}
                ).execute()

                logger.info(f"Added content to document: {title}")

            # Move to folder if specified
            if folder_id:
                try:
                    # Get current parents
                    file = (
                        drive_service.files()
                        .get(fileId=document_id, fields="parents")
                        .execute()
                    )
                    previous_parents = ",".join(file.get("parents"))

                    # Move to new folder
                    drive_service.files().update(
                        fileId=document_id,
                        addParents=folder_id,
                        removeParents=previous_parents,
                        fields="id, parents",
                    ).execute()

                    logger.info(f"Moved document to folder: {folder_id}")
                except HttpError as e:
                    logger.warning(
                        f"Could not move document to folder {folder_id}: {e}"
                    )

            # Share with users if specified
            if share_with:
                for email in share_with:
                    try:
                        drive_service.permissions().create(
                            fileId=document_id,
                            body={
                                "type": "user",
                                "role": "writer",
                                "emailAddress": email,
                            },
                        ).execute()
                        logger.info(f"Shared document with: {email}")
                    except HttpError as e:
                        logger.warning(f"Could not share with {email}: {e}")

            # Get the document URL
            doc_url = f"https://docs.google.com/document/d/{document_id}/edit"

            return {
                "documentId": document_id,
                "title": title,
                "url": doc_url,
                "revisionId": document.get("revisionId"),
                "shared_with": share_with,
                "folder_id": folder_id,
            }

        except HttpError as e:
            logger.error(f"Error creating document: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating document: {e}")
            raise

    async def update_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Google Doc.

        Args:
            params: Dictionary containing:
                - document_id: Document ID (required)
                - content: Content to append or insert (required)
                - index: Position to insert content (optional, defaults to end)
                - replace_all: Whether to replace all content (optional, default False)

        Returns:
            Dictionary with update information
        """
        try:
            document_id = params["document_id"]
            content = params["content"]
            index = params.get("index")
            replace_all = params.get("replace_all", False)

            docs_service = self._get_docs_service()

            # Get document to determine insert position
            document = docs_service.documents().get(documentId=document_id).execute()

            if replace_all:
                # Replace all content
                requests = [
                    {
                        "deleteContentRange": {
                            "range": {
                                "startIndex": 1,
                                "endIndex": len(
                                    document["body"]["content"][0]["paragraph"][
                                        "elements"
                                    ][0]["textRun"]["content"]
                                ),
                            }
                        }
                    },
                    {"insertText": {"location": {"index": 1}, "text": content}},
                ]
            else:
                # Insert or append content
                if index is None:
                    # Append to end (before the last newline)
                    index = (
                        len(
                            document["body"]["content"][0]["paragraph"]["elements"][0][
                                "textRun"
                            ]["content"]
                        )
                        - 1
                    )

                requests = [
                    {"insertText": {"location": {"index": index}, "text": content}}
                ]

            result = (
                docs_service.documents()
                .batchUpdate(documentId=document_id, body={"requests": requests})
                .execute()
            )

            logger.info(f"Updated document: {document_id}")

            return {
                "documentId": document_id,
                "replies": result.get("replies", []),
                "writeControl": result.get("writeControl", {}),
            }

        except HttpError as e:
            logger.error(f"Error updating document: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating document: {e}")
            raise
