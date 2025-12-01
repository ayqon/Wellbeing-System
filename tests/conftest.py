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
    # Patch Database singleton to use in-memory DB if not already
    # But wait, app creation might have triggered Database init.
    # We should force re-init or patch the existing instance.
    
    from src.core.database import Database
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    
    db = Database()
    
    # Force in-memory engine for tests
    # Use StaticPool to share connection across threads/requests in test
    if not str(db.engine.url).startswith("sqlite:///:memory:"):
        db.engine = create_engine(
            "sqlite:///:memory:", 
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.engine)
    
    engine = db.engine
    
    # Create tables
    BaseModel.metadata.create_all(bind=engine)
    
    session = db.SessionLocal()
    
    yield session
    
    # Teardown
    session.close()
    BaseModel.metadata.drop_all(bind=engine)
