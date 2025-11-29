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
