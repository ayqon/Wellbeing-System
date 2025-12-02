import pytest
from unittest.mock import Mock
from src.repositories.system_repository import SystemRepository
from src.models.system import SystemConfig

def test_get_config_by_key():
    session = Mock()
    repo = SystemRepository(session)
    
    repo.get('test_key')
    
    session.query.assert_called_with(SystemConfig)
    session.query.return_value.filter_by.assert_called_with(key='test_key')
    session.query.return_value.filter_by.return_value.first.assert_called_once()
