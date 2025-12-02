from src.app import create_app
import traceback

def debug_direct():
    app = create_app()
    with app.app_context():
        try:
            print("Initializing services...")
            # Access services via container
            analytics_service = app.container.analytics_service()
            
            print("Calling get_director_view('director1')...")
            # Assuming get_director_view takes user_id or similar
            # In prototype, it might be get_academic_list(director_id)
            # Let's check AnalyticsService signature if possible, or assume based on usage
            # Based on previous files, it seems to be get_director_view(director_id)
            
            # We need to find director1's ID first
            user_repo = app.container.user_repository()
            director = user_repo.get_by_username("director1")
            
            if not director:
                print("Director1 not found. Did you seed the DB?")
                return

            # get_director_view takes course_id, not user_id directly in the service signature I saw earlier?
            # Let's check the service signature again.
            # It was get_director_view(self, course_id)
            # So we need to find the course for the director.
            
            # course_repo line removed as it was malformed and unused 
            # Wait, I can't easily access course repo from here without container support or direct DB
            # Let's just query DB directly for course ID
            
            from src.models.academic import Course
            session = app.container.db.SessionLocal()
            course = session.query(Course).filter_by(director_user_id=director.id).first()
            session.close()
            
            if not course:
                 print("Course not found for director.")
                 return

            results = analytics_service.get_director_view(course.course_code)
            print(f"Success! Got {len(results)} results.")
            if results:
                print(results[:1])
            
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    debug_direct()
