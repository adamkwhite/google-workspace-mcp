"""Authentication module for Google Workspace APIs."""

import asyncio
import logging
import os
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from utils.scope_manager import ScopeManager

logger = logging.getLogger(__name__)


class GoogleAuthManager:
    """Manages authentication for Google Workspace APIs."""

    # Token refresh buffer: refresh tokens 10 minutes before expiration
    TOKEN_REFRESH_BUFFER = 600  # seconds

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CREDENTIALS_PATH", "config/credentials.json"
        )
        self.token_path = Path("config/token.pickle")
        self.creds: Optional[Credentials] = None

        # Async lock for token refresh concurrency control
        self.refresh_lock = asyncio.Lock()

        # Initialize scope manager
        self.scope_manager = ScopeManager()

        # Security: Restrict file creation to specific folders
        self.allowed_folder_ids = (
            os.getenv("GOOGLE_ALLOWED_FOLDERS", "").split(",")
            if os.getenv("GOOGLE_ALLOWED_FOLDERS")
            else []
        )
        self.default_folder_id = os.getenv(
            "GOOGLE_DEFAULT_FOLDER"
        )  # Optional: default folder for new files

    async def initialize(self):
        """Initialize authentication."""
        # Validate scope configuration first
        is_valid, errors = self.scope_manager.validate_configuration()
        if not is_valid:
            error_msg = f"Invalid scope configuration: {', '.join(errors)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        required_scopes = self.scope_manager.get_required_scopes()
        logger.info(f"Required scopes: {required_scopes}")

        # Check if we need to re-authenticate due to scope changes
        needs_reauth = False
        if os.path.exists(self.token_path):
            logger.info("Loading existing credentials...")
            with open(self.token_path, "rb") as token:
                self.creds = pickle.load(token)

            # Check if scopes have changed
            if hasattr(self.creds, "scopes") and self.creds.scopes:
                current_scopes = list(self.creds.scopes)
                needs_reauth = self.scope_manager.has_scope_changes(current_scopes)

                if needs_reauth:
                    logger.info("Scope changes detected, re-authentication required")
                    self.creds = None  # Force re-authentication

        if not self.creds or not self.creds.valid or needs_reauth:
            if (
                self.creds
                and self.creds.expired
                and self.creds.refresh_token
                and not needs_reauth
            ):
                logger.info("Refreshing expired credentials...")
                await self.refresh_token()
            else:
                logger.info("Initiating new authentication flow...")
                await self._authenticate()
                self.save_credentials()

        logger.info("Authentication successful!")

    async def _authenticate(self):
        """Perform OAuth2 authentication flow."""
        required_scopes = self.scope_manager.get_required_scopes()

        if os.path.exists(self.credentials_path):
            # Check if it's a service account key
            if self._is_service_account():
                logger.info("Detected service account credentials")
                self.creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path, scopes=required_scopes
                )
            else:
                # OAuth2 flow for regular Gmail accounts
                enabled_services = self.scope_manager.get_enabled_services()
                logger.info(
                    f"Starting OAuth2 flow for services: {list(enabled_services)}"
                )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, required_scopes
                )
                # This will open a browser for authentication
                self.creds = flow.run_local_server(port=0)
                logger.info("OAuth2 authentication completed!")
        else:
            raise FileNotFoundError(
                f"Credentials file not found at {self.credentials_path}.\n"
                "Please download OAuth2 credentials from Google Cloud Console:\n"
                "1. Go to APIs & Services > Credentials\n"
                "2. Create OAuth client ID (Desktop application)\n"
                "3. Download and save as config/credentials.json"
            )

    def _is_service_account(self) -> bool:
        """Check if the credentials file is a service account key."""
        import json

        try:
            if not self.credentials_path:
                return False
            with open(self.credentials_path, "r") as f:
                data = json.load(f)
                return data.get("type") == "service_account"
        except Exception:
            return False

    def get_credentials(self) -> Credentials:
        """Get the current credentials."""
        if not self.creds:
            raise RuntimeError("Authentication not initialized")
        return self.creds

    def get_scope_manager(self) -> ScopeManager:
        """Get the scope manager."""
        return self.scope_manager

    def get_enabled_services(self) -> List[str]:
        """Get list of enabled services."""
        return list(self.scope_manager.get_enabled_services())

    def should_refresh_token(self) -> bool:
        """
        Check if token should be refreshed proactively.

        Returns True if the token will expire within TOKEN_REFRESH_BUFFER seconds.
        """
        if not self.creds or not self.creds.expiry:
            return False

        time_until_expiry = (
            self.creds.expiry - datetime.now(timezone.utc)
        ).total_seconds()
        return time_until_expiry <= self.TOKEN_REFRESH_BUFFER

    async def refresh_token(self):
        """
        Refresh the OAuth2 access token.

        Raises:
            RefreshError: If the token refresh fails and re-authentication is needed.
        """
        try:
            logger.info("Refreshing OAuth2 token...")
            self.creds.refresh(Request())
            self.save_credentials()
            logger.info("Token refreshed successfully")
        except RefreshError as e:
            logger.error(f"Token refresh failed: {e}")
            logger.info("Re-authentication required - refresh token may be revoked")
            # Trigger re-authentication flow
            await self._authenticate()
            self.save_credentials()

    def save_credentials(self):
        """Save credentials to disk with proper metadata."""
        if not self.creds:
            return

        self.token_path.parent.mkdir(exist_ok=True)
        with open(self.token_path, "wb") as token:
            pickle.dump(self.creds, token)
        logger.debug(f"Credentials saved to {self.token_path}")

    async def ensure_valid_credentials(self) -> Credentials:
        """
        Ensure credentials are valid, refreshing if necessary.

        This method combines proactive and reactive token refresh:
        - Proactively refreshes tokens within TOKEN_REFRESH_BUFFER of expiration
        - Reactively refreshes if token is invalid/expired

        Async-safe: Uses asyncio.Lock to prevent concurrent refresh attempts.

        Returns:
            Credentials: Valid, refreshed credentials.
        """
        async with self.refresh_lock:
            # Proactive refresh: refresh before expiration
            if self.should_refresh_token():
                logger.debug("Proactive token refresh triggered")
                await self.refresh_token()
            # Reactive refresh: token is already invalid
            elif not self.creds or not self.creds.valid:
                logger.debug("Reactive token refresh triggered")
                await self.refresh_token()

        return self.creds
