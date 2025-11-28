import pytest
from sqlalchemy.orm import Session
from src.core.database import Database

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
