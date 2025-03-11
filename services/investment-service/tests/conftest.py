# tests/conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from datetime import datetime, timedelta
import pathlib
from jose import jwt

# Set test mode before importing anything else
os.environ["TEST_MODE"] = "True"

# Import after setting TEST_MODE
from main import app
from core.database import Base, get_db
from core.config import settings
from models.investment import MutualFund, Investment, FundCategory, InvestmentStatus

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# SQLite test database path
SQLITE_DB_PATH = pathlib.Path("test.db")

# Test database URL
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Create test engine
engine = create_engine(DATABASE_URL)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def drop_all_tables():
    """Drop all tables and indexes from the database"""
    with engine.connect() as conn:
        # First drop all indexes
        indexes = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")).fetchall()
        for index in indexes:
            conn.execute(text(f"DROP INDEX IF EXISTS {index[0]}"))
        conn.commit()

        # Then drop all tables
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")).fetchall()
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table[0]}"))
        conn.commit()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the test database and tables"""
    # Remove the test database if it exists
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create indexes manually after tables are created
    with engine.connect() as conn:
        # Drop existing indexes if they exist
        conn.execute(text("DROP INDEX IF EXISTS ix_mutual_funds_scheme_code"))
        conn.execute(text("DROP INDEX IF EXISTS ix_investments_user_id"))
        
        # Create indexes
        conn.execute(text("CREATE UNIQUE INDEX ix_mutual_funds_scheme_code ON mutual_funds (scheme_code)"))
        conn.execute(text("CREATE INDEX ix_investments_user_id ON investments (user_id)"))
        conn.commit()

    yield

    # Drop all tables after tests are done
    Base.metadata.drop_all(bind=engine)
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()

@pytest.fixture(scope="function")
def db():
    """Create a fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
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
        "exp": datetime.utcnow() + timedelta(hours=1) # 1 hour expiry
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,  # Match this with your settings.JWT_SECRET_KEY
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