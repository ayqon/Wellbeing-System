import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from src.repositories.base import SqlAlchemyRepository
from src.models.base import Base, BaseModel

# Define a concrete model for testing
class MockModel(BaseModel):
    __tablename__ = "mock_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def repository(db_session):
    return SqlAlchemyRepository(db_session, MockModel)

def test_add_and_get(repository):
    item = MockModel(name="Test Item")
    saved_item = repository.add(item)
    assert saved_item.id is not None
    
    fetched_item = repository.get(saved_item.id)
    assert fetched_item is not None
    assert fetched_item.name == "Test Item"

def test_list(repository):
    repository.add(MockModel(name="Item 1"))
    repository.add(MockModel(name="Item 2"))
    
    items = repository.list()
    assert len(items) == 2

def test_update(repository):
    item = repository.add(MockModel(name="Old Name"))
    item.name = "New Name"
    updated_item = repository.update(item)
    
    assert updated_item.name == "New Name"
    fetched_item = repository.get(item.id)
    assert fetched_item.name == "New Name"

def test_delete(repository):
    item = repository.add(MockModel(name="To Delete"))
    assert repository.delete(item.id) is True
    assert repository.get(item.id) is None
    assert repository.delete(999) is False
