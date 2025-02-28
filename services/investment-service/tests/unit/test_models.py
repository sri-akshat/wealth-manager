# tests/test_models.py
import pytest
from src.models.investment import Investment, MutualFund, FundCategory

def test_mutual_fund_creation(db, sample_mutual_funds):
    fund = sample_mutual_funds[0]
    assert fund.scheme_code == "HDFC001"
    assert fund.category == FundCategory.EQUITY
    assert fund.nav == 100.50

def test_investment_creation(db, sample_investments):
    investment = sample_investments[0]
    assert investment.units == 100
    assert investment.purchase_nav == 95.50
    assert investment.current_value == 10050

def test_investment_calculate_returns(db, sample_investments):
    investment = sample_investments[0]
    returns, returns_percentage = investment.calculate_returns()

    expected_returns = investment.current_value - investment.purchase_amount
    expected_percentage = (expected_returns / investment.purchase_amount) * 100

    assert returns == expected_returns
    assert returns_percentage == expected_percentage

def test_investment_is_profitable(db, sample_investments):
    investment = sample_investments[0]
    assert investment.is_profitable == True

    # Make investment unprofitable
    investment.current_nav = investment.purchase_nav * 0.9
    investment.update_current_value()
    assert investment.is_profitable == False

def test_get_user_portfolio(db, sample_investments):
    user_id = hash("test@example.com")
    portfolio = Investment.get_user_portfolio(db, user_id)

    assert len(portfolio) == 2
    assert all(inv.user_id == user_id for inv in portfolio)