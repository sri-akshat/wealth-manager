# services/user-service/src/models/user.py
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from enum import Enum as PyEnum
from datetime import datetime
from ..core.database import Base

class Role(str, PyEnum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(Role), default=Role.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.is_active is None:
            self.is_active = True
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.role is None:
            self.role = Role.CUSTOMER
