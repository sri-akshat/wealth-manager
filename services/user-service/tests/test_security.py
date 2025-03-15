import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException
from user_service.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from user_service.models.user import User, Role
from time import time
from unittest.mock import patch
from fastapi import status

def test_password_hashing():
    """Test password hashing and verification functions."""
    password = "test_password"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
    assert hashed != password  # Ensure password is actually hashed
    assert hashed.startswith("$2b$")  # Check bcrypt format

def test_token_creation():
    """Test JWT token creation."""
    data = {"sub": "test@example.com", "role": "customer"}
    token = create_access_token(data, expires_delta=timedelta(hours=24))
    
    # Verify token can be decoded
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == data["sub"]
    assert decoded["role"] == data["role"]
    assert "exp" in decoded
    
    # Test with custom expiration
    expires = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=expires)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    assert decoded["sub"] == data["sub"]
    assert decoded["role"] == data["role"]
    assert "exp" in decoded

def test_token_verification():
    """Test JWT token verification."""
    from datetime import timedelta

    # Test valid token
    data = {"sub": "test@example.com", "role": "customer"}
    token = create_access_token(data, expires_delta=timedelta(hours=24))
    assert verify_token(token) is True

    # Test invalid token
    assert verify_token("invalid_token") is False

def test_get_current_user(db, test_user):
    """Test getting current user from token."""
    from datetime import timedelta

    # Test with valid token
    token = create_access_token(
        {"sub": test_user.email, "role": test_user.role},
        expires_delta=timedelta(hours=24)
    )
    user = get_current_user(db, token)
    assert user.email == test_user.email
    assert user.role == test_user.role

    # Test with invalid token
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db, "invalid_token")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid authentication token"

    # Test with non-existent user
    token = create_access_token(
        {"sub": "nonexistent@example.com", "role": "customer"},
        expires_delta=timedelta(hours=24)
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db, token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "User not found"

def test_access_token_expiration():
    """Test access token expiration time."""
    from datetime import timedelta, datetime, timezone
    from unittest.mock import patch

    # Test with default expiration
    fixed_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # 2024-01-01 12:00:00 UTC
    with patch('user_service.core.security.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        expected_exp = int(fixed_time.timestamp()) + (30 * 60)  # Default 30 minutes
        assert decoded["exp"] == expected_exp

    # Test with custom expiration
    with patch('user_service.core.security.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        expires = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        expected_exp = int(fixed_time.timestamp()) + expires.total_seconds()
        assert decoded["exp"] == expected_exp 