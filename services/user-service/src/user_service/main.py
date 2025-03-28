from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from .core.security import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from .core.database import get_db, Base, engine
from .core.exceptions import http_exception_handler, validation_exception_handler
from .models.user import User, Role
from .schemas.user import (
    UserBase,
    UserCreate,
    User as UserSchema,
    LoginRequest,
    LoginResponse,
    RegisterResponse,
    UserList,
    ErrorResponse,
    TokenResponse,
    MessageResponse,
    ValidationError,
    HTTPValidationError
)
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="User Service",
        version=settings.VERSION,
        description="User management service for wealth manager platform. Handles user registration, authentication, and profile management.",
        routes=app.routes,
    )

    # Define ErrorResponse schema explicitly
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "title": "ErrorResponse",
        "type": "object",
        "properties": {
            "error": {
                "type": "string",
                "title": "Error",
                "description": "Error message"
            },
            "detail": {
                "type": "string",
                "nullable": True,
                "title": "Detail",
                "description": "Additional error details"
            }
        },
        "required": ["error"],
        "description": "Schema for error response",
        "example": {
            "error": "Invalid authentication token",
            "detail": None
        }
    }

    # Define ValidationError schema explicitly
    openapi_schema["components"]["schemas"]["ValidationError"] = {
        "title": "ValidationError",
        "type": "object",
        "properties": {
            "loc": {
                "title": "Location",
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Location of the validation error",
                "examples": [["body", "username"]]
            },
            "msg": {
                "title": "Message",
                "type": "string",
                "description": "Error message"
            },
            "type": {
                "title": "Error Type",
                "type": "string",
                "description": "Error type"
            }
        },
        "required": ["loc", "msg", "type"],
        "description": "Schema for validation error details",
        "example": {
            "loc": ["body", "username"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    }

    # Define HTTPValidationError schema explicitly
    openapi_schema["components"]["schemas"]["HTTPValidationError"] = {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {
            "detail": {
                "title": "Detail",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/ValidationError"
                },
                "description": "List of validation errors"
            }
        },
        "required": ["detail"],
        "description": "Schema for HTTP validation error response",
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

    # Update all error responses to use the correct schema
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "responses" in operation:
                for response in operation["responses"].values():
                    if "content" in response and "application/json" in response["content"]:
                        schema = response["content"]["application/json"]["schema"]
                        if schema.get("$ref") == "#/components/schemas/HTTPValidationError":
                            response["content"]["application/json"]["schema"] = {
                                "$ref": "#/components/schemas/HTTPValidationError"
                            }

    # Ensure RegisterResponse schema has correct type for access_token
    if "RegisterResponse" in openapi_schema["components"]["schemas"]:
        openapi_schema["components"]["schemas"]["RegisterResponse"]["properties"]["access_token"] = {
            "type": "string",
            "title": "Access Token",
            "description": "JWT access token if auto-login is enabled",
            "nullable": True
        }

    # Add OAuth2 password flow security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "token",
                    "scopes": {
                        "read:profile": "Read user profile",
                        "write:profile": "Update user profile",
                        "admin": "Admin access"
                    }
                }
            }
        }
    }

    # Apply security globally
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="User Service",
    description="User management service for wealth manager platform. Handles user registration, authentication, and profile management.",
    version=settings.VERSION,
    contact={
        "name": "Wealth Manager Team",
        "url": "https://github.com/sri-akshat/wealth-manager",
    },
    license_info={
        "name": "Private",
    },
    openapi_tags=[
        {
            "name": "users",
            "description": "Operations with users and profiles",
        },
        {
            "name": "auth",
            "description": "Authentication operations",
        },
        {
            "name": "system",
            "description": "System maintenance operations",
        },
    ]
)

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Configure OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "read:profile": "Read user profile",
        "write:profile": "Update user profile",
        "admin": "Admin access"
    }
)

# Override the default OpenAPI schema
app.openapi = custom_openapi

@app.get("/", response_model=MessageResponse, tags=["system"])
async def root():
    """
    Root endpoint that provides basic service information.
    
    Returns service name, version, and status.
    """
    return MessageResponse(
        message="User Service API",
        service="User Service",
        version="1.0.0",
        status="healthy"
    )

@app.get("/health", response_model=MessageResponse, tags=["system"])
def health_check():
    """Check if the service is healthy."""
    return MessageResponse(
        message="Service is operational",
        service="User Service",
        version="1.0.0",
        status="healthy"
    )

@app.post(
    "/register",
    response_model=RegisterResponse,
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Email already registered"},
    }
)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Creates a new user account with the provided details and optionally returns
    an access token for immediate authentication.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token for auto-login
    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role.value}
    )

    return RegisterResponse(
        access_token=access_token,
        user=db_user
    )

@app.post(
    "/token",
    response_model=TokenResponse,
    tags=["auth"],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
    summary="Create access token",
    description="""
    OAuth2 compatible token login, get an access token for future requests.
    
    Form Parameters:
    - **username**: Email address
    - **password**: Account password
    - **scope**: Space-separated list of requested scopes (optional)
    - **grant_type**: OAuth2 grant type, defaults to "password" (optional)
    """
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Create access token for user authentication.
    
    This endpoint implements OAuth2 password flow and expects form data with
    username (email) and password fields.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Include requested scopes in the token if they're allowed
    scopes = []
    if form_data.scopes:
        allowed_scopes = oauth2_scheme.scopes
        scopes = [scope for scope in form_data.scopes if scope in allowed_scopes]

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role.value,
            "scopes": scopes
        }
    )

    # Convert SQLAlchemy model to UserBase Pydantic model
    user_base = UserBase(
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,  # 1 hour
        scope=" ".join(scopes),
        user=user_base
    )

@app.get(
    "/users/me",
    response_model=UserSchema,
    tags=["users"],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid authentication token"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get the current authenticated user's profile.
    
    Returns the complete profile information of the currently logged-in user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    print(f"Current user: {user}")
    return UserSchema.model_validate(user)

@app.get(
    "/users",
    response_model=UserList,
    tags=["users"],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid authentication token"},
        403: {"model": ErrorResponse, "description": "Not authorized"}
    }
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get a list of all users (admin only).
    
    Returns a paginated list of user profiles. Only accessible by administrators.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != Role.ADMIN.value:
            raise HTTPException(
                status_code=403,
                detail="Not authorized"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    
    return UserList(
        users=users,
        total=total,
        skip=skip,
        limit=limit
    )
