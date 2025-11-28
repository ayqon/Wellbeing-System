import pytest
from datetime import datetime
from sqlalchemy import Column, Integer, String
from src.models.base import BaseModel, SoftDeleteMixin, TimestampMixin

# Mock model for testing
class TestModel(BaseModel, SoftDeleteMixin, TimestampMixin):
    __tablename__ = 'test_model'
    id = Column(Integer, primary_key=True)
    name = Column(String)

def test_soft_delete_mixin_defaults():
    """Test default values for SoftDeleteMixin."""
    model = TestModel(name="test")
    assert model.is_active is True
    assert model.deleted_at is None

def test_soft_delete_method():
    """Test soft_delete method updates flags."""
    model = TestModel(name="test")
    model.soft_delete()
    assert model.is_active is False
    assert isinstance(model.deleted_at, datetime)

def test_restore_method():
    """Test restore method reverts flags."""
    model = TestModel(name="test")
    model.soft_delete()
    model.restore()
    assert model.is_active is True
    assert model.deleted_at is None

def test_timestamp_mixin_attributes():
    """Test that TimestampMixin has the correct attributes."""
    # Note: Actual timestamp population usually happens on DB flush or via event listeners
    # Here we just check the attributes exist on the class/instance
    model = TestModel()
    assert hasattr(model, 'created_at')
    assert hasattr(model, 'updated_at')
