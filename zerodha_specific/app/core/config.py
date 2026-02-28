"""
Application configuration settings for Zerodha Trade Copier
Loaded from .env file
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Database (SQLite — lightweight, no server needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./copier.db"

    # Encryption key for storing credentials
    SECRET_KEY: str

    # Polling
    POLL_INTERVAL_SECONDS: int = 2

    # Test mode: when True, copies ALL terminal orders (including REJECTED)
    # Set to False in production to only copy COMPLETE orders
    COPY_ALL_STATUSES: bool = True

    # Zerodha API
    ZERODHA_API_BASE_URL: str = "https://api.kite.trade"
    ZERODHA_LOGIN_BASE_URL: str = "https://kite.zerodha.com"

    # CORS
    CORS_ORIGINS: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string"""
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin]

    # Server
    PORT: int = 8001
    PROJECT_NAME: str = "Zerodha Trade Copier"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
