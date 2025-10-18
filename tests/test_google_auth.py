"""Tests for Google authentication."""

import json
import os
import pickle
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from auth.google_auth import GoogleAuthManager


class TestGoogleAuthManager:
    """Test cases for GoogleAuthManager."""

    def test_init_with_default_credentials_path(self):
        """Test initialization with default credentials path."""
        manager = GoogleAuthManager()
        assert manager.credentials_path == "config/credentials.json"
        assert manager.token_path == Path("config/token.pickle")

    def test_init_with_custom_credentials_path(self):
        """Test initialization with custom credentials path."""
        custom_path = "custom/creds.json"
        manager = GoogleAuthManager(credentials_path=custom_path)
        assert manager.credentials_path == custom_path

    @patch.dict(os.environ, {"GOOGLE_CREDENTIALS_PATH": "env/creds.json"})
    def test_init_with_env_credentials_path(self):
        """Test initialization with environment variable."""
        manager = GoogleAuthManager()
        assert manager.credentials_path == "env/creds.json"

    def test_is_service_account_returns_false_when_no_file(self):
        """Test _is_service_account when credentials file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "nonexistent.json")
            manager = GoogleAuthManager(credentials_path=creds_path)

            result = manager._is_service_account()
            assert result is False

    def test_is_service_account_returns_true_for_service_account(self):
        """Test _is_service_account with service account credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "service_account.json")
            creds_data = {
                "type": "service_account",
                "project_id": "test-project",
            }

            with open(creds_path, "w") as f:
                json.dump(creds_data, f)

            manager = GoogleAuthManager(credentials_path=creds_path)
            result = manager._is_service_account()

            assert result is True

    def test_is_service_account_returns_false_for_oauth(self):
        """Test _is_service_account with OAuth credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "oauth.json")
            creds_data = {
                "installed": {
                    "client_id": "test-client-id",
                    "project_id": "test-project",
                }
            }

            with open(creds_path, "w") as f:
                json.dump(creds_data, f)

            manager = GoogleAuthManager(credentials_path=creds_path)
            result = manager._is_service_account()

            assert result is False

    def test_get_credentials_raises_when_not_initialized(self):
        """Test get_credentials raises error when not initialized."""
        manager = GoogleAuthManager()

        with pytest.raises(RuntimeError, match="Authentication not initialized"):
            manager.get_credentials()

    def test_get_credentials_returns_creds_when_initialized(self):
        """Test get_credentials returns credentials when initialized."""
        manager = GoogleAuthManager()
        mock_creds = Mock()
        manager.creds = mock_creds

        result = manager.get_credentials()

        assert result == mock_creds

    @patch("auth.google_auth.ScopeManager")
    def test_get_scope_manager(self, mock_scope_manager_class):
        """Test get_scope_manager returns the scope manager."""
        mock_instance = Mock()
        mock_scope_manager_class.return_value = mock_instance

        manager = GoogleAuthManager()
        result = manager.get_scope_manager()

        assert result == manager.scope_manager

    @patch("auth.google_auth.ScopeManager")
    def test_get_enabled_services(self, mock_scope_manager_class):
        """Test get_enabled_services delegates to scope manager."""
        mock_scope_manager = Mock()
        mock_scope_manager.get_enabled_services.return_value = ["calendar", "gmail"]
        mock_scope_manager_class.return_value = mock_scope_manager

        manager = GoogleAuthManager()
        services = manager.get_enabled_services()

        assert services == ["calendar", "gmail"]
        mock_scope_manager.get_enabled_services.assert_called_once()

    def test_is_service_account_handles_none_credentials_path(self):
        """Test _is_service_account when credentials_path is None."""
        manager = GoogleAuthManager(credentials_path=None)
        result = manager._is_service_account()
        assert result is False

    def test_is_service_account_handles_invalid_json(self):
        """Test _is_service_account with invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "invalid.json")
            with open(creds_path, "w") as f:
                f.write("{ invalid json }")

            manager = GoogleAuthManager(credentials_path=creds_path)
            result = manager._is_service_account()

            assert result is False

    def test_is_service_account_handles_empty_file(self):
        """Test _is_service_account with empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "empty.json")
            with open(creds_path, "w") as f:
                f.write("")

            manager = GoogleAuthManager(credentials_path=creds_path)
            result = manager._is_service_account()

            assert result is False

    @patch("auth.google_auth.ScopeManager")
    def test_scope_manager_initialized_once(self, mock_scope_manager_class):
        """Test that scope manager is only initialized once."""
        mock_instance = Mock()
        mock_scope_manager_class.return_value = mock_instance

        manager = GoogleAuthManager()

        # Call multiple times
        result1 = manager.get_scope_manager()
        result2 = manager.get_scope_manager()

        # Should be the same instance
        assert result1 is result2
        assert result1 is mock_instance

        # ScopeManager should only be instantiated once
        mock_scope_manager_class.assert_called_once()


class TestGoogleAuthManagerInitialize:
    """Test cases for GoogleAuthManager.initialize() method."""

    @pytest.mark.asyncio
    @patch("auth.google_auth.aiofiles.open")
    @patch("auth.google_auth.pickle.loads")
    @patch("os.path.exists")
    async def test_initialize_loads_existing_valid_token(
        self, mock_exists, mock_pickle_loads, mock_aiofiles_open
    ):
        """Test initialize loads existing valid token using aiofiles."""
        # Setup mock credentials
        mock_creds = Mock()
        mock_creds.valid = True
        mock_creds.scopes = ["https://www.googleapis.com/auth/calendar"]

        # Mock token file exists
        mock_exists.return_value = True

        # Mock aiofiles read with proper async context manager
        # aiofiles.open() is sync but returns an async context manager
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"pickled_data")

        mock_context = Mock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_file)
        mock_context.__aexit__ = AsyncMock(return_value=None)

        mock_aiofiles_open.return_value = mock_context

        # Mock pickle.loads to return our credentials
        mock_pickle_loads.return_value = mock_creds

        # Setup manager with mocked scope manager
        with patch("auth.google_auth.ScopeManager") as mock_scope_manager_class:
            mock_scope_manager = Mock()
            mock_scope_manager.validate_configuration.return_value = (True, [])
            mock_scope_manager.get_required_scopes.return_value = [
                "https://www.googleapis.com/auth/calendar"
            ]
            mock_scope_manager.has_scope_changes.return_value = False
            mock_scope_manager_class.return_value = mock_scope_manager

            manager = GoogleAuthManager()
            await manager.initialize()

            # Verify token was loaded
            assert manager.creds == mock_creds
            mock_aiofiles_open.assert_called()

    @pytest.mark.asyncio
    @patch("auth.google_auth.aiofiles.open")
    @patch("auth.google_auth.pickle.dumps")
    @patch("os.path.exists")
    async def test_initialize_saves_token_after_new_auth(
        self, mock_exists, mock_pickle_dumps, mock_aiofiles_open
    ):
        """Test initialize saves token after authentication using aiofiles."""
        # Mock no existing token
        mock_exists.return_value = False

        # Mock aiofiles write with proper async context manager
        # aiofiles.open() is sync but returns an async context manager
        mock_file = AsyncMock()
        mock_file.write = AsyncMock()

        mock_context = Mock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_file)
        mock_context.__aexit__ = AsyncMock(return_value=None)

        mock_aiofiles_open.return_value = mock_context

        # Mock pickle.dumps
        mock_pickle_dumps.return_value = b"pickled_creds"

        # Mock credentials that _authenticate will set
        mock_creds = Mock()
        mock_creds.valid = True

        with (
            patch("auth.google_auth.ScopeManager") as mock_scope_manager_class,
            patch.object(GoogleAuthManager, "_authenticate") as mock_auth,
        ):
            mock_scope_manager = Mock()
            mock_scope_manager.validate_configuration.return_value = (True, [])
            mock_scope_manager.get_required_scopes.return_value = [
                "https://www.googleapis.com/auth/calendar"
            ]
            mock_scope_manager_class.return_value = mock_scope_manager

            manager = GoogleAuthManager()

            # Set credentials when _authenticate is called
            def set_creds_on_manager():
                manager.creds = mock_creds

            mock_auth.side_effect = set_creds_on_manager

            await manager.initialize()

            # Verify authentication was called
            mock_auth.assert_called_once()
            # Verify token was saved
            mock_aiofiles_open.assert_called()
            mock_file.write.assert_called_with(b"pickled_creds")

    @pytest.mark.asyncio
    @patch("auth.google_auth.aiofiles.open")
    @patch("auth.google_auth.pickle.dumps")
    @patch("auth.google_auth.pickle.loads")
    @patch("os.path.exists")
    async def test_initialize_reauth_when_scopes_change(
        self, mock_exists, mock_pickle_loads, mock_pickle_dumps, mock_aiofiles_open
    ):
        """Test initialize triggers re-auth when scopes have changed."""
        # Setup mock credentials with old scopes
        mock_creds = Mock()
        mock_creds.valid = True
        mock_creds.scopes = ["https://www.googleapis.com/auth/calendar"]

        # Mock token exists
        mock_exists.return_value = True

        # Mock aiofiles for both read and write with proper async context managers
        # aiofiles.open() is sync but returns an async context manager
        mock_read_file = AsyncMock()
        mock_read_file.read = AsyncMock(return_value=b"old_pickled_data")

        mock_write_file = AsyncMock()
        mock_write_file.write = AsyncMock()

        # Create two separate context managers for read and write operations
        mock_read_context = Mock()
        mock_read_context.__aenter__ = AsyncMock(return_value=mock_read_file)
        mock_read_context.__aexit__ = AsyncMock(return_value=None)

        mock_write_context = Mock()
        mock_write_context.__aenter__ = AsyncMock(return_value=mock_write_file)
        mock_write_context.__aexit__ = AsyncMock(return_value=None)

        # Return different contexts for each call (read first, then write)
        mock_aiofiles_open.side_effect = [mock_read_context, mock_write_context]

        # Mock pickle operations
        mock_pickle_loads.return_value = mock_creds
        mock_pickle_dumps.return_value = b"new_pickled_data"

        # New credentials after re-auth
        new_creds = Mock()
        new_creds.valid = True

        with (
            patch("auth.google_auth.ScopeManager") as mock_scope_manager_class,
            patch.object(
                GoogleAuthManager, "_authenticate", return_value=None
            ) as mock_auth,
        ):
            mock_scope_manager = Mock()
            mock_scope_manager.validate_configuration.return_value = (True, [])
            mock_scope_manager.get_required_scopes.return_value = [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/gmail.readonly",
            ]
            # Scope change detected
            mock_scope_manager.has_scope_changes.return_value = True
            mock_scope_manager_class.return_value = mock_scope_manager

            manager = GoogleAuthManager()
            manager.creds = new_creds  # Set by _authenticate

            await manager.initialize()

            # Verify re-authentication was triggered
            mock_auth.assert_called_once()
            # Verify new token was saved
            assert mock_write_file.write.called

    @pytest.mark.asyncio
    async def test_initialize_raises_on_invalid_scope_configuration(self):
        """Test initialize raises error when scope configuration is invalid."""
        with patch("auth.google_auth.ScopeManager") as mock_scope_manager_class:
            mock_scope_manager = Mock()
            mock_scope_manager.validate_configuration.return_value = (
                False,
                ["Invalid service: unknown"],
            )
            mock_scope_manager_class.return_value = mock_scope_manager

            manager = GoogleAuthManager()

            with pytest.raises(RuntimeError, match="Invalid scope configuration"):
                await manager.initialize()
