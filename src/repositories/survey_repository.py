from typing import Optional, List
from src.repositories.base import SqlAlchemyRepository
from src.models.survey import WellbeingSurvey
from sqlalchemy.orm import Session

class SurveyRepository(SqlAlchemyRepository[WellbeingSurvey]):
    def __init__(self, session: Session):
        super().__init__(session, WellbeingSurvey)

    def get_by_student_week(self, student_id: str, week: int, year: int) -> Optional[WellbeingSurvey]:
        return self.session.query(WellbeingSurvey).filter_by(
            student_id=student_id, week=week, year=year
        ).first()
    
    def get_by_student(self, student_id: str) -> List[WellbeingSurvey]:
        """
        Get all surveys for a specific student, ordered chronologically
        """
        return self.session.query(WellbeingSurvey).filter_by(
            student_id=student_id
        ).order_by(WellbeingSurvey.created_at).all()