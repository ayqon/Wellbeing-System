from risk_engine import riskcalculator as rc

class WellbeingSurvey:
    class test_high_stress_risk_calculation:
        @staticmethod
        def is_critical():
            student = {
                'stress level': 5,
                'attendance': 100,
                'grades': 100
            }
            rc_instance = rc()  # create an instance
            risk_score, driver = rc_instance.calculate_risk(student)
            print(risk_score, driver)
            try:
                if risk_score <= 50:
                    raise ValueError(
                        f"Critical Error: risk_score must be > 50 to trigger HIGH_STRESS, got {risk_score}"
                    )
                if driver != "HIGH_STRESS":
                    raise ValueError(
                        f"Critical Error: driver must be 'HIGH_STRESS', got {driver}"
                    )
            except ValueError:
                print("Suggested Fix: Review the risk calculation logic for high stress scenarios.")    

    class test_disengagement_risk_calculation:
        @staticmethod
        def is_critical():
            student = {
                'stress level': 0.0,
                'attendance': 100,
                'grades': 100,
                'missed_surveys': 5
            }
            rc_instance = rc()
            risk_score, driver = rc_instance.calculate_risk(student)
            print(risk_score, driver)
            try:
                if risk_score <= 50:
                    raise ValueError(
                        f"Critical Error: risk_score must be > 50 to trigger DISENGAGEMENT, got {risk_score}"
                    )
                if driver != "DISENGAGEMENT":
                    raise ValueError(
                        f"Critical Error: driver must be 'DISENGAGEMENT', got {driver}"
                    )
            except ValueError:
                print("Suggested Fix: Review the risk calculation logic for disengagement scenarios.")   

    class test_silent_struggle_risk_calculation:
        @staticmethod
        def is_critical():
            student = {
                'stress level': 4.5,
                'grades': 80,
                'sleep_hours': 3
            }
            rc_instance = rc()
            risk_score, driver = rc_instance.calculate_risk(student)
            print(risk_score, driver)
            try:
                if risk_score <= 60:
                    raise ValueError(
                        f"Critical Error: risk_score must be > 60 to reflect SILENT_STRUGGLE, got {risk_score}"
                    )
            except ValueError:
                print("Suggested Fix: Review the risk calculation logic for silent struggle scenarios.")
                
    class ModuleGrade:
        def __init__(self, module_name, grade):
            self.module_name = module_name
            self.grade = grade

        def is_passing(self, threshold=50):
            return self.grade >= threshold


    class AttendanceRegister:
        def __init__(self):
            self.attendance_records = {}

        def record_attendance(self, student_id, date, present):
            if student_id not in self.attendance_records:
                self.attendance_records[student_id] = []
            self.attendance_records[student_id].append({'date': date, 'present': present})

        def get_attendance_percentage(self, student_id):
            if student_id not in self.attendance_records:
                return 0
            records = self.attendance_records[student_id]
            if not records:
                return 0
            present_count = sum(1 for record in records if record['present'])
            return (present_count / len(records)) * 100


# Run tests #
WellbeingSurvey.test_high_stress_risk_calculation.is_critical()
WellbeingSurvey.test_disengagement_risk_calculation.is_critical()
WellbeingSurvey.test_silent_struggle_risk_calculation.is_critical()



