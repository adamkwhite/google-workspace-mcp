"""Authentication module for Google Workspace APIs."""

import asyncio
import logging
import os
import pickle
import webbrowser
from pathlib import Path
from typing import List, Optional

import aiofiles
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from utils.scope_manager import ScopeManager

logger = logging.getLogger(__name__)


class GoogleAuthManager:
    """Manages authentication for Google Workspace APIs."""

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CREDENTIALS_PATH", "config/credentials.json"
        )
        self.token_path = Path("config/token.pickle")
        self.creds: Optional[Credentials] = None

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
        self._validate_scope_configuration()

        required_scopes = self.scope_manager.get_required_scopes()
        logger.info(f"Required scopes: {required_scopes}")

        needs_reauth = await self._load_existing_credentials()

        if not self.creds or not self.creds.valid or needs_reauth:
            self._resolve_credentials(needs_reauth)
            await self._save_and_deploy_credentials()

        logger.info("Authentication successful!")

    def _validate_scope_configuration(self):
        """Validate scope configuration, raising on errors."""
        is_valid, errors = self.scope_manager.validate_configuration()
        if not is_valid:
            error_msg = f"Invalid scope configuration: {', '.join(errors)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def _load_existing_credentials(self) -> bool:
        """Load cached credentials and check for scope changes. Returns needs_reauth."""
        if not os.path.exists(self.token_path):
            return False

        logger.info("Loading existing credentials...")
        async with aiofiles.open(self.token_path, "rb") as token:
            content = await token.read()
            # nosec B301 - Loading OAuth token from local file created by this application
            # This is not deserializing untrusted external data
            self.creds = pickle.loads(content)  # nosec B301

        if not (hasattr(self.creds, "scopes") and self.creds.scopes):
            return False

        current_scopes = list(self.creds.scopes)
        needs_reauth = self.scope_manager.has_scope_changes(current_scopes)
        if needs_reauth:
            logger.info("Scope changes detected, re-authentication required")
            self.creds = None
        return needs_reauth

    def _resolve_credentials(self, needs_reauth: bool):
        """Refresh existing credentials or run a new authentication flow."""
        if (
            self.creds
            and self.creds.expired
            and self.creds.refresh_token
            and not needs_reauth
        ):
            logger.info("Refreshing expired credentials...")
            self.creds.refresh(Request())
        else:
            logger.info("Initiating new authentication flow...")
            self._authenticate()

    async def _save_and_deploy_credentials(self):
        """Save credentials to disk and deploy to remote hosts."""
        self.token_path.parent.mkdir(exist_ok=True)
        async with aiofiles.open(self.token_path, "wb") as token:
            await token.write(pickle.dumps(self.creds))

        deploy_script = (
            Path(__file__).resolve().parents[2] / "scripts" / "deploy_token.sh"
        )
        if deploy_script.exists():
            logger.info("Deploying token to remote hosts...")
            await asyncio.create_subprocess_exec(str(deploy_script))

    def _authenticate(self):
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

                # Use Microsoft Edge on Windows (from WSL)
                edge_path = (
                    "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
                )
                if os.path.exists(edge_path):
                    # Register Edge as the browser for OAuth
                    webbrowser.register(
                        "edge",
                        None,
                        webbrowser.BackgroundBrowser(edge_path),
                        preferred=True,
                    )
                    logger.info("Using Microsoft Edge for authentication")

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
