"""
Tests for Telegram bot functionality.
"""

import pytest

from config.settings import Settings
from telegram_bot.maintenance import MaintenanceManager


class TestMaintenanceManager:
    """Test maintenance mode management."""

    def test_enable_maintenance(self, tmp_path):
        """Test enabling maintenance mode."""
        manager = MaintenanceManager(str(tmp_path / "maintenance.json"))

        assert manager.enable_maintenance()
        assert manager.is_maintenance_enabled()
        assert "обслуживании" in manager.get_maintenance_message()

    def test_disable_maintenance(self, tmp_path):
        """Test disabling maintenance mode."""
        manager = MaintenanceManager(str(tmp_path / "maintenance.json"))

        manager.enable_maintenance()
        assert manager.disable_maintenance()
        assert not manager.is_maintenance_enabled()

    def test_custom_maintenance_message(self, tmp_path):
        """Test custom maintenance message."""
        manager = MaintenanceManager(str(tmp_path / "maintenance.json"))
        custom_msg = "🔧 Custom maintenance message"

        assert manager.enable_maintenance(custom_msg)
        assert manager.get_maintenance_message() == custom_msg
