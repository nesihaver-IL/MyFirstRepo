"""API configuration using pydantic-settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Azure settings
    azure_subscription_id: str
    azure_resource_group: str
    azure_project_name: str

    # Agent settings
    agent_model: str = "gpt-4o"
    agent_temperature: float = 0.3
    use_file_search: bool = True

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Azure AI Search (optional)
    search_endpoint: Optional[str] = None
    search_index: str = "product-knowledge-base"

    # Azure OpenAI (optional)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
