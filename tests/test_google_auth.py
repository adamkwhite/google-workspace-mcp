"""Tests for Google authentication."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.google_auth import GoogleAuthManager  # noqa: E402


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
                "private_key_id": "key123",
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
                    "client_id": "client123",
                    "client_secret": "secret123",
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
        """Test get_credentials returns credentials after initialization."""
        manager = GoogleAuthManager()
        mock_creds = Mock()
        manager.creds = mock_creds

        result = manager.get_credentials()
        assert result == mock_creds

    @patch("src.auth.google_auth.ScopeManager")
    def test_get_scope_manager(self, mock_scope_manager_class):
        """Test get_scope_manager returns scope manager instance."""
        mock_instance = Mock()
        mock_scope_manager_class.return_value = mock_instance

        manager = GoogleAuthManager()
        result = manager.get_scope_manager()

        assert result == manager.scope_manager

    @patch("src.auth.google_auth.ScopeManager")
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

    @patch("src.auth.google_auth.ScopeManager")
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
        # ScopeManager constructor should only be called once
        assert mock_scope_manager_class.call_count == 1
