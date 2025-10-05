"""Scope management utilities for Google Workspace MCP."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ScopeManager:
    """Manages Google API scopes based on user configuration."""

    def __init__(self, config_path: str = "config/scopes.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load scope configuration from file."""
        if not self.config_path.exists():
            logger.warning(
                f"Scope config not found at {self.config_path}, using defaults"
            )
            return self._get_default_config()

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            logger.info(f"Loaded scope configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading scope config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default configuration when config file doesn't exist."""
        return {
            "enabled_services": {
                "calendar": True,
                "gmail": True,
                "docs": True,
                "drive": True,
            },
            "scope_dependencies": {
                "docs": ["drive"],
                "sheets": ["drive"],
                "slides": ["drive"],
            },
            "scope_mappings": {
                "calendar": "https://www.googleapis.com/auth/calendar",
                "gmail": "https://www.googleapis.com/auth/gmail.modify",
                "docs": "https://www.googleapis.com/auth/documents",
                "sheets": "https://www.googleapis.com/auth/spreadsheets",
                "slides": "https://www.googleapis.com/auth/presentations",
                "drive": "https://www.googleapis.com/auth/drive.file",
            },
            "service_descriptions": {
                "calendar": "Create, view, and manage calendar events",
                "gmail": "Send, read, and manage email messages",
                "docs": "Create and edit Google Documents",
                "sheets": "Create and edit Google Spreadsheets",
                "slides": "Create and edit Google Presentations",
                "drive": "Access Google Drive files (required for Docs/Sheets/Slides)",
            },
        }

    def get_enabled_services(self) -> Set[str]:
        """Get set of enabled services."""
        return {
            service
            for service, enabled in self.config.get("enabled_services", {}).items()
            if enabled
        }

    def get_required_scopes(self) -> List[str]:
        """Get list of Google API scopes based on enabled services."""
        enabled_services = self.get_enabled_services()
        required_services = set(enabled_services)

        # Add dependencies
        dependencies = self.config.get("scope_dependencies", {})
        for service in enabled_services:
            if service in dependencies:
                required_services.update(dependencies[service])

        # Convert to actual Google API scopes
        scope_mappings = self.config.get("scope_mappings", {})
        scopes = []
        for service in required_services:
            if service in scope_mappings:
                scopes.append(scope_mappings[service])
            else:
                logger.warning(f"No scope mapping found for service: {service}")

        logger.info(
            f"Required scopes for enabled services {enabled_services}: {scopes}"
        )
        return scopes

    def _validate_dependencies(
        self, enabled_services: Set[str], dependencies: dict
    ) -> List[str]:
        """Validate service dependencies are met."""
        errors = []
        for service in enabled_services:
            if service in dependencies:
                for dep in dependencies[service]:
                    if (
                        dep not in self.config["enabled_services"]
                        or not self.config["enabled_services"][dep]
                    ):
                        errors.append(
                            f"Service '{service}' requires '{dep}' to be enabled"
                        )
        return errors

    def _validate_scope_mappings(
        self, enabled_services: Set[str], dependencies: dict, scope_mappings: dict
    ) -> List[str]:
        """Validate all required services have scope mappings."""
        errors = []
        required_services = set(enabled_services)
        for service in enabled_services:
            if service in dependencies:
                required_services.update(dependencies[service])

        for service in required_services:
            if service not in scope_mappings:
                errors.append(f"Missing scope mapping for service: {service}")

        return errors

    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate the current configuration."""
        errors = []

        # Check required keys
        required_keys = ["enabled_services", "scope_dependencies", "scope_mappings"]
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required config key: {key}")

        if errors:
            return False, errors

        enabled_services = self.get_enabled_services()
        dependencies = self.config.get("scope_dependencies", {})
        scope_mappings = self.config.get("scope_mappings", {})

        # Validate dependencies and scope mappings
        errors.extend(self._validate_dependencies(enabled_services, dependencies))
        errors.extend(
            self._validate_scope_mappings(
                enabled_services, dependencies, scope_mappings
            )
        )

        return len(errors) == 0, errors

    def is_service_enabled(self, service: str) -> bool:
        """Check if a specific service is enabled."""
        return self.config.get("enabled_services", {}).get(service, False)

    def get_service_description(self, service: str) -> str:
        """Get description for a service."""
        return self.config.get("service_descriptions", {}).get(
            service, f"Google {service.title()} service"
        )

    def get_configuration_summary(self) -> Dict:
        """Get a summary of the current configuration."""
        enabled_services = self.get_enabled_services()
        is_valid, errors = self.validate_configuration()

        return {
            "config_file": str(self.config_path),
            "config_exists": self.config_path.exists(),
            "enabled_services": list(enabled_services),
            "required_scopes": self.get_required_scopes(),
            "is_valid": is_valid,
            "errors": errors,
            "service_descriptions": {
                service: self.get_service_description(service)
                for service in enabled_services
            },
        }

    def has_scope_changes(self, current_scopes: List[str]) -> bool:
        """Check if current scopes differ from required scopes."""
        required_scopes = set(self.get_required_scopes())
        current_scopes_set = set(current_scopes)

        # Check if scopes have changed
        has_changes = required_scopes != current_scopes_set

        if has_changes:
            logger.info("Scope changes detected:")
            logger.info(f"  Current: {sorted(current_scopes_set)}")
            logger.info(f"  Required: {sorted(required_scopes)}")

        return has_changes

    def save_config(self, config: Optional[Dict] = None) -> bool:
        """Save configuration to file."""
        try:
            config_to_save = config or self.config

            # Ensure config directory exists
            self.config_path.parent.mkdir(exist_ok=True)

            with open(self.config_path, "w") as f:
                json.dump(config_to_save, f, indent=2)

            logger.info(f"Configuration saved to {self.config_path}")

            # Reload config
            self.config = config_to_save
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
