class AdminService:
    """
    Service for administrative operations.
    """
    def __init__(self, user_repository):
        """
        Initialize the AdminService.
        
        Args:
            user_repository: Repository for User entity operations.
        """
        self.user_repo = user_repository

    def hard_delete_user(self, user_id):
        """
        Hard delete a user and all associated data (GDPR compliance).
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        return self.user_repo.delete(user_id)
#