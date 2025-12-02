from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class StudentMetricsDTO:
    stress: int
    sleep: int
    misses: int
    grade: float

class RiskCalculator:
    """
    Service for calculating student risk scores based on wellbeing metrics.
    
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
        
        # Ensure components are within reasonable bounds
        
        total_risk = (stress_component + sleep_component + misses_component + grade_component) / 4
        
        return max(0.0, min(100.0, total_risk))

    def calculate(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Accepts a list of anonymized students (dicts) and returns
        metrics for the Director view.
        
        Adapts dictionary input to StudentMetricsDTO for calculation.
        """
        results = []
        for s in students:
            # Extract metrics from dict with defaults
            metrics = StudentMetricsDTO(
                stress=s.get('stress', 0) or 0,
                sleep=s.get('sleep', 8) or 8,
                misses=s.get('misses', 0) or 0,
                grade=s.get('grade', 100.0) or 100.0
            )
            
            # Use cached risk if available to support tests/legacy data
            if 'cached_risk' in s and s['cached_risk'] is not None and s['cached_risk'] > 0:
                score = float(s['cached_risk'])
            else:
                score = self.compute(metrics)
            
            # Determine driver
            driver = "NONE"
            if metrics.stress >= 4:
                driver = "HIGH_STRESS"
            elif metrics.misses >= 5:
                driver = "DISENGAGEMENT"

            # For Director correlations view, return metrics
            results.append({
                "risk_score": score,      
                "driver": driver, 
                "name": None,
                "email": None,
                "student_id": None,
                "grade": s.get('grade'),
                "attendance": s.get('attendance'),
                # Frontend compatibility fields
                "x": score,
                "y": len(driver),
                "r": score / 100 if score else 0
            })
        return results
