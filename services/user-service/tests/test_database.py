import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy import text
from sqlalchemy.orm import Session
from user_service.models.user import User, Role
from user_service.core.database import Base, get_db
from user_service.core.security import get_password_hash

def test_database_connection(db):
    """Test database connection is working."""
    # Try to execute a simple query
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_create_user(db):
    """Test creating a user in the database."""
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

def test_get_user_by_email(db, test_user):
    """Test retrieving a user by email."""
    user = db.query(User).filter(User.email == test_user.email).first()
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email
    assert user.full_name == test_user.full_name
    assert user.role == test_user.role

def test_update_user(db, test_user):
    """Test updating a user's information."""
    # Update user's name
    test_user.full_name = "Updated Name"
    db.commit()
    db.refresh(test_user)
    
    assert test_user.full_name == "Updated Name"
    
    # Verify the update in the database
    updated_user = db.query(User).filter(User.id == test_user.id).first()
    assert updated_user.full_name == "Updated Name"

def test_delete_user(db, test_user):
    """Test deleting a user."""
    user_id = test_user.id
    db.delete(test_user)
    db.commit()
    
    # Verify user is deleted
    deleted_user = db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None

def test_unique_email_constraint(db):
    """Test that email addresses must be unique."""
    # Create first user
    user1 = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User 1",
        role=Role.CUSTOMER
    )
    db.add(user1)
    db.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User 2",
        role=Role.CUSTOMER
    )
    db.add(user2)
    
    with pytest.raises(IntegrityError):
        db.commit()

def test_user_role_enum():
    """Test that user role must be a valid enum value."""
    with pytest.raises(ValueError):
        Role("INVALID_ROLE") 