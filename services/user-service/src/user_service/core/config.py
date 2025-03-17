# services/user-service/src/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from all locations
dotenv_locations = [
    os.path.join(os.getcwd(), '.env'),
    os.path.join(os.getcwd(), 'services', '.env'),
    os.path.join(os.getcwd(), 'services', 'user-service', '.env')
]

for location in dotenv_locations:
    if os.path.exists(location):
        load_dotenv(location)

class Settings(BaseSettings):
    PROJECT_NAME: str = "User Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/user_db"
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_SECRET_KEY: str = "your_secret_key_here"
    
    # Test configuration
    TEST_MODE: bool = False
    TESTING: bool = False
    
    # Service Information
    SERVICE_NAME: Optional[str] = None
    SERVICE_PORT: Optional[str] = None
    
    # Authentication Settings
    PASSWORD_HASH_ALGORITHM: Optional[str] = None
    PASSWORD_MIN_LENGTH: Optional[int] = None
    PASSWORD_REQUIRE_SPECIAL_CHARS: Optional[bool] = None
    PASSWORD_REQUIRE_NUMBERS: Optional[bool] = None
    
    # Email Configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_VERIFICATION_REQUIRED: Optional[bool] = None
    
    # Token Configuration
    REFRESH_TOKEN_EXPIRE_DAYS: Optional[int] = None
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    EMAIL_VERIFICATION_TOKEN_EXPIRE_DAYS: Optional[int] = None
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: Optional[bool] = None
    RATE_LIMIT_LOGIN_ATTEMPTS: Optional[int] = None
    RATE_LIMIT_LOGIN_TIMEFRAME_MINUTES: Optional[int] = None
    
    model_config = SettingsConfigDict(
        env_file=None,  # We're loading dotenv files manually above
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from environment variables
    )

settings = Settings()
