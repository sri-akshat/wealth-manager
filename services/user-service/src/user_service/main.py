from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .core.security import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from .core.database import get_db, Base, engine
from .models.user import User, Role
from .schemas.user import UserCreate, UserResponse, Token, TokenData
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="User management service for wealth manager platform. Handles user registration, authentication, and profile management.",
    version="1.0.0",
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/register", response_model=UserResponse, tags=["users"])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user: User details including email, password, full name, and role
        
    Returns:
        The created user without sensitive information
        
    Raises:
        400: If the email is already registered
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        
    Returns:
        JWT access token with type
        
    Raises:
        401: If credentials are invalid
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse, tags=["users"])
async def read_users_me(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Get the current authenticated user's profile.
    
    Returns the profile information of the currently logged-in user.
    
    Raises:
        401: If the token is invalid
        404: If user not found
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[UserResponse], tags=["users"])
async def get_users(
        skip: int = 0,
        limit: int = 100,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Get a list of all users (admin only).
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of user profiles
        
    Raises:
        401: If the token is invalid
        403: If the user is not an admin
    """
    # Verify admin access
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    users = db.query(User).offset(skip).limit(limit).all()
    return users
