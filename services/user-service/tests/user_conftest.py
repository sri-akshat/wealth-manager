"""User service test configuration."""
import pytest
from datetime import timedelta

from user_service.core.database import Base, get_db
from user_service.main import app
from user_service.models.user import User, Role
from user_service.core.security import get_password_hash, SECRET_KEY

from test_utils.db import db_engine, db
from test_utils.fixtures import create_test_client

# Create test client
client = create_test_client(app, get_db)

@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role=Role.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db):
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Admin User",
        role=Role.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_user_token(test_user):
    from test_utils.fixtures import create_test_token
    return create_test_token(
        SECRET_KEY,
        test_user.email,
        test_user.role.value,
        timedelta(hours=24)
    )

@pytest.fixture(scope="function")
def test_admin_token(test_admin):
    from test_utils.fixtures import create_test_token
    return create_test_token(
        SECRET_KEY,
        test_admin.email,
        test_admin.role.value,
        timedelta(hours=24)
    ) 