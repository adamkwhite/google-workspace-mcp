#!/usr/bin/env python3
"""Interactive scope configuration tool for Google Workspace MCP."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.scope_manager import ScopeManager


class ScopeConfigurator:
    """Interactive scope configuration utility."""

    def __init__(self):
        self.scope_manager = ScopeManager()
        self.config_path = Path("config/scopes.json")

    def display_banner(self):
        """Display banner and introduction."""
        print("=" * 60)
        print("🔧 Google Workspace MCP - Scope Configuration")
        print("=" * 60)
        print()
        print("This tool helps you configure which Google services to enable.")
        print("Only enabled services will be available in the MCP server.")
        print()

    def display_current_config(self):
        """Display current configuration."""
        print("📋 Current Configuration:")
        print("-" * 25)

        config_summary = self.scope_manager.get_configuration_summary()

        print(f"Config file: {config_summary['config_file']}")
        print(f"File exists: {'✅' if config_summary['config_exists'] else '❌'}")
        print(f"Configuration valid: {'✅' if config_summary['is_valid'] else '❌'}")

        if not config_summary['is_valid']:
            print("❌ Configuration errors:")
            for error in config_summary['errors']:
                print(f"   • {error}")

        print()
        print("Enabled services:")
        for service in config_summary['enabled_services']:
            description = config_summary['service_descriptions'].get(service, '')
            print(f"   ✅ {service}: {description}")

        print()
        print("Required scopes:")
        for scope in config_summary['required_scopes']:
            print(f"   • {scope}")
        print()

    def display_available_services(self) -> Dict[str, Dict]:
        """Display available services and return service info."""
        services = {
            'calendar': {
                'name': 'Google Calendar',
                'description': 'Create, view, and manage calendar events',
                'dependencies': []
            },
            'gmail': {
                'name': 'Gmail',
                'description': 'Send, read, and manage email messages',
                'dependencies': []
            },
            'docs': {
                'name': 'Google Docs',
                'description': 'Create and edit Google Documents',
                'dependencies': ['drive']
            },
            'sheets': {
                'name': 'Google Sheets',
                'description': 'Create and edit Google Spreadsheets (Coming Soon)',
                'dependencies': ['drive']
            },
            'slides': {
                'name': 'Google Slides',
                'description': 'Create and edit Google Presentations (Coming Soon)',
                'dependencies': ['drive']
            },
            'drive': {
                'name': 'Google Drive',
                'description': 'Access Google Drive files (required for Docs/Sheets/Slides)',
                'dependencies': []
            }
        }

        print("📝 Available Services:")
        print("-" * 20)
        for service_id, info in services.items():
            deps = f" (requires: {', '.join(info['dependencies'])})" if info['dependencies'] else ""
            print(f"   {service_id}: {info['name']} - {info['description']}{deps}")
        print()

        return services

    def get_user_selection(self, available_services: Dict) -> Set[str]:
        """Get user's service selection."""
        current_enabled = self.scope_manager.get_enabled_services()

        print("🔧 Service Selection:")
        print("-" * 18)
        print("Enter services to enable (space-separated), or 'default' for recommended:")
        print(f"Current: {' '.join(sorted(current_enabled))}")
        print(f"Recommended: calendar gmail docs drive")
        print(f"Available: {' '.join(sorted(available_services.keys()))}")
        print()

        while True:
            user_input = input("Services to enable: ").strip().lower()

            if user_input == "":
                print("❌ Please enter services or 'default'")
                continue

            if user_input == "default":
                selected = {'calendar', 'gmail', 'docs', 'drive'}
                break

            # Parse space-separated services
            selected = set(user_input.split())

            # Validate selection
            invalid = selected - set(available_services.keys())
            if invalid:
                print(f"❌ Unknown services: {' '.join(invalid)}")
                print(f"   Available: {' '.join(sorted(available_services.keys()))}")
                continue

            break

        return selected

    def validate_dependencies(self, selected: Set[str], available_services: Dict) -> Set[str]:
        """Validate and add required dependencies."""
        final_selection = set(selected)
        added_deps = set()

        for service in selected:
            deps = available_services[service]['dependencies']
            for dep in deps:
                if dep not in final_selection:
                    final_selection.add(dep)
                    added_deps.add(dep)

        if added_deps:
            print(f"ℹ️ Auto-enabled dependencies: {', '.join(added_deps)}")

        return final_selection

    def confirm_selection(self, services: Set[str], available_services: Dict) -> bool:
        """Confirm user's selection."""
        print()
        print("📋 Final Configuration:")
        print("-" * 22)

        for service in sorted(services):
            info = available_services[service]
            print(f"   ✅ {service}: {info['name']} - {info['description']}")

        print()

        while True:
            confirm = input("Confirm this configuration? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' or 'n'")

    def save_configuration(self, enabled_services: Set[str]) -> bool:
        """Save the configuration to file."""
        try:
            # Get current config or use default
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = self.scope_manager._get_default_config()

            # Update enabled services
            config['enabled_services'] = {
                service: service in enabled_services
                for service in config['enabled_services'].keys()
            }

            # Ensure config directory exists
            self.config_path.parent.mkdir(exist_ok=True)

            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"✅ Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            return False

    def cleanup_tokens(self):
        """Offer to clean up tokens if scopes changed."""
        token_path = Path("config/token.pickle")

        if token_path.exists():
            print()
            print("🔄 Authentication Token Cleanup:")
            print("-" * 32)
            print("Scope changes require re-authentication.")
            print("Delete existing authentication token?")

            while True:
                cleanup = input("Delete token to force re-auth? (y/n): ").strip().lower()
                if cleanup in ['y', 'yes']:
                    try:
                        token_path.unlink()
                        print(f"✅ Deleted {token_path}")
                        print("   Next MCP startup will prompt for re-authentication")
                    except Exception as e:
                        print(f"❌ Failed to delete token: {e}")
                    break
                elif cleanup in ['n', 'no']:
                    print("   Token kept - you may need to manually delete it later")
                    break
                else:
                    print("❌ Please enter 'y' or 'n'")

    def run(self):
        """Run the interactive configuration."""
        try:
            self.display_banner()
            self.display_current_config()

            available_services = self.display_available_services()
            selected_services = self.get_user_selection(available_services)
            final_services = self.validate_dependencies(selected_services, available_services)

            if self.confirm_selection(final_services, available_services):
                if self.save_configuration(final_services):
                    self.cleanup_tokens()
                    print()
                    print("🎉 Configuration complete!")
                    print("   Restart your MCP server to apply changes.")
                    return True
            else:
                print("❌ Configuration cancelled")
                return False

        except KeyboardInterrupt:
            print("\n\n❌ Configuration cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Configuration failed: {e}")
            return False


def main():
    """Main entry point."""
    configurator = ScopeConfigurator()
    success = configurator.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())