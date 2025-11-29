import pytest
from unittest.mock import Mock, MagicMock
from src.container import Container
from src.services.auth_service import AuthService
from src.services.survey_service import SurveyService
from src.services.risk_engine import RiskCalculator
from src.repositories.base import AbstractRepository

class TestContainer:
    def test_container_initialization(self):
        """Test that container initializes and sets up database"""
        container = Container()
        assert container.db is not None

    def test_user_repository_singleton(self):
        """Test that user_repository is created and is a singleton (or at least consistent)"""
        container = Container()
        repo1 = container.user_repository()
        repo2 = container.user_repository()
        
        assert repo1 is not None
        assert repo1 is repo2
        # Verify it implements the interface (duck typing or isinstance if we imported the concrete class)
        assert isinstance(repo1, AbstractRepository)

    def test_student_repository_singleton(self):
        """Test that student_repository is created and is a singleton"""
        container = Container()
        repo1 = container.student_repository()
        repo2 = container.student_repository()
        
        assert repo1 is not None
        assert repo1 is repo2
        assert isinstance(repo1, AbstractRepository)

    def test_survey_repository_singleton(self):
        """Test that survey_repository is created and is a singleton"""
        container = Container()
        repo1 = container.survey_repository()
        repo2 = container.survey_repository()
        
        assert repo1 is not None
        assert repo1 is repo2
        assert isinstance(repo1, AbstractRepository)

    def test_auth_service_injection(self):
        """Test that AuthService is created with injected UserRepository"""
        container = Container()
        auth_service = container.auth_service()
        
        assert isinstance(auth_service, AuthService)
        assert auth_service.user_repo is container.user_repository()

    def test_survey_service_injection(self):
        """Test that SurveyService is created with injected Repositories"""
        container = Container()
        survey_service = container.survey_service()
        
        assert isinstance(survey_service, SurveyService)
        assert survey_service.survey_repo is container.survey_repository()
        assert survey_service.student_repo is container.student_repository()

    def test_risk_calculator_singleton(self):
        """Test that RiskCalculator is created"""
        container = Container()
        calculator = container.risk_calculator()
        assert isinstance(calculator, RiskCalculator)
