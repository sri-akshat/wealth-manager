from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from models.investment import FundCategory, InvestmentStatus

class MutualFundBase(BaseModel):
    scheme_name: str
    category: FundCategory
    nav: float
    risk_level: str
    expense_ratio: float

    @validator('nav', 'expense_ratio')
    def validate_positive_float(cls, v):
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

class MutualFundCreate(MutualFundBase):
    scheme_code: str

class MutualFundResponse(MutualFundBase):
    id: int
    scheme_code: str
    aum: float
    last_updated: datetime

    class Config:
        from_attributes = True

class InvestmentCreate(BaseModel):
    fund_id: int
    purchase_amount: float

    @validator('purchase_amount')
    def validate_purchase_amount(cls, v):
        if v <= 0:
            raise ValueError("Purchase amount must be positive")
        return v

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

    @property
    def is_profitable(self) -> bool:
        return self.returns > 0

class PortfolioSummary(BaseModel):
    total_investment: float = Field(ge=0)
    current_value: float = Field(ge=0)
    total_returns: float
    returns_percentage: float
    number_of_investments: int = Field(ge=0)
    asset_allocation: dict[str, float]  # Category name -> allocation percentage

    class Config:
        from_attributes = True

    @validator('asset_allocation')
    def validate_allocation_percentages(cls, v):
        total = sum(v.values())
        if abs(total - 100) > 0.01 and total != 0:  # Allow for floating point imprecision
            raise ValueError("Asset allocation percentages must sum to 100%")
        return v

class PortfolioAnalytics(BaseModel):
    summary: PortfolioSummary
    investments: List[PortfolioInvestment]

    class Config:
        from_attributes = True

    @property
    def profitable_investments_count(self) -> int:
        return sum(1 for inv in self.investments if inv.is_profitable)

    @property
    def total_profitable_value(self) -> float:
        return sum(inv.current_value for inv in self.investments if inv.is_profitable)

class InvestmentFilter(BaseModel):
    category: Optional[FundCategory] = None
    min_amount: Optional[float] = Field(default=None, ge=0)
    max_amount: Optional[float] = Field(default=None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and values.get('min_amount') is not None:
            if v < values['min_amount']:
                raise ValueError("max_amount must be greater than min_amount")
        return v

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v is not None and values.get('start_date') is not None:
            if v < values['start_date']:
                raise ValueError("end_date must be after start_date")
        return v

class PortfolioSort(BaseModel):
    sort_by: Optional[str] = Field(
        default=None,
        description="Field to sort by: 'purchase_date', 'current_value', 'returns_percentage'")
    ascending: bool = True

    @validator('sort_by')
    def validate_sort_field(cls, v):
        valid_fields = {'purchase_date', 'current_value', 'returns_percentage', None}
        if v not in valid_fields:
            raise ValueError(f"sort_by must be one of: {valid_fields}")
        return v