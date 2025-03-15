# tests/test_models.py
import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from investment_service.models.investment import Investment, MutualFund, FundCategory, InvestmentStatus

def test_mutual_fund_creation(db, sample_mutual_funds):
    fund = sample_mutual_funds[0]
    assert fund.scheme_code == "HDFC001"
    assert fund.scheme_name == "HDFC Top 100 Fund"
    assert fund.category == FundCategory.EQUITY
    assert fund.nav == 100.50
    assert fund.aum == 1000000000.00  # 1 billion
    assert fund.risk_level == "HIGH"
    assert fund.expense_ratio == 1.5

def test_investment_creation(db, sample_investments):
    investment = sample_investments[0]
    assert investment.units == 100
    assert investment.purchase_nav == 100.50
    assert investment.current_nav == 105.50
    assert investment.purchase_amount == 10050.00
    assert investment.current_value == 10550.00
    assert investment.status == InvestmentStatus.COMPLETED

def test_investment_calculate_returns(db, sample_investments):
    investment = sample_investments[0]
    returns, returns_percentage = investment.calculate_returns()
    assert returns == 500.00  # 10550 - 10050
    assert returns_percentage == pytest.approx(4.975124378109453)  # (500 / 10050) * 100

def test_investment_is_profitable(db, sample_investments):
    investment = sample_investments[0]
    assert investment.is_profitable  # Access as property, not method

def test_get_user_portfolio(db, sample_investments):
    user_id = abs(hash("test@example.com")) % (2**31)
    portfolio = Investment.get_user_portfolio(db, user_id)
    assert len(portfolio) == 2
    assert portfolio[0].purchase_amount == 10050.00
    assert portfolio[1].purchase_amount == 11287.50