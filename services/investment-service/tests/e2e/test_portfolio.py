# tests/e2e/test_portfolio.py
import pytest
from datetime import datetime

from src.models.investment import Investment, FundCategory
from src.schemas.investment import PortfolioSummary, PortfolioInvestment

def test_portfolio_returns_calculation(db, sample_investments):
    user_id = hash("test@example.com")
    portfolio = Investment.get_user_portfolio(db, user_id)

    total_investment = sum(inv.purchase_amount for inv in portfolio)
    total_current_value = sum(inv.current_value for inv in portfolio)
    expected_returns = total_current_value - total_investment

    for investment in portfolio:
        returns, percentage = investment.calculate_returns()
        assert returns == investment.current_value - investment.purchase_amount
        assert percentage == (returns / investment.purchase_amount) * 100

def test_portfolio_asset_allocation(db, sample_investments):
    user_id = hash("test@example.com")
    portfolio = Investment.get_user_portfolio(db, user_id)

    allocation = {}
    total_value = 0

    for investment in portfolio:
        category = investment.fund.category
        allocation[category] = allocation.get(category, 0) + investment.current_value
        total_value += investment.current_value

    for category, value in allocation.items():
        allocation[category] = (value / total_value) * 100

    assert sum(allocation.values()) == pytest.approx(100.0)
    assert FundCategory.EQUITY in allocation