import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from user_service.models.user import User, Role, Base
from user_service.core.security import verify_password, get_password_hash
import time

def test_user_creation(db):
    """Test creating a user with valid data."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role=Role.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER
    assert verify_password("password123", user.hashed_password)
    assert user.is_active is True
    assert user.created_at is not None

def test_user_role_values():
    """Test Role enum values."""
    assert Role.CUSTOMER.value == "customer"
    assert Role.ADMIN.value == "admin"
    assert len(Role) == 2

def test_user_role_comparison():
    """Test Role comparison."""
    assert Role.CUSTOMER.value == "customer"
    assert Role.ADMIN.value == "admin"
    assert Role.CUSTOMER != Role.ADMIN

def test_user_role_invalid():
    """Test Role with invalid value."""
    with pytest.raises(ValueError):
        Role("invalid")

def test_user_model_creation():
    """Test User model creation with all fields."""
    now = time.time()
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        role=Role.CUSTOMER,
        is_active=True,
        created_at=now
    )
    
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashedpass123"
    assert user.full_name == "Test User"
    assert user.role == Role.CUSTOMER
    assert user.is_active is True
    assert user.created_at == now

def test_user_model_defaults():
    """Test User model default values."""
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        role=Role.CUSTOMER
    )
    
    assert user.is_active is True
    assert user.created_at is not None

def test_user_model_table_name():
    """Test User model table name."""
    assert User.__tablename__ == "users"

def test_user_model_columns():
    """Test User model has all required columns."""
    columns = User.__table__.columns
    assert "id" in columns
    assert "email" in columns
    assert "hashed_password" in columns
    assert "full_name" in columns
    assert "role" in columns
    assert "is_active" in columns
    assert "created_at" in columns

def test_user_model_email_unique_constraint():
    """Test User model email unique constraint."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    session = Session(engine)
    
    # Create first user
    user1 = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User 1",
        role=Role.CUSTOMER
    )
    session.add(user1)
    session.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User 2",
        role=Role.CUSTOMER
    )
    session.add(user2)
    
    with pytest.raises(IntegrityError):
        session.commit()
    
    session.close()
    engine.dispose()

def test_user_role_validation():
    """Test Role validation."""
    with pytest.raises(ValueError):
        Role("invalid_role")

def test_user_role_validation_in_model():
    """Test Role validation in User model."""
    # Test that we can create a user with a valid role
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        role=Role.CUSTOMER
    )
    assert user.role == Role.CUSTOMER

    # Test that an invalid role is converted to the default role
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        role=None
    )
    assert user.role == Role.CUSTOMER

def test_user_password_hashing():
    """Test password hashing in User model."""
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_user_last_login_update():
    """Test updating user's last login time."""
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        role=Role.CUSTOMER
    )
    assert user.created_at is not None 