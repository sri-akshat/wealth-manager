# services/user-service/src/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, constr, ConfigDict
from typing import Optional, List, Literal, Union
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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "test@example.com",
                "full_name": "Test User",
                "role": "customer",
                "id": 1,
                "is_active": True,
                "created_at": "2025-03-26T23:36:59.449495"
            }
        }
    )

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
    access_token: str = Field(None, description="JWT access token if auto-login is enabled", nullable=True)
    user: User = Field(..., description="Created user details")

class UserList(BaseModel):
    """Schema for list of users response."""
    users: List[User] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of users skipped")
    limit: int = Field(..., description="Maximum number of users returned")

class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details", ge=None)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Invalid authentication token",
                "detail": None
            }
        }
    )

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

class MessageResponse(BaseModel):
    """Schema for service status and information responses."""
    message: str = Field(..., description="Response message")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Service status")

class ValidationError(BaseModel):
    """Schema for validation error details."""
    loc: List[str] = Field(
        ...,
        title="Location",
        description="Location of the validation error",
        examples=[["body", "username"]],
        json_schema_extra={
            "type": "array",
            "items": {"type": "string"}
        }
    )
    msg: str = Field(
        ...,
        title="Message",
        description="Error message"
    )
    type: str = Field(
        ...,
        title="Error Type",
        description="Error type"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "loc": ["body", "username"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        }
    }

class HTTPValidationError(BaseModel):
    """Schema for HTTP validation error response."""
    detail: List[ValidationError] = Field(
        ...,
        title="Detail",
        description="List of validation errors"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "username"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }
    }
