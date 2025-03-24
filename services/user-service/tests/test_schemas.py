import pytest
from datetime import datetime, UTC
from pydantic import ValidationError
from user_service.schemas.user import (
    UserBase, 
    UserCreate, 
    User, 
    TokenResponse,
    ErrorResponse,
    RegisterResponse
)
from user_service.models.user import Role

def test_user_base_valid():
    """Test creating a valid UserBase instance."""
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER
    }
    user = UserBase(**user_data)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER

def test_user_base_invalid_email():
    """Test UserBase with invalid email."""
    with pytest.raises(ValidationError):
        UserBase(email="invalid_email", full_name="Test User", role=Role.CUSTOMER)

def test_user_base_invalid_role():
    """Test UserBase with invalid role."""
    with pytest.raises(ValidationError):
        UserBase(email="test@example.com", full_name="Test User", role="invalid_role")

def test_user_base_missing_name():
    """Test UserBase with missing name."""
    with pytest.raises(ValidationError):
        UserBase(email="test@example.com", role=Role.CUSTOMER)

def test_user_create_valid():
    """Test creating a valid UserCreate instance."""
    user_data = {
        "email": "test@example.com",
        "password": "securepass123",
        "full_name": "Test User",
        "role": Role.CUSTOMER
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.password == "securepass123"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER

def test_user_create_missing_password():
    """Test UserCreate with missing password."""
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", full_name="Test User", role=Role.CUSTOMER)

def test_user_response_valid():
    """Test creating a valid User instance."""
    current_time = datetime.now(UTC)
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    user = User(**user_data)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER
    assert user.is_active is True
    assert user.created_at == current_time

def test_user_response_optional_last_login():
    """Test User with optional last_login."""
    current_time = datetime.now(UTC)
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    user = User(**user_data)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER
    assert user.is_active is True
    assert user.created_at == current_time

def test_token_response_valid():
    """Test creating a valid TokenResponse instance."""
    current_time = datetime.now(UTC)
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    token_data = {
        "access_token": "some.jwt.token",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "read:profile write:profile",
        "user": user_data
    }
    token = TokenResponse(**token_data)
    assert token.access_token == "some.jwt.token"
    assert token.token_type == "bearer"
    assert token.expires_in == 3600
    assert token.scope == "read:profile write:profile"
    assert token.user.email == "test@example.com"

def test_token_response_default_values():
    """Test TokenResponse with default values."""
    current_time = datetime.now(UTC)
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    token_data = {
        "access_token": "some.jwt.token",
        "user": user_data
    }
    token = TokenResponse(**token_data)
    assert token.token_type == "bearer"  # Default value
    assert token.expires_in == 3600  # Default value
    assert token.scope == ""  # Default value

def test_error_response_valid():
    """Test creating a valid ErrorResponse instance."""
    error_data = {
        "detail": "Invalid credentials",
        "status_code": 401,
        "error_type": "authentication_error"
    }
    error = ErrorResponse(**error_data)
    assert error.detail == "Invalid credentials"
    assert error.status_code == 401
    assert error.error_type == "authentication_error"

def test_register_response_valid():
    """Test creating a valid RegisterResponse instance."""
    current_time = datetime.now(UTC)
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    register_data = {
        "access_token": "some.jwt.token",
        "user": user_data
    }
    response = RegisterResponse(**register_data)
    assert response.access_token == "some.jwt.token"
    assert response.user.email == "test@example.com" 