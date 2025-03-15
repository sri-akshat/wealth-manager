# tests/e2e/test_portfolio.py
import pytest
from datetime import datetime
from decimal import Decimal

from investment_service.models.investment import Investment, FundCategory
from investment_service.schemas.investment import PortfolioSummary, PortfolioInvestment, PortfolioAnalytics

def test_get_portfolio_summary(client, sample_investments, test_user, test_user_token):
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    
    data = response.json()
    summary = PortfolioSummary(**data)
    
    assert summary.total_investment == 21337.50  # 10050 + 11287.50
    assert summary.current_value == 22587.50  # 10550 + 12037.50
    assert summary.total_returns == 1250.00  # 22587.50 - 21337.50
    assert summary.returns_percentage == pytest.approx(5.8582308142940835)  # (1250 / 21337.50) * 100
    assert summary.number_of_investments == 2
    assert "equity" in summary.asset_allocation
    assert summary.asset_allocation["equity"] == 100.0  # Both investments are in equity funds

def test_get_portfolio_investments(client, sample_investments, test_user, test_user_token):
    response = client.get(
        "/portfolio/investments",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    
    data = response.json()
    investments = [PortfolioInvestment(**inv) for inv in data["investments"]]  # Access the investments field
    
    assert len(investments) == len(sample_investments)
    assert all(inv.category in [FundCategory.EQUITY, FundCategory.DEBT] for inv in investments)
    assert all(inv.current_value > 0 for inv in investments)
    
    # Check first investment
    assert investments[0].units == 100
    assert investments[0].purchase_nav == 100.50
    assert investments[0].current_nav == 105.50
    assert investments[0].purchase_amount == 10050.00
    assert investments[0].current_value == 10550.00
    assert investments[0].returns == 500.00
    assert investments[0].returns_percentage == pytest.approx(4.975124378109453)
    
    # Check second investment
    assert investments[1].units == 150
    assert investments[1].purchase_nav == 75.25
    assert investments[1].current_nav == 80.25
    assert investments[1].purchase_amount == 11287.50
    assert investments[1].current_value == 12037.50
    assert investments[1].returns == 750.00
    assert investments[1].returns_percentage == pytest.approx(6.64451827242525)  # (750 / 11287.50) * 100

def test_portfolio_analytics(client, sample_investments, test_user, test_user_token):
    response = client.get(
        "/portfolio/analytics",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    
    data = response.json()
    analytics = PortfolioAnalytics(**data)
    
    # Check summary
    assert analytics.summary.total_investment == 21337.50
    assert analytics.summary.current_value == 22587.50
    assert analytics.summary.total_returns == 1250.00
    assert analytics.summary.returns_percentage == pytest.approx(5.8582308142940835)
    assert analytics.summary.number_of_investments == 2
    assert "equity" in analytics.summary.asset_allocation
    assert analytics.summary.asset_allocation["equity"] == 100.0
    
    # Check investments
    assert len(analytics.investments) == 2
    assert analytics.investments[0].purchase_amount == 10050.00
    assert analytics.investments[1].purchase_amount == 11287.50

def test_portfolio_returns_calculation(db, sample_investments):
    total_investment = sum(inv.purchase_amount for inv in sample_investments)
    total_current_value = sum(inv.current_value for inv in sample_investments)
    total_returns = total_current_value - total_investment
    returns_percentage = (total_returns / total_investment) * 100

    assert total_investment == 21337.50
    assert total_current_value == 22587.50
    assert total_returns == 1250.00
    assert returns_percentage == pytest.approx(5.8582308142940835)

def test_portfolio_asset_allocation(db, sample_investments):
    total_value = sum(inv.current_value for inv in sample_investments)
    equity_value = sum(inv.current_value for inv in sample_investments if inv.fund.category == FundCategory.EQUITY)
    equity_percentage = (equity_value / total_value) * 100

    assert equity_percentage == 100.00  # All sample investments are in equity funds