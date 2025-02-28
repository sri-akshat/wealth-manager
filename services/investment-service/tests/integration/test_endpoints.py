# tests/integration/test_endpoints.py
import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client):
    """Test access without any authorization header"""
    response = client.get("/portfolio/summary")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_investment_not_found(client, test_user_token):
    """Test attempting to create investment with non-existent fund"""
    response = client.post(
        "/investments",
        headers={"Authorization": test_user_token},
        json={
            "fund_id": 9999,
            "purchase_amount": 10000
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Fund not found"

def test_create_investment(client, sample_mutual_funds, test_user_token):
    """Test successful investment creation"""
    response = client.post(
        "/investments",
        headers={"Authorization": test_user_token},
        json={
            "fund_id": sample_mutual_funds[0].id,
            "purchase_amount": 10000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["purchase_amount"] == 10000
    assert data["fund"]["scheme_code"] == "HDFC001"

def test_get_portfolio_summary(client, sample_investments, test_user_token):
    """Test getting portfolio summary for user with investments"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": test_user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["number_of_investments"] > 0
    assert data["total_investment"] > 0
    assert "asset_allocation" in data

def test_get_empty_portfolio(client, db, test_user_token):
    """Test getting portfolio summary for user without investments"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": test_user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_investment"] == 0
    assert data["number_of_investments"] == 0
    assert data["asset_allocation"] == {}

def test_get_portfolio_summary_unauthorized(client):
    """Test portfolio summary access with invalid authentication"""
    # No token
    response = client.get("/portfolio/summary")
    assert response.status_code == 401

    # Invalid token
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": "Bearer invalid.token"}
    )
    assert response.status_code == 401

def test_invalid_token_format(client):
    """Test access with malformed token"""
    response = client.get(
        "/portfolio/summary",
        headers={"Authorization": "InvalidFormat Token"}
    )
    assert response.status_code == 401