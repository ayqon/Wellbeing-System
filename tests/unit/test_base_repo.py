import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from src.repositories.base import SqlAlchemyRepository
from src.models.base import Base, BaseModel

# Define a concrete model for testing purposes.
# This allows us to test the repository logic without relying on actual application models.
class MockModel(BaseModel):
    """
    A simple SQLAlchemy model used for testing the generic repository.
    """
    __tablename__ = "mock_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

@pytest.fixture
def db_session():
    """
    Fixture to create a fresh in-memory SQLite database session for each test.
    
    Yields:
        Session: A SQLAlchemy session connected to an in-memory database.
    """
    # Use an in-memory SQLite database for fast, isolated tests.
    # Initialize the Database singleton
    from src.core.database import Database
    db_instance = Database()
    
    # Create tables for the mock model
    MockModel.metadata.create_all(bind=db_instance.engine)
    
    session = db_instance.SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        MockModel.metadata.drop_all(bind=db_instance.engine)

@pytest.fixture
def repository(db_session):
    """
    Fixture to create a SqlAlchemyRepository instance using the test database session.
    
    Args:
        db_session: The database session fixture.
        
    Returns:
        SqlAlchemyRepository: A repository instance for MockModel.
    """
    return SqlAlchemyRepository(db_session, MockModel)

def test_add_and_get(repository):
    """
    Test adding a new entity and retrieving it by ID.
    """
    # Create a new item instance.
    item = MockModel(name="Test Item")
    
    # Add the item to the repository.
    saved_item = repository.add(item)
    
    # Verify that an ID was assigned (simulating auto-increment).
    assert saved_item.id is not None
    
    # Retrieve the item by its ID.
    fetched_item = repository.get(saved_item.id)
    
    # Verify that the fetched item matches the saved item.
    assert fetched_item is not None
    assert fetched_item.name == "Test Item"

def test_list(repository):
    """
    Test listing all entities in the repository.
    """
    # Add multiple items to the repository.
    repository.add(MockModel(name="Item 1"))
    repository.add(MockModel(name="Item 2"))
    
    # List all items.
    items = repository.list()
    
    # Verify that the correct number of items is returned.
    assert len(items) == 2

def test_update(repository):
    """
    Test updating an existing entity.
    """
    # Add an initial item.
    item = repository.add(MockModel(name="Old Name"))
    
    # Modify the item's attribute.
    item.name = "New Name"
    
    # Update the item in the repository.
    updated_item = repository.update(item)
    
    # Verify that the returned item has the new name.
    assert updated_item.name == "New Name"
    
    # Fetch the item again to ensure the change was persisted.
    fetched_item = repository.get(item.id)
    assert fetched_item.name == "New Name"

def test_delete(repository):
    """
    Test deleting an entity by ID.
    """
    # Add an item to delete.
    item = repository.add(MockModel(name="To Delete"))
    
    # Delete the item and verify the result is True.
    assert repository.delete(item.id) is True
    
    # Verify that the item can no longer be retrieved.
    assert repository.get(item.id) is None
    
    # Verify that deleting a non-existent ID returns False.
    assert repository.delete(999) is False
