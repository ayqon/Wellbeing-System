from src.core.database import Database
from src.repositories.user_repository import UserRepository
from src.repositories.student_repository import StudentRepository
from src.repositories.survey_repository import SurveyRepository
from src.services.auth_service import AuthService
from src.services.survey_service import SurveyService
from src.services.risk_engine import RiskCalculator
from src.models.user import User
from src.models.student import Student
from src.models.survey import WellbeingSurvey

class Container:
    """
    Dependency Injection Container.
    
    Responsible for initializing and wiring together the application's
    services and repositories.
    """
    
    def __init__(self):
        self.db = Database()
        self._user_repo = None
        self._student_repo = None
        self._survey_repo = None
        self._auth_service = None
        self._survey_service = None
        self._risk_calculator = None

    def user_repository(self) -> UserRepository:
        if not self._user_repo:
            self._user_repo = UserRepository(self.db.SessionLocal())
        return self._user_repo

    def student_repository(self) -> StudentRepository:
        if not self._student_repo:
            self._student_repo = StudentRepository(self.db.SessionLocal())
        return self._student_repo

    def survey_repository(self) -> SurveyRepository:
        if not self._survey_repo:
            self._survey_repo = SurveyRepository(self.db.SessionLocal())
        return self._survey_repo

    def auth_service(self) -> AuthService:
        if not self._auth_service:
            self._auth_service = AuthService(self.user_repository())
        return self._auth_service

    def survey_service(self) -> SurveyService:
        if not self._survey_service:
            self._survey_service = SurveyService(
                self.survey_repository(),
                self.student_repository()
            )
        return self._survey_service

    def risk_calculator(self) -> RiskCalculator:
        if not self._risk_calculator:
            self._risk_calculator = RiskCalculator()
        return self._risk_calculator

    def analytics_service(self):
        from src.services.analytics_service import AnalyticsService
        from src.utils.privacy import Anonymizer
        
        if not hasattr(self, '_analytics_service') or not self._analytics_service:
            self._analytics_service = AnalyticsService(
                self.risk_calculator(),
                Anonymizer(),
                self.student_repository(),
                self.survey_repository()
            )
        return self._analytics_service
    def import_service(self):
        from src.services.import_service import ImportService
        from src.services.user_csv_parser import UserCSVParser
        
        if not hasattr(self, '_import_service') or not self._import_service:
            self._import_service = ImportService(
                self.user_repository(),
                self.student_repository(),
                UserCSVParser()
            )
        return self._import_service

    def system_repository(self):
        from src.repositories.system_repository import SystemRepository
        if not hasattr(self, '_system_repo') or not self._system_repo:
            self._system_repo = SystemRepository(self.db.SessionLocal())
        return self._system_repo

    def admin_service(self):
        from src.services.admin_service import AdminService
        
        if not hasattr(self, '_admin_service') or not self._admin_service:
            self._admin_service = AdminService(
                self.user_repository(),
                self.system_repository()
            )
        return self._admin_service
