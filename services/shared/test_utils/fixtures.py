"""Shared test fixtures for all services."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from jose import jwt

from .db import db_engine, db

def create_test_client(app, get_db):
    """Create a test client for FastAPI application."""
    @pytest.fixture(scope="function")
    def client(db):
        def override_get_db():
            try:
                yield db
            finally:
                db.close()
                
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as test_client:
            yield test_client
    
    return client

def create_test_token(secret_key, user_email, role=None, expires_delta=None):
    """Create a test JWT token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=1)
    
    payload = {
        "sub": user_email,
        "exp": datetime.utcnow() + expires_delta
    }
    if role:
        payload["role"] = role
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return f"Bearer {token}" 