#!/usr/bin/env python3
"""NovaCode Self-Update Engine.

Provides auto-update capabilities including version checking, configuration
migration, plugin updates, and backup/restore functionality.

Classes:
    UpdateManager: Manages the self-update process.
    VersionChecker: Checks for new versions and validates compatibility.
    ConfigMigrator: Handles configuration migration between versions.
    PluginUpdater: Manages plugin updates.

Functions:
    check_for_updates: Check if a new version is available.
    perform_update: Execute the self-update process.
    migrate_config: Migrate configuration to the latest format.
    update_plugins: Update all installed plugins.
    create_backup: Create a backup before updating.
    restore_backup: Restore from a backup if update fails.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

NOVACODE_HOME = Path.home() / ".local" / "share" / "novacode"
BACKUP_DIR = NOVACODE_HOME / "backups"
CONFIG_FILE = NOVACODE_HOME / "config.json"
VERSION_FILE = NOVACODE_HOME / "version.txt"
UPDATE_LOG = NOVACODE_HOME / "update.log"
PLUGIN_DIR = NOVACODE_HOME / "plugins"
CONFIG_VERSION = 3

UPDATE_SOURCES: Dict[str, str] = {
    "github": "https://api.github.com/repos/novacode-cli/novacode/releases/latest",
    "pypi": "https://pypi.org/pypi/novacode/json",
    "internal": "https://updates.novacode.ai/latest",
}

VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-.]?(.*))?$")


class UpdateError(Exception):
    """Raised when an update operation fails."""

    def __init__(self, message: str, recoverable: bool = True) -> None:
        super().__init__(message)
        self.recoverable = recoverable


class VersionInfo:
    """Represents a semantic version."""

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: str = "",
        raw: str = "",
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.raw = raw

    @classmethod
    def parse(cls, version_str: str) -> Optional[VersionInfo]:
        """Parse a version string into a VersionInfo object.

        Args:
            version_str: Version string like "1.2.3" or "v1.2.3-beta".

        Returns:
            VersionInfo instance or None if parsing fails.
        """
        match = VERSION_PATTERN.match(version_str.strip())
        if not match:
            return None
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4) or "",
            raw=version_str,
        )

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        return version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: VersionInfo) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        return self.prerelease < other.prerelease

    def __le__(self, other: VersionInfo) -> bool:
        return self == other or self < other

    def __gt__(self, other: VersionInfo) -> bool:
        return not self <= other

    def __ge__(self, other: VersionInfo) -> bool:
        return not self < other

    def is_compatible(self, other: VersionInfo) -> bool:
        """Check if versions are compatible (same major version).

        Args:
            other: Another VersionInfo to compare.

        Returns:
            True if major versions match.
        """
        return self.major == other.major


class VersionChecker:
    """Checks for new versions and validates compatibility.

    Attributes:
        current_version: The currently installed version.
        update_source: URL to check for updates.
    """

    def __init__(
        self,
        current_version: Optional[str] = None,
        update_source: str = "github",
    ) -> None:
        """Initialize the VersionChecker.

        Args:
            current_version: Current version string. Auto-detected if None.
            update_source: Key from UPDATE_SOURCES to use.
        """
        self.current_version = VersionInfo.parse(
            current_version or self._detect_current_version()
        ) or VersionInfo(0, 0, 0)
        self.update_source = UPDATE_SOURCES.get(update_source, UPDATE_SOURCES["github"])

    @staticmethod
    def _detect_current_version() -> str:
        """Detect the current installed version.

        Returns:
            Version string or "0.0.0" if not found.
        """
        if VERSION_FILE.exists():
            return VERSION_FILE.read_text(encoding="utf-8").strip()
        try:
            import novacode  # noqa: WPS433

            return getattr(novacode, "__version__", "0.0.0")
        except ImportError:
            return "0.0.0"

    def get_latest_version(self) -> Optional[VersionInfo]:
        """Fetch the latest version from the update source.

        Returns:
            Latest VersionInfo or None if fetch fails.
        """
        try:
            req = urllib.request.Request(
                self.update_source,
                headers={"Accept": "application/json", "User-Agent": "codeforge-updater/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if "github" in self.update_source:
                tag = data.get("tag_name", "")
                return VersionInfo.parse(tag)
            if "pypi" in self.update_source:
                version = data.get("info", {}).get("version", "")
                return VersionInfo.parse(version)
            version = data.get("version", "")
            return VersionInfo.parse(version)
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, OSError):
            return None

    def check_update_available(self) -> Tuple[bool, Optional[VersionInfo]]:
        """Check if an update is available.

        Returns:
            Tuple of (update_available, latest_version).
        """
        latest = self.get_latest_version()
        if latest is None:
            return False, None
        return latest > self.current_version, latest

    def is_update_safe(self, target_version: VersionInfo) -> bool:
        """Determine if updating to target version is safe.

        Args:
            target_version: The version to update to.

        Returns:
            True if the update is considered safe.
        """
        if not self.current_version.is_compatible(target_version):
            return False
        if target_version.prerelease:
            return False
        return True


class ConfigMigrator:
    """Handles configuration migration between versions.

    Supports incremental migration through version-numbered migration steps.
    """

    MIGRATIONS: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize the ConfigMigrator.

        Args:
            config_path: Path to the config file.
        """
        self.config_path = config_path or CONFIG_FILE
        self._register_builtin_migrations()

    def _register_builtin_migrations(self) -> None:
        """Register built-in migration functions."""
        self.MIGRATIONS = {
            1: self._migrate_v0_to_v1,
            2: self._migrate_v1_to_v2,
            3: self._migrate_v2_to_v3,
        }

    @staticmethod
    def _migrate_v0_to_v1(config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from unversioned to version 1.

        Adds version field and normalizes model settings.
        """
        config["version"] = 1
        if "model" in config and isinstance(config["model"], str):
            config["model"] = {
                "default": config["model"],
                "fallbacks": [],
            }
        return config

    @staticmethod
    def _migrate_v1_to_v2(config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1 to version 2.

        Adds plugin configuration section.
        """
        config["version"] = 2
        if "plugins" not in config:
            config["plugins"] = {
                "enabled": [],
                "auto_update": True,
                "sources": ["official"],
            }
        return config

    @staticmethod
    def _migrate_v2_to_v3(config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 2 to version 3.

        Adds learning configuration and performance tracking settings.
        """
        config["version"] = 3
        if "learning" not in config:
            config["learning"] = {
                "enabled": True,
                "db_path": str(NOVACODE_HOME / "learning.db"),
                "auto_improve": True,
                "max_patterns": 10000,
                "retention_days": 90,
            }
        if "performance_tracking" not in config:
            config["performance_tracking"] = {
                "enabled": True,
                "track_latency": True,
                "track_tokens": True,
                "track_success_rate": True,
            }
        return config

    def get_current_config_version(self) -> int:
        """Get the current config version number.

        Returns:
            Config version integer (0 if no config exists).
        """
        if not self.config_path.exists():
            return 0
        try:
            config = json.loads(self.config_path.read_text(encoding="utf-8"))
            return config.get("version", 0)
        except (json.JSONDecodeError, OSError):
            return 0

    def migrate(self, target_version: int = CONFIG_VERSION) -> bool:
        """Migrate configuration to the target version.

        Args:
            target_version: Target config version.

        Returns:
            True if migration was successful.
        """
        current = self.get_current_config_version()
        if current >= target_version:
            return True

        if not self.config_path.exists():
            config: Dict[str, Any] = {}
        else:
            try:
                config = json.loads(self.config_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                config = {}

        for version in range(current, target_version):
            migration = self.MIGRATIONS.get(version + 1)
            if migration:
                try:
                    config = migration(config)
                except Exception as exc:
                    raise UpdateError(
                        f"Migración a versión {version + 1} falló: {exc}",
                        recoverable=True,
                    )

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return True

    def validate_config(self) -> List[str]:
        """Validate the current configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: List[str] = []
        if not self.config_path.exists():
            return ["Configuration file not found"]

        try:
            config = json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"Invalid JSON: {exc}"]

        if "version" not in config:
            errors.append("Campo de versión faltante")

        if "model" in config:
            model = config["model"]
            if isinstance(model, dict):
                if "default" not in model:
                    errors.append("Config de modelo sin campo 'default'")

        return errors


class PluginUpdater:
    """Manages plugin discovery, installation, and updates."""

    PLUGIN_MANIFEST = NOVACODE_HOME / "plugin_manifest.json"

    def __init__(self, plugin_dir: Optional[Path] = None) -> None:
        """Initialize the PluginUpdater.

        Args:
            plugin_dir: Directory containing plugins.
        """
        self.plugin_dir = plugin_dir or PLUGIN_DIR
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

    def get_installed_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get all installed plugins with their metadata.

        Returns:
            Dict mapping plugin name to metadata dict.
        """
        plugins: Dict[str, Dict[str, Any]] = {}
        if self.PLUGIN_MANIFEST.exists():
            try:
                manifest = json.loads(
                    self.PLUGIN_MANIFEST.read_text(encoding="utf-8")
                )
                plugins = manifest.get("plugins", {})
            except (json.JSONDecodeError, OSError):
                pass
        return plugins

    def get_available_plugins(self) -> List[Dict[str, Any]]:
        """Fetch the list of available plugins from the registry.

        Returns:
            List of plugin metadata dicts.
        """
        try:
            url = "https://plugins.novacode.ai/registry.json"
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json", "User-Agent": "codeforge-updater/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("plugins", [])
        except (urllib.error.URLError, json.JSONDecodeError, OSError):
            return []

    def install_plugin(self, name: str, source: str = "official") -> bool:
        """Install a plugin.

        Args:
            name: Plugin name.
            source: Plugin source registry.

        Returns:
            True if installation was successful.
        """
        plugin_path = self.plugin_dir / f"{name}.py"
        try:
            if source == "official":
                url = f"https://plugins.novacode.ai/plugins/{name}.py"
                req = urllib.request.Request(
                    url, headers={"User-Agent": "novacode-updater/1.0"}
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content = resp.read()
                plugin_path.write_bytes(content)
                self._update_manifest(name, {
                    "version": "1.0.0",
                    "source": source,
                    "installed_at": datetime.now().isoformat(),
                })
                return True
        except (urllib.error.URLError, OSError) as exc:
            raise UpdateError(f"Failed to install plugin {name}: {exc}")
        return False

    def update_plugin(self, name: str) -> bool:
        """Update a single plugin to the latest version.

        Args:
            name: Plugin name.

        Returns:
            True if update was successful.
        """
        installed = self.get_installed_plugins()
        if name not in installed:
            raise UpdateError(f"Plugin '{name}' is not installed")

        plugin_meta = installed[name]
        try:
            url = f"https://plugins.novacode.ai/plugins/{name}.py"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "novacode-updater/1.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()

            plugin_path = self.plugin_dir / f"{name}.py"
            if plugin_path.exists():
                backup_path = plugin_path.with_suffix(".py.bak")
                shutil.copy2(plugin_path, backup_path)

            plugin_path.write_bytes(content)
            plugin_meta["updated_at"] = datetime.now().isoformat()
            self._update_manifest(name, plugin_meta)
            return True
        except (urllib.error.URLError, OSError) as exc:
            raise UpdateError(f"Failed to update plugin {name}: {exc}")

    def update_all_plugins(self) -> Dict[str, bool]:
        """Update all installed plugins.

        Returns:
            Dict mapping plugin name to update success status.
        """
        installed = self.get_installed_plugins()
        results: Dict[str, bool] = {}
        for name in installed:
            try:
                results[name] = self.update_plugin(name)
            except UpdateError:
                results[name] = False
        return results

    def remove_plugin(self, name: str) -> bool:
        """Remove an installed plugin.

        Args:
            name: Plugin name.

        Returns:
            True if removal was successful.
        """
        plugin_path = self.plugin_dir / f"{name}.py"
        try:
            if plugin_path.exists():
                plugin_path.unlink()
            installed = self.get_installed_plugins()
            if name in installed:
                del installed[name]
                self._save_manifest(installed)
            return True
        except OSError as exc:
            raise UpdateError(f"Failed to remove plugin {name}: {exc}")

    def _update_manifest(
        self, name: str, metadata: Dict[str, Any]
    ) -> None:
        """Update the plugin manifest with new metadata.

        Args:
            name: Plugin name.
            metadata: Plugin metadata dict.
        """
        installed = self.get_installed_plugins()
        installed[name] = metadata
        self._save_manifest(installed)

    def _save_manifest(self, plugins: Dict[str, Dict[str, Any]]) -> None:
        """Save the plugin manifest to disk.

        Args:
            plugins: Dict of plugin name to metadata.
        """
        manifest = {
            "version": 1,
            "plugins": plugins,
            "updated_at": datetime.now().isoformat(),
        }
        self.PLUGIN_MANIFEST.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


class UpdateManager:
    """Manages the complete self-update process.

    Coordinates version checking, backup creation, update execution,
    and rollback on failure.

    Attributes:
        novacode_home: Path to the NovaCode installation directory.
        backup_dir: Path to store backups.
    """

    def __init__(
        self,
        novacode_home: Optional[Path] = None,
        backup_dir: Optional[Path] = None,
    ) -> None:
        """Initialize the UpdateManager.

        Args:
            novacode_home: Path to NovaCode home directory.
            backup_dir: Path to backup directory.
        """
        self.novacode_home = novacode_home or NOVACODE_HOME
        self.backup_dir = backup_dir or BACKUP_DIR
        self.version_checker = VersionChecker()
        self.config_migrator = ConfigMigrator()
        self.plugin_updater = PluginUpdater()

    def check_for_updates(self) -> Dict[str, Any]:
        """Check for available updates.

        Returns:
            Dict with update information.
        """
        available, latest = self.version_checker.check_update_available()
        return {
            "update_available": available,
            "current_version": str(self.version_checker.current_version),
            "latest_version": str(latest) if latest else None,
            "safe_to_update": (
                self.version_checker.is_update_safe(latest) if latest else False
            ),
        }

    def create_backup(self) -> Path:
        """Create a backup of the current installation.

        Returns:
            Path to the backup directory.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)

        exclude_dirs = {"backups", "log", "output", "run", "service_cache", "__pycache__"}
        exclude_exts = {".pyc", ".pyo"}

        for item in self.novacode_home.iterdir():
            if item.name in exclude_dirs:
                continue
            if item.suffix in exclude_exts:
                continue
            try:
                if item.is_dir():
                    shutil.copytree(
                        item,
                        backup_path / item.name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
                    )
                else:
                    shutil.copy2(item, backup_path / item.name)
            except OSError:
                continue

        manifest = {
            "timestamp": timestamp,
            "version": str(self.version_checker.current_version),
            "items": [item.name for item in backup_path.iterdir()],
        }
        (backup_path / "backup_manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        return backup_path

    def restore_backup(self, backup_path: Path) -> bool:
        """Restore from a backup.

        Args:
            backup_path: Path to the backup directory.

        Returns:
            True if restore was successful.
        """
        if not backup_path.exists():
            raise UpdateError(f"Backup not found: {backup_path}", recoverable=False)

        manifest_path = backup_path / "backup_manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                items = manifest.get("items", [])
            except (json.JSONDecodeError, OSError):
                items = [item.name for item in backup_path.iterdir()]
        else:
            items = [item.name for item in backup_path.iterdir()]

        for item_name in items:
            if item_name == "backup_manifest.json":
                continue
            src = backup_path / item_name
            dst = self.novacode_home / item_name
            try:
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except OSError:
                continue
        return True

    def perform_update(
        self,
        target_version: Optional[str] = None,
        skip_backup: bool = False,
        skip_plugins: bool = False,
    ) -> Dict[str, Any]:
        """Execute the self-update process.

        Args:
            target_version: Specific version to update to. Latest if None.
            skip_backup: If True, skip creating a backup.
            skip_plugins: If True, skip plugin updates.

        Returns:
            Dict with update results.
        """
        result: Dict[str, Any] = {
            "success": False,
            "steps_completed": [],
            "errors": [],
            "backup_path": None,
        }

        update_info = self.check_for_updates()
        if not update_info["update_available"] and target_version is None:
            result["errors"].append("No updates available")
            return result

        if not skip_backup:
            try:
                backup_path = self.create_backup()
                result["backup_path"] = str(backup_path)
                result["steps_completed"].append("backup_created")
            except OSError as exc:
                result["errors"].append(f"Backup falló: {exc}")
                if not skip_backup:
                    return result

        try:
            self.config_migrator.migrate()
            result["steps_completed"].append("config_migrated")
        except UpdateError as exc:
            result["errors"].append(f"Config migration falló: {exc}")

        if not skip_plugins:
            try:
                plugin_results = self.plugin_updater.update_all_plugins()
                result["plugin_updates"] = plugin_results
                result["steps_completed"].append("plugins_updated")
            except UpdateError as exc:
                result["errors"].append(f"Plugin update falló: {exc}")

        try:
            self._update_core_files(target_version)
            result["steps_completed"].append("core_updated")
        except UpdateError as exc:
            result["errors"].append(f"Core update falló: {exc}")
            if result["backup_path"]:
                self.restore_backup(Path(result["backup_path"]))
                result["steps_completed"].append("rollback_completed")
            return result

        if target_version:
            VERSION_FILE.write_text(target_version, encoding="utf-8")
        elif update_info["latest_version"]:
            VERSION_FILE.write_text(
                str(update_info["latest_version"]), encoding="utf-8"
            )

        result["success"] = len(result["errors"]) == 0
        self._log_update(result)
        return result

    def _update_core_files(self, target_version: Optional[str] = None) -> None:
        """Update core NovaCode files.

        Args:
            target_version: Specific version to fetch.

        Raises:
            UpdateError: If the update fails.
        """
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    f"novacode=={target_version}" if target_version else "novacode",
                ],
                capture_output=True,
                timeout=120,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise UpdateError(
                f"pip install falló: {exc.stderr.decode('utf-8', errors='replace') if exc.stderr else str(exc)}"
            )
        except subprocess.TimeoutExpired:
            raise UpdateError("pip install timed out after 120 seconds")
        except FileNotFoundError:
            raise UpdateError("pip not found. Cannot perform update.")

    def _log_update(self, result: Dict[str, Any]) -> None:
        """Log update results to the update log file.

        Args:
            result: Update result dict.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }
        try:
            with UPDATE_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except OSError:
            pass

    def auto_update(
        self,
        interval_hours: int = 24,
        silent: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Perform automatic update if interval has elapsed.

        Args:
            interval_hours: Hours between update checks.
            silent: If True, suppress output.

        Returns:
            Update result dict if update was performed, None otherwise.
        """
        state_file = self.novacode_home / ".last_update_check"
        now = time.time()
        if state_file.exists():
            try:
                last_check = float(state_file.read_text(encoding="utf-8").strip())
                if now - last_check < interval_hours * 3600:
                    return None
            except (ValueError, OSError):
                pass

        state_file.write_text(str(now), encoding="utf-8")

        update_info = self.check_for_updates()
        if not update_info["update_available"]:
            return None
        if not update_info["safe_to_update"]:
            if not silent:
                print(f"Update available but not safe: {update_info['latest_version']}")
            return None

        return self.perform_update()


def check_for_updates() -> Dict[str, Any]:
    """Check if a new version is available.

    Returns:
        Dict with update availability information.
    """
    manager = UpdateManager()
    return manager.check_for_updates()


def perform_update(
    target_version: Optional[str] = None,
    skip_backup: bool = False,
) -> Dict[str, Any]:
    """Execute the self-update process.

    Args:
        target_version: Specific version to update to.
        skip_backup: If True, skip creating a backup.

    Returns:
        Dict with update results.
    """
    manager = UpdateManager()
    return manager.perform_update(target_version=target_version, skip_backup=skip_backup)


def migrate_config() -> bool:
    """Migrate configuration to the latest format.

    Returns:
        True if migration was successful.
    """
    migrator = ConfigMigrator()
    return migrator.migrate()


def update_plugins() -> Dict[str, bool]:
    """Update all installed plugins.

    Returns:
        Dict mapping plugin name to update success status.
    """
    updater = PluginUpdater()
    return updater.update_all_plugins()


def create_backup() -> Path:
    """Create a backup before updating.

    Returns:
        Path to the backup directory.
    """
    manager = UpdateManager()
    return manager.create_backup()


def restore_backup(backup_path: str) -> bool:
    """Restore from a backup.

    Args:
        backup_path: Path to the backup directory.

    Returns:
        True if restore was successful.
    """
    manager = UpdateManager()
    return manager.restore_backup(Path(backup_path))


def auto_update(interval_hours: int = 24) -> Optional[Dict[str, Any]]:
    """Perform automatic update check and apply if available.

    Args:
        interval_hours: Hours between update checks.

    Returns:
        Update result if performed, None otherwise.
    """
    manager = UpdateManager()
    return manager.auto_update(interval_hours=interval_hours)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NovaCode Self-Update Engine")
    parser.add_argument(
        "action",
        choices=["check", "update", "migrate", "plugins", "backup", "restore"],
        help="Action to perform",
    )
    parser.add_argument("--version", help="Target version for update")
    parser.add_argument("--backup-path", help="Path for restore")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup")
    parser.add_argument(
        "--interval", type=int, default=24, help="Auto-update interval in hours"
    )

    args = parser.parse_args()

    if args.action == "check":
        result = check_for_updates()
        print(json.dumps(result, indent=2))
    elif args.action == "update":
        result = perform_update(
            target_version=args.version, skip_backup=args.skip_backup
        )
        print(json.dumps(result, indent=2))
    elif args.action == "migrate":
        success = migrate_config()
        print(f"Migration {'successful' if success else 'failed'}")
    elif args.action == "plugins":
        results = update_plugins()
        print(json.dumps(results, indent=2))
    elif args.action == "backup":
        path = create_backup()
        print(f"Backup created: {path}")
    elif args.action == "restore":
        if not args.backup_path:
            print("Error: --backup-path required for restore", file=sys.stderr)
            sys.exit(1)
        success = restore_backup(args.backup_path)
        print(f"Restore {'successful' if success else 'failed'}")
