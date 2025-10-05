"""Tests for scope manager."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.scope_manager import ScopeManager  # noqa: E402


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
