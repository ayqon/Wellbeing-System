<<<<<<< HEAD
###OOP: Make weights constants/class attributes.
###Method: compute(metrics: StudentMetricsDTO) -> float
###OOP: Make weights constants
class riskcalculator:

    W_DISENGAGEMENT = 11
    W_STRESS = 11
    W_SLEEP = 1.3
    W_GRADES = 1.0
    W_ATTENDANCE = 0.5

    def __init__(self):
        pass


    def calculate_risk(self, student):
        # Placeholder implementation of risk calculation logic
        stress_level = student.get('stress level', 0)
        attendance = student.get('attendance', 100)
        grades = student.get('grades', 100)
        missed_surveys = student.get('missed_surveys', 0)
        sleep_hours = student.get('sleep_hours', 8)
        risk_score = 0
        driver = "NONE"
        # High Stress Scenario
        if stress_level >= 4.0:
            risk_score = stress_level * self.W_STRESS + attendance * self.W_ATTENDANCE # arbitrary weight
            driver = "HIGH_STRESS"
        # Consecutive Survey Misses Scenario
        if missed_surveys >= 5:
            risk_score = missed_surveys * self.W_DISENGAGEMENT  # arbitrary weight
            driver = "DISENGAGEMENT"
        # Silent Struggle Scenario
        if stress_level >= 4.0 and grades >= 80 and sleep_hours <= 4:
            risk_score = stress_level * self.W_STRESS + (100 - grades) * self.W_GRADES + (8 - sleep_hours) * self.W_SLEEP 
            driver = "SILENT_STRUGGLE"
        return risk_score, driver
    
    def compute(self, metrics):
        """
        Compute risk score from student metrics.
        
        Args:
            metrics: StudentMetricsDTO containing student data
            
        Returns:
            float: Risk score
        """
        driver = "NONE"
        risk_score, driver = self.calculate_risk(metrics)
        return risk_score, driver
    
        # ----------- Required by AnalyticsService -----------
    def calculate(self, students):
        """
        Accepts a list of anonymized students and returns
        correlation-style metric dicts (x,y,r) as required
        by AnalyticsService + integration test.
        """
        results = []
        for s in students:
            score, driver = self.calculate_risk(s)

            # For Director correlations view, return metrics
            # (these don't have to use your risk weights — placeholder output)
            results.append({
                "x": score,      # any numeric mapping acceptable
                "y": len(driver), 
                "r": score / 100 if score else 0,
                "name": None,
                "email": None,
                "student_id": None,
            })
        return results

    
=======
from dataclasses import dataclass

@dataclass
class StudentMetricsDTO:
    stress: int
    sleep: int
    misses: int
    grade: float

class RiskCalculator:
    """
    Service for calculating student risk scores.
    
    Formula: Risk = (Stress*20 + (100-Sleep*8) + Misses*10 + (100-Grade)) / 4
    """
    
    STRESS_WEIGHT = 20
    SLEEP_WEIGHT = 8
    MISSES_WEIGHT = 10
    
    def compute(self, metrics: StudentMetricsDTO) -> float:
        """
        Compute the risk score for a student based on their metrics.
        
        Args:
            metrics (StudentMetricsDTO): The student's metrics.
            
        Returns:
            float: The calculated risk score (0-100).
        """
        stress_component = metrics.stress * self.STRESS_WEIGHT
        sleep_component = 100 - (metrics.sleep * self.SLEEP_WEIGHT)
        misses_component = metrics.misses * self.MISSES_WEIGHT
        grade_component = 100 - metrics.grade
        
        # Ensure components are within reasonable bounds (0-100 approx)
        # Note: Sleep component can be negative if sleep > 12.5, but formula is as requested.
        
        total_risk = (stress_component + sleep_component + misses_component + grade_component) / 4
        
        return max(0.0, min(100.0, total_risk))
>>>>>>> 3a7964ac494425bc0b4b351b1539993b2dbe5c09
