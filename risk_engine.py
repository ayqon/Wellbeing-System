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
    
#
    