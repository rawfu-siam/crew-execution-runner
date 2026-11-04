"""
Application Configuration Management Module.
Leverages Pydantic BaseSettings to rigidly load and validate
required environment strings and third-party URLs.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings loaded securely from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    OPENAI_API_KEY: str
    SLACK_WEBHOOK_URL: str
    N8N_WEBHOOK_URL: str
    DATABASE_URL: str = "sqlite:///./crew_runner.db"
    LOG_LEVEL: str = "INFO"


# Global settings instance for application-wide dependency injection
settings = Settings()
