"""Unit tests for OAuth2 token refresh functionality."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from google.auth.exceptions import RefreshError

from auth.google_auth import GoogleAuthManager


class TestTokenRefresh:
    """Test cases for token refresh functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auth_manager = GoogleAuthManager()

    def test_should_refresh_token_no_credentials(self):
        """Test should_refresh_token returns False when no credentials exist."""
        self.auth_manager.creds = None
        assert self.auth_manager.should_refresh_token() is False

    def test_should_refresh_token_no_expiry(self):
        """Test should_refresh_token returns False when credentials have no expiry."""
        self.auth_manager.creds = Mock()
        self.auth_manager.creds.expiry = None
        assert self.auth_manager.should_refresh_token() is False

    def test_should_refresh_token_within_buffer(self):
        """Test should_refresh_token returns True when expiry is within buffer."""
        self.auth_manager.creds = Mock()
        # Set expiry to 5 minutes from now (within 10-minute buffer)
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        assert self.auth_manager.should_refresh_token() is True

    def test_should_refresh_token_exactly_at_buffer(self):
        """Test should_refresh_token returns True when expiry equals buffer."""
        self.auth_manager.creds = Mock()
        # Set expiry to exactly 10 minutes from now (at buffer boundary)
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(seconds=600)
        assert self.auth_manager.should_refresh_token() is True

    def test_should_refresh_token_outside_buffer(self):
        """Test should_refresh_token returns False when expiry is beyond buffer."""
        self.auth_manager.creds = Mock()
        # Set expiry to 15 minutes from now (beyond 10-minute buffer)
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
        assert self.auth_manager.should_refresh_token() is False

    def test_should_refresh_token_already_expired(self):
        """Test should_refresh_token returns True when token is already expired."""
        self.auth_manager.creds = Mock()
        # Set expiry to past time
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) - timedelta(minutes=5)
        assert self.auth_manager.should_refresh_token() is True

    @pytest.mark.asyncio
    @patch("auth.google_auth.Request")
    async def test_refresh_token_success(self, mock_request):
        """Test successful token refresh."""
        self.auth_manager.creds = Mock()
        self.auth_manager.creds.refresh = Mock()

        # Mock save_credentials
        self.auth_manager.save_credentials = Mock()

        await self.auth_manager.refresh_token()

        # Verify refresh was called
        self.auth_manager.creds.refresh.assert_called_once()
        # Verify credentials were saved
        self.auth_manager.save_credentials.assert_called_once()

    @pytest.mark.asyncio
    @patch("auth.google_auth.Request")
    async def test_refresh_token_failure_triggers_reauth(self, mock_request):
        """Test that refresh failure triggers re-authentication."""
        self.auth_manager.creds = Mock()
        self.auth_manager.creds.refresh = Mock(side_effect=RefreshError("Token revoked"))

        # Mock _authenticate and save_credentials
        self.auth_manager._authenticate = AsyncMock()
        self.auth_manager.save_credentials = Mock()

        await self.auth_manager.refresh_token()

        # Verify re-authentication was triggered
        self.auth_manager._authenticate.assert_called_once()
        # Verify credentials were saved after re-authentication
        self.auth_manager.save_credentials.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_valid_credentials_proactive_refresh(self):
        """Test ensure_valid_credentials triggers proactive refresh."""
        self.auth_manager.creds = Mock()
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        self.auth_manager.creds.valid = True

        # Mock refresh_token
        self.auth_manager.refresh_token = AsyncMock()

        result = await self.auth_manager.ensure_valid_credentials()

        # Verify proactive refresh was triggered
        self.auth_manager.refresh_token.assert_called_once()
        # Verify credentials were returned
        assert result == self.auth_manager.creds

    @pytest.mark.asyncio
    async def test_ensure_valid_credentials_reactive_refresh(self):
        """Test ensure_valid_credentials triggers reactive refresh for invalid creds."""
        self.auth_manager.creds = Mock()
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        self.auth_manager.creds.valid = False  # Invalid credentials

        # Mock refresh_token
        self.auth_manager.refresh_token = AsyncMock()

        result = await self.auth_manager.ensure_valid_credentials()

        # Verify reactive refresh was triggered
        self.auth_manager.refresh_token.assert_called_once()
        # Verify credentials were returned
        assert result == self.auth_manager.creds

    @pytest.mark.asyncio
    async def test_ensure_valid_credentials_no_refresh_needed(self):
        """Test ensure_valid_credentials skips refresh when not needed."""
        self.auth_manager.creds = Mock()
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        self.auth_manager.creds.valid = True  # Valid and not expiring soon

        # Mock refresh_token
        self.auth_manager.refresh_token = AsyncMock()

        result = await self.auth_manager.ensure_valid_credentials()

        # Verify refresh was NOT called
        self.auth_manager.refresh_token.assert_not_called()
        # Verify credentials were returned
        assert result == self.auth_manager.creds

    @pytest.mark.asyncio
    async def test_ensure_valid_credentials_uses_lock(self):
        """Test ensure_valid_credentials uses threading lock for safety."""
        import threading

        self.auth_manager.creds = Mock()
        self.auth_manager.creds.expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        self.auth_manager.creds.valid = True

        # Mock refresh_token
        self.auth_manager.refresh_token = AsyncMock()

        # Verify the auth_manager has a refresh_lock of the correct type
        assert type(self.auth_manager.refresh_lock).__name__ == "lock"

        # Call ensure_valid_credentials
        await self.auth_manager.ensure_valid_credentials()

        # Verify refresh was called (lock was acquired and released successfully)
        self.auth_manager.refresh_token.assert_called_once()

    def test_token_refresh_buffer_constant(self):
        """Test TOKEN_REFRESH_BUFFER constant is set correctly."""
        assert GoogleAuthManager.TOKEN_REFRESH_BUFFER == 600  # 10 minutes in seconds

    @patch("auth.google_auth.pickle")
    def test_save_credentials_creates_directory(self, mock_pickle):
        """Test save_credentials creates config directory if needed."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            self.auth_manager.token_path = Path(tmpdir) / "config" / "token.pickle"
            self.auth_manager.creds = Mock()

            self.auth_manager.save_credentials()

            # Verify directory was created
            assert self.auth_manager.token_path.parent.exists()
            # Verify pickle.dump was called
            mock_pickle.dump.assert_called_once()

    def test_save_credentials_no_creds(self):
        """Test save_credentials handles None credentials gracefully."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            self.auth_manager.token_path = Path(tmpdir) / "token.pickle"
            self.auth_manager.creds = None

            # Should not raise an error
            self.auth_manager.save_credentials()

            # File should not be created
            assert not self.auth_manager.token_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
