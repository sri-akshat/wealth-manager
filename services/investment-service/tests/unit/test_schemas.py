# tests/test_schemas.py
import pytest
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from investment_service.models.investment import FundCategory, InvestmentStatus
from investment_service.schemas.investment import (
    InvestmentCreate,
    InvestmentResponse,
    PortfolioSummary,
    PortfolioInvestment
)

def test_investment_create_schema():
    data = {
        "fund_id": 1,
        "purchase_amount": 10000
    }
    investment = InvestmentCreate(**data)
    assert investment.fund_id == 1
    assert investment.purchase_amount == 10000

def test_investment_response_schema():
    data = {
        "id": 1,
        "user_id": hash("test@example.com"),
        "fund_id": 1,
        "units": 100,
        "purchase_nav": 95.50,
        "current_nav": 100.50,
        "purchase_amount": 9550,
        "current_value": 10050,
        "purchase_date": datetime.utcnow(),
        "status": InvestmentStatus.COMPLETED
    }
    response = InvestmentResponse(**data)
    assert response.id == 1
    assert response.units == 100
    assert response.current_value == 10050

def test_portfolio_summary_schema():
    data = {
        "total_investment": 100000,
        "current_value": 110000,
        "total_returns": 10000,
        "returns_percentage": 10.0,
        "number_of_investments": 5,
        "asset_allocation": {
            "EQUITY": 60.0,
            "DEBT": 40.0
        }
    }
    summary = PortfolioSummary(**data)
    assert summary.total_investment == 100000
    assert summary.returns_percentage == 10.0
    assert summary.asset_allocation["EQUITY"] == 60.0

def test_portfolio_investment_schema():
    data = {
        "id": 1,
        "fund_name": "HDFC Top 100",
        "category": FundCategory.EQUITY,
        "units": 100,
        "purchase_nav": 95.50,
        "current_nav": 100.50,
        "purchase_amount": 9550,
        "current_value": 10050,
        "returns": 500,
        "returns_percentage": 5.23,
        "purchase_date": datetime.utcnow()
    }
    investment = PortfolioInvestment(**data)
    assert investment.fund_name == "HDFC Top 100"
    assert investment.category == FundCategory.EQUITY
    assert investment.returns == 500