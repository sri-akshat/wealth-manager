# src/core/config.py
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from all locations
dotenv_locations = [
    os.path.join(os.getcwd(), '.env'),
    os.path.join(os.getcwd(), 'services', '.env'),
    os.path.join(os.getcwd(), 'services', 'investment-service', '.env')
]

for location in dotenv_locations:
    if os.path.exists(location):
        load_dotenv(location)

class Settings:
    PROJECT_NAME: str = "Investment Service"
    VERSION: str = "1.0.0"

    # Test configuration
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    TEST_MODE: bool = os.getenv("TEST_MODE", "False").lower() == "true"

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "investment_db")
    
    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    
    # Service Information
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "investment-service")
    SERVICE_PORT: str = os.getenv("SERVICE_PORT", "8001")
    
    # Feature Flags
    ENABLE_MARKET_DATA: bool = os.getenv("ENABLE_MARKET_DATA", "true").lower() == "true"
    ENABLE_PORTFOLIO_ANALYTICS: bool = os.getenv("ENABLE_PORTFOLIO_ANALYTICS", "true").lower() == "true"
    
    # External APIs
    MARKET_DATA_API_KEY: str = os.getenv("MARKET_DATA_API_KEY", "")
    MARKET_DATA_API_URL: str = os.getenv("MARKET_DATA_API_URL", "")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_TIMEFRAME_SECONDS: int = int(os.getenv("RATE_LIMIT_TIMEFRAME_SECONDS", "60"))
    
    # Cache Configuration
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))

    @property
    def DATABASE_URL(self) -> str:
        # Use environment DATABASE_URL if provided
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            return env_db_url
            
        # Use SQLite for tests
        if self.TEST_MODE:
            return "sqlite:///./test.db"
            
        # Otherwise, use PostgreSQL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()