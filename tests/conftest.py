import pytest
from src.app import create_app
from src.core.database import Database
from src.models.base import BaseModel
import src.models # Register all models

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")
    app.config.update({
        "TESTING": True,
    })
    
    # Use in-memory SQLite for tests
    # Note: Database singleton might need adjustment to support this if it's hardcoded
    # For now, we assume Database() handles it or we patch it.
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """
    Creates a new database session for a test.
    """
    db = Database()
    engine = db.engine
    
    # Create tables
    BaseModel.metadata.create_all(bind=engine)
    
    session = db.SessionLocal()
    
    yield session
    
    # Teardown
    session.close()
    BaseModel.metadata.drop_all(bind=engine)
