from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.investment import FundCategory, InvestmentStatus

class MutualFundBase(BaseModel):
    scheme_name: str
    category: FundCategory
    nav: float
    risk_level: str
    expense_ratio: float

class MutualFundCreate(MutualFundBase):
    scheme_code: str

class MutualFundResponse(MutualFundBase):
    id: int
    scheme_code: str
    aum: float
    last_updated: datetime

    class Config:
        from_attributes = True

# Remove user_id from InvestmentCreate
class InvestmentCreate(BaseModel):
    fund_id: int
    purchase_amount: float

class InvestmentResponse(BaseModel):
    id: int
    user_id: int
    fund_id: int
    units: float
    purchase_nav: float
    current_nav: float
    purchase_date: datetime
    status: InvestmentStatus
    purchase_amount: float
    current_value: float
    fund: MutualFundResponse

    class Config:
        from_attributes = True

class PortfolioSummary(BaseModel):
    total_invested: float
    current_value: float
    total_returns: float
    returns_percentage: float
    investments: List[InvestmentResponse]
