# services/user-service/src/models/user.py
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    DISTRIBUTOR = "distributor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
