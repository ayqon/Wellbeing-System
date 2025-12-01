import pytest
from src.services.risk_engine import RiskCalculator, StudentMetricsDTO

class TestRiskEngineLegacy:
    """
    Refactored tests from the original test_tracking_models.py.
    Now using standard pytest and the updated RiskCalculator interface.
    """

    def test_high_stress_risk_calculation(self):
        # student = {'stress level': 5, 'attendance': 100, 'grades': 100}
        # Mapping to DTO: stress=5, sleep=8 (default), misses=0 (default), grade=100
        metrics = StudentMetricsDTO(stress=5, sleep=8, misses=0, grade=100.0)
        
        rc = RiskCalculator()
        risk_score = rc.compute(metrics)
        
        # Formula: (5*20 + (100-8*8) + 0*10 + (100-100)) / 4
        # (100 + 36 + 0 + 0) / 4 = 136 / 4 = 34.0
        
        # WAIT! The original test expected > 50.
        # Original formula was: stress_level * W_STRESS + ...
        # New formula is: (Stress*20 + (100-Sleep*8) + Misses*10 + (100-Grade)) / 4
        
        # If stress is 5 (max), component is 100.
        # If sleep is 8 (good), component is 36.
        # If misses is 0, component is 0.
        # If grade is 100, component is 0.
        # Total = 136 / 4 = 34.
        
        # The new formula (Day 2 spec) produces different results than the legacy test expected.
        # However, I must adhere to the Day 2 spec implemented in RiskCalculator.
        # I will update the test expectations to match the approved formula.
        
        assert risk_score == 34.0

    def test_disengagement_risk_calculation(self):
        # student = {'missed_surveys': 5}
        metrics = StudentMetricsDTO(stress=0, sleep=8, misses=5, grade=100.0)
        
        rc = RiskCalculator()
        risk_score = rc.compute(metrics)
        
        # Formula: (0 + 36 + 50 + 0) / 4 = 86 / 4 = 21.5
        
        assert risk_score == 21.5

    def test_silent_struggle_risk_calculation(self):
        # student = {'stress level': 4.5, 'grades': 80, 'sleep_hours': 3}
        metrics = StudentMetricsDTO(stress=5, sleep=3, misses=0, grade=80.0) 
        # Note: stress was 4.5, but DTO expects int. Rounding to 5.
        
        rc = RiskCalculator()
        risk_score = rc.compute(metrics)
        
        # Formula: (100 + (100-24) + 0 + 20) / 4
        # (100 + 76 + 0 + 20) / 4 = 196 / 4 = 49.0
        
        assert risk_score == 49.0
