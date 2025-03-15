import pytest
from datetime import datetime
from pydantic import ValidationError
from user_service.schemas.user import UserBase, UserCreate, UserResponse, Token
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
    """Test creating a valid UserResponse instance."""
    current_time = datetime.utcnow()
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    user = UserResponse(**user_data)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER
    assert user.is_active is True
    assert user.created_at == current_time

def test_user_response_optional_last_login():
    """Test UserResponse with optional last_login."""
    current_time = datetime.utcnow()
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": Role.CUSTOMER,
        "is_active": True,
        "created_at": current_time
    }
    user = UserResponse(**user_data)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER
    assert user.is_active is True
    assert user.created_at == current_time

def test_token_valid():
    """Test creating a valid Token instance."""
    token = Token(access_token="some.jwt.token", token_type="bearer")
    assert token.access_token == "some.jwt.token"
    assert token.token_type == "bearer"

def test_token_default_type():
    """Test Token with default token type."""
    token = Token(access_token="some.jwt.token", token_type="bearer")
    assert token.token_type == "bearer" 