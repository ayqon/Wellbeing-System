import pytest
from unittest.mock import MagicMock
from src.repositories.base import SqlAlchemyRepository

class TestBaseRepository:
    def test_add_success(self):
        session = MagicMock()
        repo = SqlAlchemyRepository(session, MagicMock())
        item = MagicMock()
        repo.add(item)
        session.add.assert_called_with(item)
        session.commit.assert_called()

    def test_delete_success(self):
        session = MagicMock()
        repo = SqlAlchemyRepository(session, MagicMock())
        item = MagicMock()
        # Mock get to return the item
        repo.get = MagicMock(return_value=item)
        
        repo.delete(1)
        
        repo.get.assert_called_with(1)
        session.delete.assert_called_with(item)
        session.commit.assert_called()

    def test_add_error(self):
        session = MagicMock()
        session.add.side_effect = Exception("DB Error")
        repo = SqlAlchemyRepository(session, MagicMock())
        
        with pytest.raises(Exception):
            repo.add(MagicMock())
            
    def test_delete_error(self):
        session = MagicMock()
        session.delete.side_effect = Exception("DB Error")
        repo = SqlAlchemyRepository(session, MagicMock())
        
        with pytest.raises(Exception):
            repo.delete(MagicMock())

