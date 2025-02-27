from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum

class Base(DeclarativeBase):
    pass

class InvestmentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FundCategory(str, enum.Enum):
    EQUITY = "equity"
    DEBT = "debt"
    HYBRID = "hybrid"
    LIQUID = "liquid"
    INDEX = "index"

class MutualFund(Base):
    __tablename__ = "mutual_funds"

    id = Column(Integer, primary_key=True)
    scheme_code = Column(String, unique=True, index=True)
    scheme_name = Column(String)
    category = Column(Enum(FundCategory))
    nav = Column(Float)
    aum = Column(Float)  # Assets Under Management
    risk_level = Column(String)  # HIGH, MEDIUM, LOW
    expense_ratio = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

    investments = relationship("Investment", back_populates="fund")

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    fund_id = Column(Integer, ForeignKey("mutual_funds.id"))
    units = Column(Float)
    purchase_nav = Column(Float)
    current_nav = Column(Float)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(InvestmentStatus))
    purchase_amount = Column(Float)
    current_value = Column(Float)

    fund = relationship("MutualFund", back_populates="investments")
