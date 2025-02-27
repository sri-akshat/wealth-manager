from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError  # Change this line
from .core.database import get_db, engine
from .core.security import verify_password, get_password_hash, create_access_token
from .models.user import User, UserRole, Base
from .schemas.user import UserCreate, UserResponse, Token
from typing import List

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
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

@app.post("/token", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    try:
        from jose import jwt  # Add this import
        payload = jwt.decode(token, "your-secret-key-here", algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[UserResponse])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    # Verify admin access
    try:
        from jose import jwt  # Add this import if not at top
        payload = jwt.decode(token, "your-secret-key-here", algorithms=["HS256"])
        role = payload.get("role")
        if role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    users = db.query(User).offset(skip).limit(limit).all()
    return users
