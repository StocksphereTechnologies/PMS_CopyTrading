# """
# Application configuration settings


#     """Application settings"""
    
#     # Database
#     DATABASE_URL: str = "postgresql+asyncpg://postgres:root@localhost:5432/trading_db"
    
#     # Redis
#     REDIS_URL: str = "redis://localhost:6379/0"
#     REDIS_ENABLED: bool = True
    
#     # API Settings
#     API_V1_PREFIX: str = "/api/v1"
#     PROJECT_NAME: str = "Multi-Account Trading Backend"
#     VERSION: str = "1.0.0"
    
#     # Security
#     SECRET_KEY: str = "rSVnMUy_OJRKJtArWFtXtSdcgiDCQpLL05dKxJUsibI"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
#     # CORS
#     CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
#     # Broker API Settings
#     ZERODHA_API_BASE_URL: str = "https://api.kite.trade"
#     FIVEPAISA_API_BASE_URL: str = "https://openapi.5paisa.com"

    
#     class Config:
#         env_file = ".env"
#         case_sensitive = True


# settings = Settings()


"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    DATABASE_URL: str

    REDIS_URL: str
    REDIS_ENABLED: bool = True

    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Multi-Account Trading Backend"
    VERSION: str = "1.0.0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from JSON string or comma-separated"""
        if not self.CORS_ORIGINS:
            return []
        # Try parsing as JSON first
        try:
            import json
            return json.loads(self.CORS_ORIGINS)
        except:
            # Fallback to comma-separated
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin]

    ZERODHA_API_BASE_URL: str = "https://api.kite.trade"
    FIVEPAISA_API_BASE_URL: str = "https://openapi.5paisa.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

