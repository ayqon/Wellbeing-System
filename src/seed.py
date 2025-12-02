import random
from datetime import date, timedelta, datetime
from src.app import create_app
from src.models.base import BaseModel
from src.models.user import User
from src.models.student import Student
from src.models.academic import Course, Module, StudentModule, ModuleGrade, AttendanceRegister
from src.models.survey import WellbeingSurvey, SurveyStatus
from src.services.risk_engine import RiskCalculator, StudentMetricsDTO

def seed_db():
    app = create_app()
    
    with app.app_context():
        # Access the session from the container's db instance
        session = app.container.db.SessionLocal()
        try:
            # Reset DB
            print("Resetting database...")
            BaseModel.metadata.drop_all(session.get_bind())
            BaseModel.metadata.create_all(session.get_bind())
            
            print("Seeding database with algorithmic data...")
            # Password hashing is handled by User model
            default_pass = "password123"

            # --- 1. Users (Staff) ---
            users = []
            
            # Officer
            officer = User(username="officer1", role="OFFICER")
            officer.set_password(default_pass)
            users.append(officer)
            
            # Directors
            director1 = User(username="director1", role="DIRECTOR") # CS
            director1.set_password(default_pass)
            users.append(director1)
            
            director2 = User(username="director2", role="DIRECTOR") # ENG
            director2.set_password(default_pass)
            users.append(director2)
            
            # Module Leaders (10)
            leaders = []
            for i in range(1, 11):
                uid = f"leader{i}"
                leader = User(username=uid, role="STAFF")
                leader.set_password(default_pass)
                users.append(leader)
                leaders.append(leader) # Keep track for assignment

            session.add_all(users)
            session.commit() # Commit to get IDs

            # --- 2. Academic Structure ---
            # We need IDs for directors
            cs_course = Course(course_code="CS100", name="Computer Science", director_user_id=director1.id)
            eng_course = Course(course_code="ENG100", name="Engineering", director_user_id=director2.id)
            
            session.add(cs_course)
            session.add(eng_course)
            session.commit() # Get Course IDs
            
            modules = []
            # CS Modules (Leaders 1-5)
            for i in range(1, 6):
                leader = leaders[i-1]
                modules.append(Module(
                    module_code=f"CS10{i}", 
                    name=f"CS Module {i}",
                    course=cs_course,
                    leader_user_id=leader.id
                ))
                
            # ENG Modules (Leaders 6-10)
            for i in range(1, 6):
                leader = leaders[i+4]
                modules.append(Module(
                    module_code=f"ENG10{i}", 
                    name=f"ENG Module {i}",
                    course=eng_course,
                    leader_user_id=leader.id
                ))
            
            session.add_all(modules)
            session.commit() # Get Module IDs

            # --- 3. Students & Trends ---
            students = []
            
            # Profiles: 
            # 0-19: CS Students
            # 20-39: ENG Students
            
            for i in range(1, 41):
                uid = f"student{i}"
                course_code = "CS100" if i <= 20 else "ENG100"
                
                # Determine Profile
                if i % 4 == 0: profile = "B" # Disengaged
                elif i % 4 == 1: profile = "C" # Silent Struggle
                elif i % 4 == 2: profile = "D" # Critical
                else: profile = "A" # Healthy
                
                first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
                last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
                
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                
                # Create User
                user = User(
                    username=uid, 
                    role="STUDENT",
                    first_name=fname,
                    last_name=lname
                )
                user.set_password(default_pass)
                session.add(user)
                session.flush() # Get User ID
                
                # Create Student
                student = Student(
                    student_id=uid, 
                    user_id=user.id,
                    name=f"{fname} {lname}",
                    email=f"{uid}@example.com",
                    course_code=course_code
                )
                student.current_risk_score = 0.0
                session.add(student)
                
                # Store profile for data generation (temporary attribute)
                student._profile = profile 
                students.append(student)

            session.commit() # Get Student IDs

            # --- 4. Data Generation (10 Weeks) ---
            start_date = date.today() - timedelta(weeks=10)
            
            for week in range(1, 11):
                week_start = start_date + timedelta(weeks=week-1)
                
                for student in students:
                    profile = student._profile
                    
                    # -- Survey --
                    # Skip some surveys for Disengaged/Critical
                    if profile in ["B", "D"] and random.random() < 0.3:
                        # Skipped survey logic (if we want to record skipped status explicitly)
                        # For now, just don't create a record or create SKIPPED
                        # Let's create SKIPPED for explicit tracking if model supports it
                        survey = WellbeingSurvey(
                            student_id=student.student_id, # String ID
                            week=week,
                            year=2023,
                            status=SurveyStatus.SKIPPED,
                            is_critical=False
                        )
                        session.add(survey)
                        student.increment_misses()
                    else:
                        stress = 2 # Default Healthy
                        # Generate quarter-hour sleep values
                        sleep_hours = random.randint(7, 8)
                        sleep_quarters = random.choice([0.0, 0.25, 0.5, 0.75])
                        sleep = sleep_hours + sleep_quarters
                        
                        if profile == "C": # Silent Struggle
                            stress = random.randint(4, 5) # High Stress
                            sleep_hours = random.randint(4, 6)
                            sleep_quarters = random.choice([0.0, 0.25, 0.5, 0.75])
                            sleep = sleep_hours + sleep_quarters
                        elif profile == "D": # Critical
                            stress = 5 # Max Stress
                            sleep_hours = random.randint(3, 5)
                            sleep_quarters = random.choice([0.0, 0.25, 0.5, 0.75])
                            sleep = sleep_hours + sleep_quarters
                        elif profile == "B": # Disengaged
                            stress = random.randint(1, 3) 
                        
                        is_critical = stress >= 4
                        
                        survey = WellbeingSurvey(
                            student_id=student.student_id, # String ID
                            week=week,
                            year=2023,
                            stress=stress,
                            sleep=sleep,
                            status=SurveyStatus.COMPLETED,
                            is_critical=is_critical
                        )
                        session.add(survey)

                    # -- Attendance --
                    # Find modules for this student's course
                    course_modules = [m for m in modules if m.course.course_code == student.course_code]
                    active_modules = course_modules[:2] 
                    
                    for mod in active_modules:
                        status = "Present"
                        if profile == "B": # Disengaged
                             if random.random() < 0.6: status = "Absent" # High absenteeism
                        elif profile == "D": # Critical
                             if random.random() < 0.4: status = "Absent"
                        
                        att = AttendanceRegister(
                            student_id=student.id, # Integer ID
                            module_id=mod.id,      # Integer ID
                            date=datetime.combine(week_start, datetime.min.time()), 
                            status=status
                        )
                        session.add(att)

            # --- 5. Grades ---
            for student in students:
                profile = student._profile
                course_modules = [m for m in modules if m.course.course_code == student.course_code]
                
                for mod in course_modules:
                    grade_val = 70 # Default
                    
                    if profile == "A": grade_val = random.randint(65, 85)
                    elif profile == "B": grade_val = random.randint(30, 50) # Low grades
                    elif profile == "C": grade_val = random.randint(75, 95) # High grades
                    elif profile == "D": grade_val = random.randint(20, 45) # Low grades
                    
                    grade = ModuleGrade(
                        student_id=student.id, # Integer ID
                        module_id=mod.id,      # Integer ID
                        grade=grade_val,
                        is_final=True
                    )
                    session.add(grade)
                    
                    # Create Enrollment (StudentModule)
                    enrollment = StudentModule(
                        student=student,
                        module=mod,
                        semester="Fall 2023"
                    )
                    session.add(enrollment)
            
            session.commit()

            # --- 6. Calculate Risk ---
            print("Calculating risk scores...")
            calculator = RiskCalculator() # No weights needed in constructor

            for student in students:
                # Aggregate data
                # Stress (Last 3 weeks avg)
                # We need to query surveys for this student
                # Since we have the objects in session, we can try to access relationship if loaded
                # Or just query
                recent_surveys = session.query(WellbeingSurvey).filter(
                    WellbeingSurvey.student_id == student.student_id,
                    WellbeingSurvey.week >= 8,
                    WellbeingSurvey.status == SurveyStatus.COMPLETED
                ).all()
                
                avg_stress = sum([s.stress for s in recent_surveys]) / len(recent_surveys) if recent_surveys else 0
                avg_sleep = sum([s.sleep for s in recent_surveys]) / len(recent_surveys) if recent_surveys else 8
                
                # Misses (Total)
                # Query attendance
                misses = session.query(AttendanceRegister).filter(
                    AttendanceRegister.student_id == student.id,
                    AttendanceRegister.status == "Absent"
                ).count()
                
                # Grade (Avg)
                grades = session.query(ModuleGrade).filter(
                    ModuleGrade.student_id == student.id
                ).all()
                avg_grade = sum([g.grade for g in grades]) / len(grades) if grades else 0
                
                # Calculate
                metrics = StudentMetricsDTO(
                    stress=int(avg_stress),
                    sleep=int(avg_sleep),
                    misses=misses,
                    grade=avg_grade
                )
                
                risk_score = calculator.compute(metrics)
                student.current_risk_score = risk_score
                student.missed_surveys = misses # Using misses for attendance misses proxy as per original script logic?
                # Original script: student.consecutive_misses = misses
                # Our model: student.missed_surveys
                # Let's just update risk score.

            session.commit()
            print("Database seeded successfully!")
            print(f"- {len(users)} Users created")
            print(f"- {len(students)} Students")
            print(f"- {len(modules)} Modules")
            print("Profiles distributed: A (Healthy), B (Disengaged), C (Silent Struggle), D (Critical)")
        
        finally:
            session.close()

if __name__ == "__main__":
    seed_db()
