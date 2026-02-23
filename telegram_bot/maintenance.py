"""
Maintenance mode management for the Telegram bot.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Manages maintenance mode state."""

    def __init__(self, state_file: str = "maintenance_state.json"):
        """
        Initialize maintenance manager.

        Args:
            state_file: Path to maintenance state file
        """
        self.state_file = Path(state_file)

    def enable_maintenance(self, message: str = "🔧 Бот на обслуживании. Попробуйте позже.") -> bool:
        """
        Enable maintenance mode.

        Args:
            message: Message to show users

        Returns:
            True if successful
        """
        try:
            state = {"enabled": True, "message": message}
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info("Maintenance mode enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to enable maintenance: {e}")
            return False

    def disable_maintenance(self) -> bool:
        """
        Disable maintenance mode.

        Returns:
            True if successful
        """
        try:
            state = {"enabled": False, "message": None}
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info("Maintenance mode disabled")
            return True
        except Exception as e:
            logger.error(f"Failed to disable maintenance: {e}")
            return False

    def is_maintenance_enabled(self) -> bool:
        """Check if maintenance mode is enabled."""
        try:
            if not self.state_file.exists():
                return False

            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            return state.get("enabled", False)
        except Exception as e:
            logger.error(f"Failed to read maintenance state: {e}")
            return False

    def get_maintenance_message(self) -> str:
        """Get maintenance message."""
        try:
            if not self.state_file.exists():
                return "🔧 Бот на обслуживании."

            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            return state.get("message", "🔧 Бот на обслуживании.")
        except Exception as e:
            logger.error(f"Failed to get maintenance message: {e}")
            return "🔧 Бот на обслуживании."
