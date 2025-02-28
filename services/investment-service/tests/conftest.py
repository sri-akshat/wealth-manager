# tests/conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from datetime import datetime
import pathlib
from jose import jwt

# Set test mode before importing anything else
os.environ["TEST_MODE"] = "True"

# Import after setting TEST_MODE
from src.main import app
from src.core.database import Base, get_db
from src.models.investment import MutualFund, Investment, FundCategory, InvestmentStatus

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Use absolute path for SQLite database
BASE_DIR = pathlib.Path(__file__).parent.parent
SQLITE_DB_PATH = BASE_DIR / "test.db"
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Create test engine
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the test database and tables"""
    # Remove the test database if it exists
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()

    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after all tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    """Creates a fresh database session for each test"""
    connection = engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()
    # Bind the session to the connection
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        # Roll back the transaction
        transaction.rollback()
        # Close the connection
        connection.close()

@pytest.fixture(scope="function")
def client(db):
    """Test client fixture that uses the db fixture"""
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Don't close here as it's handled by the db fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_token():
    """Create a valid JWT token for testing"""
    payload = {
        "sub": "test@example.com",
        "exp": datetime.utcnow().timestamp() + 3600  # 1 hour expiry
    }
    token = jwt.encode(
        payload,
        "your-secret-key-here",  # Match this with your settings.JWT_SECRET_KEY
        algorithm="HS256"
    )
    return f"Bearer {token}"


@pytest.fixture
def sample_mutual_funds(db):
    """Creates sample mutual fund data"""
    try:
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
                scheme_name="ICICI Prudential Value Fund",
                category=FundCategory.EQUITY,
                nav=50.25,
                aum=500000000,
                risk_level="HIGH",
                expense_ratio=1.2
            )
        ]
        for fund in funds:
            db.add(fund)
        db.commit()

        # Refresh the objects to ensure they have their IDs
        for fund in funds:
            db.refresh(fund)

        return funds
    except Exception as e:
        print(f"Error in sample_mutual_funds fixture: {e}")
        db.rollback()
        raise

@pytest.fixture
def sample_investments(db, sample_mutual_funds):
    """Creates sample investment data"""
    try:
        user_id = hash("test@example.com")
        investments = [
            Investment(
                user_id=user_id,
                fund_id=sample_mutual_funds[0].id,
                units=100,
                purchase_nav=95.50,
                current_nav=100.50,
                purchase_amount=9550,
                current_value=10050,
                status=InvestmentStatus.COMPLETED,
                purchase_date=datetime(2023, 1, 1)
            ),
            Investment(
                user_id=user_id,
                fund_id=sample_mutual_funds[1].id,
                units=200,
                purchase_nav=48.25,
                current_nav=50.25,
                purchase_amount=9650,
                current_value=10050,
                status=InvestmentStatus.COMPLETED,
                purchase_date=datetime(2023, 2, 1)
            )
        ]
        for investment in investments:
            db.add(investment)
        db.commit()

        # Refresh the objects to ensure they have their IDs
        for investment in investments:
            db.refresh(investment)

        return investments
    except Exception as e:
        print(f"Error in sample_investments fixture: {e}")
        db.rollback()
        raise