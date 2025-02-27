# services/user-service/src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@user-db/userdb"
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

# services/user-service/src/models/user.py
from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import DeclarativeBase
import enum

class Base(DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    DISTRIBUTOR = "distributor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)

# services/user-service/src/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

# services/user-service/src/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .core.database import get_db
from .core.security import create_access_token, verify_password, get_password_hash
from .models.user import User, UserRole
from datetime import timedelta
from .core.config import settings

app = FastAPI(title="User Service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/users/create")
async def create_user(
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        db: Session = Depends(get_db)
):
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

@app.post("/token")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
