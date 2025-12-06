"""
Configuration management using Pydantic
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=3306, alias="DB_PORT")
    name: str = Field(default="polymarket_insider", alias="DB_NAME")
    user: str = Field(default="root", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class PolymarketConfig(BaseSettings):
    """Polymarket API configuration"""
    api_url: str = Field(
        default="https://gamma-api.polymarket.com",
        alias="POLYMARKET_API_URL"
    )
    clob_api_url: str = Field(
        default="https://clob.polymarket.com",
        alias="POLYMARKET_CLOB_API_URL"
    )
    api_key: Optional[str] = Field(default=None, alias="POLYMARKET_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class CollectionConfig(BaseSettings):
    """Data collection configuration"""
    interval_minutes: int = Field(default=5, alias="COLLECTION_INTERVAL_MINUTES")
    max_traders_to_track: int = Field(default=1000, alias="MAX_TRADERS_TO_TRACK")
    batch_size: int = Field(default=100, alias="BATCH_SIZE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: str = Field(default="INFO", alias="LOG_LEVEL")
    file: str = Field(default="logs/polymarket.log", alias="LOG_FILE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class AppConfig(BaseSettings):
    """Application configuration"""
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class Settings:
    """Unified settings object"""
    def __init__(self):
        self.database = DatabaseConfig()
        self.polymarket = PolymarketConfig()
        self.collection = CollectionConfig()
        self.logging = LoggingConfig()
        self.app = AppConfig()


# Global settings instance
settings = Settings()
