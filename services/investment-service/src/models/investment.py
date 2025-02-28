from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, relationship, Session
from datetime import datetime
import enum
from ..core.database import Base  # Import Base from database.py

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

    def calculate_returns(self) -> tuple[float, float]:
        """Calculate absolute and percentage returns for the investment"""
        returns = self.current_value - self.purchase_amount
        returns_percentage = (returns / self.purchase_amount * 100) if self.purchase_amount > 0 else 0
        return returns, returns_percentage

    def update_current_value(self) -> None:
        """Update current value based on latest NAV"""
        self.current_value = self.units * self.current_nav

    @property
    def is_profitable(self) -> bool:
        """Check if investment is profitable"""
        return self.current_value > self.purchase_amount

    @classmethod
    def get_user_portfolio(cls, db: Session, user_id: str) -> list['Investment']:
        """Get all investments for a user with related fund information"""
        return db.query(cls).filter(
            cls.user_id == user_id
        ).join(
            MutualFund
        ).all()
