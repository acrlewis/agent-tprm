"""Configuration settings."""
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings (loaded from environment)."""

    # Claude settings
    claude_api_key: str = Field(
        ...,
        validation_alias=AliasChoices("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"),
    )
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.0  # deterministic

    # App settings
    app_env: str = "development"
    log_level: str = "INFO"

    # Data paths
    data_dir: str = "data"
    surveys_dir: str = "data/surveys"
    frameworks_dir: str = "data/frameworks"
    audit_log_dir: str = "outputs/logs"

    # Risk scoring thresholds
    risk_low_max: int = 40
    risk_moderate_max: int = 60
    risk_high_max: int = 80

    # Low confidence threshold
    low_confidence_threshold: float = 0.6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()
