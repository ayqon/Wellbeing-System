import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from src.services.admin_service import AdminService
from src.models.user import User
from src.models.system import SystemConfig

@pytest.fixture
def user_repo():
    return Mock()

@pytest.fixture
def system_repo():
    return Mock()

@pytest.fixture
def admin_service(user_repo, system_repo):
    return AdminService(user_repo, system_repo)

def test_create_user_success(admin_service, user_repo):
    user_repo.get_by_username.return_value = None
    
    user = admin_service.create_user("testuser", "password", "STUDENT")
    
    assert user.username == "testuser"
    assert user.role == "STUDENT"
    user_repo.add.assert_called_once()

def test_create_user_already_exists(admin_service, user_repo):
    user_repo.get_by_username.return_value = Mock()
    
    with pytest.raises(ValueError, match="already exists"):
        admin_service.create_user("testuser", "password", "STUDENT")

def test_set_academic_year_success(admin_service, system_repo):
    system_repo.get.return_value = None
    
    admin_service.set_academic_year("2023-09-01", "2024-06-30")
    
    assert system_repo.add.call_count == 2  # Start and end dates

def test_set_academic_year_invalid_dates(admin_service):
    with pytest.raises(ValueError, match="End date must be after start date"):
        admin_service.set_academic_year("2024-06-30", "2023-09-01")

def test_get_current_academic_week(admin_service, system_repo):
    # Mock start date to be 2 weeks ago
    start_date = datetime.now() - timedelta(days=14)
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    config = Mock()
    config.value = start_date_str
    system_repo.get.return_value = config
    
    week, year = admin_service.get_current_academic_week()
    
    assert week == 3  # 14 days = 2 weeks passed, so we are in week 3
    assert year == datetime.now().year

def test_get_current_academic_week_before_start(admin_service, system_repo):
    # Mock start date to be in the future
    start_date = datetime.now() + timedelta(days=7)
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    config = Mock()
    config.value = start_date_str
    system_repo.get.return_value = config
    
    week, year = admin_service.get_current_academic_week()
    
    assert week == 1

def test_admin_service_no_system_repo(user_repo):
    service = AdminService(user_repo)
    
    with pytest.raises(ValueError, match="System repository not configured"):
        service.set_academic_year("2023-09-01", "2024-06-30")
        
    assert service.get_academic_year_config() is None
    
    week, year = service.get_current_academic_week()
    assert week == 1
    assert year == datetime.now().year

def test_get_current_academic_week_no_config(admin_service, system_repo):
    system_repo.get.return_value = None
    
    week, year = admin_service.get_current_academic_week()
    
    assert week == 1
    assert year == datetime.now().year

def test_save_config_update(admin_service, system_repo):
    # Mock existing config
    existing_config = Mock()
    system_repo.get.return_value = existing_config
    
    admin_service.set_academic_year("2023-09-01", "2024-06-30")
    
    # Should call update, not add
    system_repo.update.assert_called()
    # add is called 0 times because we are updating both start and end date
    # actually wait, set_academic_year calls _save_config twice.
    # if get returns a mock, it returns it for both calls.
    # so both calls will be updates.
    system_repo.add.assert_not_called()

def test_get_all_users(admin_service, user_repo):
    user_repo.list.return_value = ['user1', 'user2']
    users = admin_service.get_all_users()
    assert users == ['user1', 'user2']
    user_repo.list.assert_called_once()

def test_get_academic_year_config_success(admin_service, system_repo):
    mock_start = Mock()
    mock_start.value = '2023-09-01'
    mock_end = Mock()
    mock_end.value = '2024-06-30'
    
    def get_side_effect(key):
        if key == 'academic_year_start':
            return mock_start
        elif key == 'academic_year_end':
            return mock_end
        return None
        
    system_repo.get.side_effect = get_side_effect
    
    config = admin_service.get_academic_year_config()
    
    assert config['start_date'] == '2023-09-01'
    assert config['end_date'] == '2024-06-30'

def test_bulk_delete_users(admin_service, user_repo):
    user_ids = ['1', '2', '3']
    user_repo.delete.side_effect = [True, True, False] # 2 success, 1 fail
    
    result = admin_service.bulk_delete_users(user_ids)
    
    assert result['success'] == 2
    assert result['errors'] == 1
    assert user_repo.delete.call_count == 3
