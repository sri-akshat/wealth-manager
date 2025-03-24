from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from ..models.investment import FundCategory, InvestmentStatus
from pydantic import BaseModel, Field, validator

class MutualFundBase(BaseModel):
    scheme_code: str
    scheme_name: str
    category: FundCategory
    nav: float = Field(gt=0)
    aum: float = Field(gt=0)
    risk_level: str
    expense_ratio: float = Field(gt=0)

class MutualFundCreate(MutualFundBase):
    pass

class MutualFundResponse(MutualFundBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True

class InvestmentBase(BaseModel):
    fund_id: int
    purchase_amount: float = Field(gt=0)

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentResponse(BaseModel):
    id: int
    user_id: int
    fund_id: int
    units: float
    purchase_nav: float
    current_nav: float
    purchase_amount: float
    current_value: float
    purchase_date: datetime
    status: InvestmentStatus

    class Config:
        from_attributes = True

class PortfolioInvestment(BaseModel):
    id: int
    fund_name: str
    category: FundCategory
    units: float
    purchase_nav: float
    current_nav: float
    purchase_amount: float
    current_value: float
    returns: float
    returns_percentage: float
    purchase_date: datetime

    class Config:
        from_attributes = True

class PortfolioInvestmentList(BaseModel):
    """
    A list of portfolio investments.
    """
    investments: List[PortfolioInvestment]

class PortfolioSummary(BaseModel):
    total_investment: float
    current_value: float
    total_returns: float
    returns_percentage: float
    number_of_investments: int
    asset_allocation: Dict[str, float]

class PortfolioAnalytics(BaseModel):
    summary: PortfolioSummary
    investments: List[PortfolioInvestment]

class InvestmentFilter(BaseModel):
    category: Optional[FundCategory] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator("end_date")
    def validate_date_range(cls, v, values):
        if v and values.get("start_date") and v < values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

class MessageResponse(BaseModel):
    """
    A simple message response schema.
    """
    message: str
    service: str
    version: str
    status: str