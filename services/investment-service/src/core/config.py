# src/core/config.py
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Investment Service"
    VERSION: str = "1.0.0"

    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    TEST_MODE: bool = os.getenv("TEST_MODE", "False").lower() == "true"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "investment_db")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "default_secret_key")

    @property
    def DATABASE_URL(self) -> str:
        if self.TEST_MODE:
            return "sqlite:///./test.db"
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()