"""
Application settings and configuration management.
"""

import logging
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"

    # Anthropic Claude Configuration
    anthropic_api_key: str
    anthropic_llm_model: str = "claude-opus-4-1-20250805"
    anthropic_fallback_model: str = "claude-sonnet-4-20250514"

    # Embeddings Configuration (using sentence-transformers)
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Telegram Bot
    telegram_bot_token: str
    telegram_admin_ids: Optional[str] = None

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # Application Settings
    log_level: str = "INFO"
    chunk_size: int = 500
    chunk_overlap: int = 100
    max_retrieval_results: int = 5
    maintenance_mode: bool = False

    # Data Paths
    raw_data_path: str = "./data/raw"
    processed_data_path: str = "./data/processed"

    # Project root
    project_root: Path = Path(__file__).parent.parent

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def admin_ids(self) -> list[int]:
        """Parse admin IDs from string."""
        if not self.telegram_admin_ids:
            return []
        return [int(uid.strip()) for uid in self.telegram_admin_ids.split(",")]

    @property
    def log_path(self) -> Path:
        """Get log file path."""
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir / "app.log"

    @property
    def raw_data_dir(self) -> Path:
        """Get raw data directory."""
        path = Path(self.raw_data_path)
        if not path.is_absolute():
            path = self.project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def processed_data_dir(self) -> Path:
        """Get processed data directory."""
        path = Path(self.processed_data_path)
        if not path.is_absolute():
            path = self.project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()


def setup_logging(settings: Settings) -> logging.Logger:
    """Setup logging configuration."""
    logger = logging.getLogger("goszakup")
    logger.setLevel(getattr(logging, settings.log_level))

    # File handler
    fh = logging.FileHandler(settings.log_path)
    fh.setLevel(getattr(logging, settings.log_level))

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, settings.log_level))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# Global settings instance
settings = get_settings()
logger = setup_logging(settings)
