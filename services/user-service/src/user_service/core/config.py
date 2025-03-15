# services/user-service/src/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

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
    
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
