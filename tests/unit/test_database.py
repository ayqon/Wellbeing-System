import pytest
from sqlalchemy.orm import Session
from src.core.database import Database
from unittest.mock import MagicMock

def test_database_singleton():
    """Test that the Database class acts as a singleton."""
    db1 = Database()
    db2 = Database()
    assert db1 is db2

def test_database_initialization():
    """Test that the database initializes the engine and session factory."""
    db = Database()
    assert db.engine is not None
    assert db.SessionLocal is not None

def test_get_db():
    """Test the get_db generator yields a session."""
    db = Database()
    # We can't easily test the session yield without a real DB connection string
    # But we can check if it returns a generator
    generator = db.get_db()
    assert hasattr(generator, '__next__')
    
    # Mock SessionLocal to return a mock session
    mock_session = MagicMock()
    db.SessionLocal = MagicMock(return_value=mock_session)
    
    gen = db.get_db()
    session = next(gen)
    assert session is mock_session
    
    # Verify close is called on cleanup
    try:
        next(gen)
    except StopIteration:
        pass
    mock_session.close.assert_called()
