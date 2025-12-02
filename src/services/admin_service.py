from datetime import datetime, timedelta
from src.models.user import User
from src.models.system import SystemConfig

class AdminService:
    """
    Service for administrative operations.
    """
    def __init__(self, user_repository, system_repo=None):
        """
        Initialize the AdminService.
        
        Args:
            user_repository: Repository for User entity operations.
            system_repo: Repository for SystemConfig operations (optional).
        """
        self.user_repo = user_repository
        self.system_repo = system_repo

    def get_all_users(self):
        """Get all users."""
        return self.user_repo.list()

    def create_user(self, username, password, role, first_name=None, last_name=None):
        """Create a new user."""
        if self.user_repo.get_by_username(username):
            raise ValueError(f"User {username} already exists")
            
        user = User(
            username=username,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        self.user_repo.add(user)
        return user

    def hard_delete_user(self, user_id):
        """
        Hard delete a user and all associated data (GDPR compliance).
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        return self.user_repo.delete(user_id)

    def bulk_delete_users(self, user_ids):
        """
        Bulk delete multiple users.
        
        Args:
            user_ids: List of user IDs to delete.
            
        Returns:
            dict: {'success': int, 'errors': int}
        """
        success_count = 0
        error_count = 0
        
        for user_id in user_ids:
            try:
                if self.hard_delete_user(user_id):
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
                
        return {'success': success_count, 'errors': error_count}

    def set_academic_year(self, start_date_str, end_date_str):
        """Set academic year start and end dates."""
        if not self.system_repo:
            raise ValueError("System repository not configured")
            
        # Validate dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
            
        # Save config
        self._save_config('academic_year_start', start_date_str, "Start date of academic year")
        self._save_config('academic_year_end', end_date_str, "End date of academic year")
        
    def get_academic_year_config(self):
        """Get academic year configuration."""
        if not self.system_repo:
            return None
            
        start = self.system_repo.get('academic_year_start')
        end = self.system_repo.get('academic_year_end')
        
        return {
            'start_date': start.value if start else None,
            'end_date': end.value if end else None
        }
        
    def get_current_academic_week(self):
        """
        Calculate current academic week based on start date.
        Returns tuple (week_number, year).
        """
        if not self.system_repo:
            return 1, datetime.now().year
            
        start_config = self.system_repo.get('academic_year_start')
        if not start_config:
            return 1, datetime.now().year
            
        start_date = datetime.strptime(start_config.value, '%Y-%m-%d')
        now = datetime.now()
        
        if now < start_date:
            return 1, now.year
            
        # Calculate weeks difference
        delta = now - start_date
        week_num = (delta.days // 7) + 1
        
        return week_num, now.year

    def _save_config(self, key, value, description):
        """Helper to save config value."""
        config = self.system_repo.get(key)
        if config:
            config.value = value
            config.description = description
            self.system_repo.update(config)
        else:
            config = SystemConfig(key=key, value=value, description=description)
            self.system_repo.add(config)