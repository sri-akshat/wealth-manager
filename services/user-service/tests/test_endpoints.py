import pytest
from fastapi import status
from fastapi.testclient import TestClient
from user_service.models.user import Role
from user_service.core.security import create_access_token

def test_create_user(client):
    """Test user creation endpoint."""
    response = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "role": Role.CUSTOMER.value
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["full_name"] == "Test User"
    assert data["user"]["role"] == Role.CUSTOMER.value
    assert "access_token" in data

def test_register_user(client):
    """Test user registration with valid data."""
    response = client.post(
        "/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "role": Role.CUSTOMER.value
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New User"
    assert data["user"]["role"] == Role.CUSTOMER.value
    assert "access_token" in data

def test_register_duplicate_email(client, test_user):
    """Test user registration with duplicate email."""
    response = client.post(
        "/register",
        json={
            "email": test_user.email,
            "password": "password123",
            "full_name": "Duplicate User",
            "role": Role.CUSTOMER.value
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/token",
        data={
            "username": test_user.email,
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/token",
        data={
            "username": "wrong@example.com",
            "password": "wrongpass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user_token):
    """Test getting current user profile."""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == Role.CUSTOMER.value

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_users_admin(client, test_admin_token):
    """Test getting all users (admin only)."""
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)
    assert len(data["users"]) > 0
    assert "total" in data
    assert "skip" in data
    assert "limit" in data

def test_get_users_unauthorized(client, test_user_token):
    """Test getting all users with non-admin token."""
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_users_no_token(client):
    """Test getting all users without token."""
    response = client.get("/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"} 