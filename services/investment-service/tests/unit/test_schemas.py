# tests/unit/test_schemas.py
import pytest
from pydantic import ValidationError
from datetime import datetime
from src.models.investment import FundCategory
from src.schemas.investment import (
    MutualFundCreate,
    InvestmentCreate,
    PortfolioSummary,
    InvestmentFilter
)

def test_mutual_fund_create_validation():
    # Valid data
    valid_data = {
        "scheme_code": "TEST001",
        "scheme_name": "Test Fund",
        "category": FundCategory.EQUITY,  # Use enum value directly
        "nav": 100.50,
        "risk_level": "HIGH",
        "expense_ratio": 1.5
    }
    fund = MutualFundCreate(**valid_data)
    assert fund.scheme_code == "TEST001"

    # Invalid nav
    with pytest.raises(ValidationError):
        invalid_data = valid_data.copy()
        invalid_data["nav"] = -100
        MutualFundCreate(**invalid_data)

def test_investment_filter_validation():
    # Valid data
    valid_data = {
        "category": FundCategory.EQUITY,  # Use enum value directly
        "min_amount": 1000,
        "max_amount": 5000,
        "start_date": datetime(2023, 1, 1),
        "end_date": datetime(2023, 12, 31)
    }
    filter_params = InvestmentFilter(**valid_data)
    assert filter_params.category == FundCategory.EQUITY

    # Invalid date range
    with pytest.raises(ValidationError):
        invalid_data = valid_data.copy()
        invalid_data["start_date"] = datetime(2023, 12, 31)
        invalid_data["end_date"] = datetime(2023, 1, 1)
        InvestmentFilter(**invalid_data)