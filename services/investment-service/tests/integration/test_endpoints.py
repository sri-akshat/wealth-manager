# tests/integration/test_endpoints.py

from fastapi.testclient import TestClient
from investment_service.models.investment import MutualFund, Investment
from investment_service.schemas.investment import InvestmentCreate, PortfolioSummary
from datetime import datetime, timezone
import pytest

def test_unauthorized_access(client):
    """Test access without any authorization header"""
    response = client.get("/portfolio/summary")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_invalid_auth_header_format(client):
    """Test access with invalid authorization header format"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": "InvalidFormat"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_invalid_token(client):
    """Test access with invalid token"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_missing_bearer(client):
    """Test access with token but missing Bearer prefix"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": "some.token.here"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_investment_not_found(client, test_user_token):
    """Test attempting to create investment with non-existent fund"""
    response = client.post(
        "/investments",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "fund_id": 9999,
            "purchase_amount": 10000
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Fund not found"

def test_create_investment(client, db, sample_mutual_funds, test_user_token):
    """Test successful investment creation"""
    # Get the fund from the database to ensure it's attached to the session
    fund = db.query(MutualFund).filter(MutualFund.scheme_code == "HDFC001").first()
    fund_id = fund.id  # Get the ID before the session is closed

    response = client.post(
        "/investments",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "fund_id": fund_id,
            "purchase_amount": 10000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fund_id"] == fund_id
    assert data["purchase_amount"] == 10000
    assert data["units"] == pytest.approx(99.50248756218906)  # 10000 / 100.50

def test_get_portfolio_summary(client, sample_investments, test_user_token):
    """Test getting portfolio summary for user with investments"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_investment"] == 21337.50
    assert data["current_value"] == 22587.50
    assert data["total_returns"] == 1250.00
    assert data["returns_percentage"] == pytest.approx(5.8582308142940835)  # (1250 / 21337.50) * 100
    assert data["number_of_investments"] == 2
    assert data["asset_allocation"]["equity"] == 100.0

def test_get_empty_portfolio(client, db, test_user_token):
    """Test getting portfolio summary for user without investments"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_investment"] == 0
    assert data["current_value"] == 0
    assert data["total_returns"] == 0
    assert data["returns_percentage"] == 0
    assert data["number_of_investments"] == 0
    assert data["asset_allocation"] == {}

def test_get_portfolio_summary_unauthorized(client):
    """Test portfolio summary access with invalid authentication"""
    # No token
    response = client.get("/portfolio/summary")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_invalid_token_format(client):
    """Test access with malformed token"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": "InvalidFormat Token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"