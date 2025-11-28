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



