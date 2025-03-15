"""Database test utilities shared across services."""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
import os

def is_sqlite_url(url):
    """Check if the database URL is for SQLite."""
    return url.startswith('sqlite')

def create_test_engine(database_url=None, **kwargs):
    """Create a test database engine."""
    if database_url is None:
        database_url = "sqlite:///:memory:"
    
    connect_args = {}
    if is_sqlite_url(database_url):
        connect_args["check_same_thread"] = False
        kwargs["poolclass"] = StaticPool
    
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        **kwargs
    )

    if is_sqlite_url(database_url):
        # Enable SQLite foreign key support
        event.listen(engine, "connect", _set_sqlite_pragma)
    
    return engine

def create_test_session_factory(engine):
    """Create a test session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable SQLite foreign key support."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    database_url = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    engine = create_test_engine(database_url)
    yield engine

@pytest.fixture(scope="function")
def db(db_engine):
    """Create a test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = create_test_session_factory(db_engine)(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close() 