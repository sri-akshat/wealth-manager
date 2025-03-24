# services/user-service/src/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from ..models.user import Role

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    role: Role = Field(default=Role.CUSTOMER, description="User's role in the system")

class UserCreate(UserBase):
    """Schema for user registration request."""
    password: str = Field(..., description="User's password", min_length=8)

class User(UserBase):
    """Schema for user response."""
    id: int = Field(..., description="User's unique identifier")
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(..., description="When the user account was created")

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class LoginResponse(BaseModel):
    """Schema for successful login response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: User = Field(..., description="User details")

class RegisterResponse(BaseModel):
    """Schema for successful registration response."""
    access_token: Optional[str] = Field(None, description="JWT access token if auto-login is enabled")
    user: User = Field(..., description="Created user details")

class UserList(BaseModel):
    """Schema for list of users response."""
    users: List[User] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of users skipped")
    limit: int = Field(..., description="Maximum number of users returned")

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: str = Field(..., description="Type of error")

class TokenResponse(BaseModel):
    """
    OAuth2 compatible token response.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(3600, description="Token expiration in seconds")
    scope: str = Field("", description="Space-separated list of granted scopes")
    user: UserBase = Field(..., description="User profile information")

    class Config:
        from_attributes = True
