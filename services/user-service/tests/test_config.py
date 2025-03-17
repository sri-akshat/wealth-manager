import os
from user_service.core.config import Settings

def test_settings_default_values(monkeypatch):
    # Ensure no environment variables are set that could affect the test
    monkeypatch.delenv("ENV_FILE", raising=False)
    monkeypatch.delenv("TEST_MODE", raising=False)
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("VERSION", raising=False)
    monkeypatch.delenv("API_V1_STR", raising=False)
    
    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://postgres:postgres@localhost:5432/user_db"
    assert settings.PROJECT_NAME == "User Service"
    assert settings.VERSION == "1.0.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.TEST_MODE is False
    assert settings.TESTING is False

def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@testdb:5432/testdb")
    monkeypatch.setenv("PROJECT_NAME", "Test Service")
    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://test:test@testdb:5432/testdb"
    assert settings.PROJECT_NAME == "Test Service"

def test_settings_env_file():
    settings = Settings()
    # We're now manually loading .env files, so env_file should be None
    assert settings.model_config["env_file"] is None
    assert settings.model_config["env_file_encoding"] == "utf-8"
    assert settings.model_config["case_sensitive"] is False
    # Check that extra fields are ignored
    assert settings.model_config["extra"] == "ignore" 