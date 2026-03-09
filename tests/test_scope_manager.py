"""Tests for scope manager."""

import json
import tempfile
from pathlib import Path

from utils.scope_manager import ScopeManager


class TestScopeManager:
    """Test cases for ScopeManager."""

    def test_init_with_default_config(self):
        """Test initialization with default config path."""
        manager = ScopeManager()
        assert manager.config_path == Path("config/scopes.json")

    def test_init_with_custom_config(self):
        """Test initialization with custom config path."""
        custom_path = "custom/path/config.json"
        manager = ScopeManager(custom_path)
        assert manager.config_path == Path(custom_path)

    def test_get_enabled_services_default(self):
        """Test getting enabled services with default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            manager = ScopeManager(str(config_path))

            # Default should enable all services
            services = manager.get_enabled_services()
            assert "calendar" in services
            assert "gmail" in services
            assert "docs" in services

    def test_get_enabled_services_custom(self):
        """Test getting enabled services from custom config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"calendar": True, "gmail": True, "docs": False},
                "scope_mappings": {},
                "scope_dependencies": {},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            services = manager.get_enabled_services()

            assert "calendar" in services
            assert "gmail" in services
            assert "docs" not in services

    def test_get_required_scopes_calendar(self):
        """Test getting required scopes for calendar service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"calendar": True},
                "scope_mappings": {
                    "calendar": "https://www.googleapis.com/auth/calendar"
                },
                "scope_dependencies": {},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            scopes = manager.get_required_scopes()

            assert any("calendar" in scope.lower() for scope in scopes)

    def test_get_required_scopes_gmail(self):
        """Test getting required scopes for gmail service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {
                    "gmail": "https://www.googleapis.com/auth/gmail.modify"
                },
                "scope_dependencies": {},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            scopes = manager.get_required_scopes()

            assert any("gmail" in scope.lower() for scope in scopes)

    def test_get_required_scopes_docs_includes_drive(self):
        """Test that docs service includes drive scopes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"docs": True},
                "scope_mappings": {
                    "docs": "https://www.googleapis.com/auth/documents",
                    "drive": "https://www.googleapis.com/auth/drive.file",
                },
                "scope_dependencies": {"docs": ["drive"]},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            scopes = manager.get_required_scopes()

            # Docs requires drive
            assert any("drive" in scope.lower() for scope in scopes)

    def test_save_config(self):
        """Test saving configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            manager = ScopeManager(str(config_path))

            config_data = {
                "enabled_services": {"calendar": True},
                "scope_mappings": {
                    "calendar": "https://www.googleapis.com/auth/calendar"
                },
                "scope_dependencies": {},
            }

            result = manager.save_config(config_data)
            assert result is True
            assert config_path.exists()

            # Verify saved data
            saved_data = json.loads(config_path.read_text())
            assert saved_data["enabled_services"] == {"calendar": True}

    def test_get_configuration_summary(self):
        """Test getting configuration summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"calendar": True, "gmail": True},
                "scope_mappings": {},
                "scope_dependencies": {},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            summary = manager.get_configuration_summary()

            assert "config_file" in summary
            assert "enabled_services" in summary
            # enabled_services is a set, convert to list for assertion
            enabled_list = list(summary["enabled_services"])
            assert "calendar" in enabled_list
            assert "gmail" in enabled_list

    def test_has_scope_changes_no_changes(self):
        """Test detecting no scope changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            manager = ScopeManager(str(config_path))

            scopes = manager.get_required_scopes()
            has_changes = manager.has_scope_changes(scopes)

            assert has_changes is False

    def test_has_scope_changes_with_changes(self):
        """Test detecting scope changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            manager = ScopeManager(str(config_path))

            # Different scopes should trigger change detection
            different_scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
            has_changes = manager.has_scope_changes(different_scopes)

            assert has_changes is True

    def test_load_config_missing_file(self):
        """Test loading config when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.json"
            manager = ScopeManager(str(config_path))

            # Should return default config
            config = manager.config
            assert "enabled_services" in config

    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "invalid.json"
            config_path.write_text("{ invalid json }")

            manager = ScopeManager(str(config_path))

            # Should fall back to default config
            config = manager.config
            assert "enabled_services" in config


class TestGmailSettings:
    """Test cases for Gmail settings functionality."""

    def test_get_gmail_settings_no_settings(self):
        """Test getting Gmail settings when none are configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {},
                "scope_dependencies": {},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            settings = manager.get_gmail_settings()

            assert settings == {}

    def test_get_gmail_settings_with_restriction(self):
        """Test getting Gmail settings with restriction configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {},
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": "Jobs"},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            settings = manager.get_gmail_settings()

            assert settings == {"restricted_label": "Jobs"}

    def test_get_restricted_label_none(self):
        """Test getting restricted label when none configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {},
                "scope_dependencies": {},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            label = manager.get_restricted_label()

            assert label is None

    def test_get_restricted_label_configured(self):
        """Test getting restricted label when configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {},
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": "Jobs"},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            label = manager.get_restricted_label()

            assert label == "Jobs"

    def test_validate_gmail_settings_valid(self):
        """Test validating valid Gmail settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {
                    "gmail": "https://www.googleapis.com/auth/gmail.modify"
                },
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": "Jobs"},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            is_valid, errors = manager.validate_configuration()

            assert is_valid is True
            assert len(errors) == 0

    def test_validate_gmail_settings_invalid_type(self):
        """Test validating Gmail settings with invalid label type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {
                    "gmail": "https://www.googleapis.com/auth/gmail.modify"
                },
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": 123},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            is_valid, errors = manager.validate_configuration()

            assert is_valid is False
            assert any("must be a string" in error for error in errors)

    def test_validate_gmail_settings_empty_string(self):
        """Test validating Gmail settings with empty label string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {
                    "gmail": "https://www.googleapis.com/auth/gmail.modify"
                },
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": ""},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            is_valid, errors = manager.validate_configuration()

            assert is_valid is False
            assert any("cannot be empty" in error for error in errors)

    def test_validate_gmail_settings_whitespace_only(self):
        """Test validating Gmail settings with whitespace-only label."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {
                    "gmail": "https://www.googleapis.com/auth/gmail.modify"
                },
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": "   "},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            is_valid, errors = manager.validate_configuration()

            assert is_valid is False
            assert any("cannot be empty" in error for error in errors)

    def test_validate_gmail_settings_disabled_gmail(self):
        """Test that Gmail settings are not validated when Gmail is disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": False},
                "scope_mappings": {},
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": ""},  # Invalid but ignored
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            is_valid, errors = manager.validate_configuration()

            assert is_valid is True
            assert len(errors) == 0

    def test_configuration_summary_includes_gmail_settings(self):
        """Test that configuration summary includes Gmail settings when Gmail is enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": True},
                "scope_mappings": {},
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": "Jobs"},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            summary = manager.get_configuration_summary()

            assert "gmail_settings" in summary
            assert summary["gmail_settings"]["restricted_label"] == "Jobs"

    def test_configuration_summary_excludes_gmail_settings_when_disabled(self):
        """Test that configuration summary excludes Gmail settings when Gmail is disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "scopes.json"
            config_data = {
                "enabled_services": {"gmail": False, "calendar": True},
                "scope_mappings": {},
                "scope_dependencies": {},
                "gmail_settings": {"restricted_label": "Jobs"},
            }
            config_path.write_text(json.dumps(config_data))

            manager = ScopeManager(str(config_path))
            summary = manager.get_configuration_summary()

            assert "gmail_settings" not in summary
