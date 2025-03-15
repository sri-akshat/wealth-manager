"""Test fixtures for investment service."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone
from investment_service.core.database import Base, get_db
from investment_service.core.config import settings
from investment_service.main import app
from investment_service.models.investment import MutualFund, Investment, FundCategory, InvestmentStatus
from investment_service.core.auth import create_test_token

# Set test mode
settings.TEST_MODE = True

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create a test client with a fresh database."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user():
    """Create a test user."""
    return {
        "email": "test@example.com",
        "full_name": "Test User"
    }

@pytest.fixture(scope="function")
def test_user_token(test_user):
    """Create a test token for the test user."""
    return create_test_token(test_user["email"])

@pytest.fixture(scope="function")
def sample_mutual_funds(db):
    """Create sample mutual funds."""
    funds = [
        MutualFund(
            scheme_code="HDFC001",
            scheme_name="HDFC Top 100 Fund",
            category=FundCategory.EQUITY,
            nav=100.50,
            aum=1000000000,
            risk_level="HIGH",
            expense_ratio=1.5
        ),
        MutualFund(
            scheme_code="ICICI001",
            scheme_name="ICICI Prudential Bluechip Fund",
            category=FundCategory.EQUITY,
            nav=75.25,
            aum=800000000,
            risk_level="HIGH",
            expense_ratio=1.2
        )
    ]
    for fund in funds:
        db.add(fund)
    db.commit()
    for fund in funds:
        db.refresh(fund)
    return funds

@pytest.fixture(scope="function")
def sample_investments(db, test_user, sample_mutual_funds):
    """Create sample investments for the test user."""
    user_id = abs(hash(test_user["email"])) % (2**31)  # Match the ID generation in auth.py
    investments = [
        Investment(
            user_id=user_id,
            fund_id=sample_mutual_funds[0].id,
            units=100,
            purchase_nav=100.50,
            current_nav=105.50,
            purchase_amount=10050.00,
            current_value=10550.00,
            status=InvestmentStatus.COMPLETED,
            purchase_date=datetime.now(timezone.utc)
        ),
        Investment(
            user_id=user_id,
            fund_id=sample_mutual_funds[1].id,
            units=150,
            purchase_nav=75.25,
            current_nav=80.25,
            purchase_amount=11287.50,
            current_value=12037.50,
            status=InvestmentStatus.COMPLETED,
            purchase_date=datetime.now(timezone.utc)
        )
    ]
    for investment in investments:
        db.add(investment)
    db.commit()
    for investment in investments:
        db.refresh(investment)
    return investments 