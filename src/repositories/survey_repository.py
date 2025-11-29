from typing import Optional
from src.repositories.base import BaseRepository
from src.models.survey import WellbeingSurvey
from sqlalchemy.orm import Session

class SurveyRepository(BaseRepository[WellbeingSurvey]):
    def __init__(self, session: Session):
        super().__init__(session, WellbeingSurvey)

    def get_by_student_week(self, student_id: str, week: int, year: int) -> Optional[WellbeingSurvey]:
        return self.session.query(WellbeingSurvey).filter_by(
            student_id=student_id, week=week, year=year
        ).first()