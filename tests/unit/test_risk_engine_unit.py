import pytest
from src.services.risk_engine import RiskCalculator, StudentMetricsDTO

class TestRiskCalculator:
    def test_calculate_uses_cached_risk(self):
        calc = RiskCalculator()
        students = [{'cached_risk': 80.0}]
        results = calc.calculate(students)
        assert results[0]['risk_score'] == 80.0

    def test_calculate_computes_risk(self):
        calc = RiskCalculator()
        students = [{'stress': 1, 'sleep': 8, 'misses': 0, 'grade': 100}]
        # cached_risk missing or None
        results = calc.calculate(students)
        assert results[0]['risk_score'] >= 0

    def test_calculate_driver_high_stress(self):
        calc = RiskCalculator()
        students = [{'stress': 5, 'sleep': 8, 'misses': 0, 'grade': 100}]
        results = calc.calculate(students)
        assert results[0]['driver'] == "HIGH_STRESS"

    def test_calculate_driver_disengagement(self):
        calc = RiskCalculator()
        students = [{'stress': 1, 'sleep': 8, 'misses': 10, 'grade': 100}]
        results = calc.calculate(students)
        assert results[0]['driver'] == "DISENGAGEMENT"

    def test_calculate_driver_none(self):
        calc = RiskCalculator()
        students = [{'stress': 1, 'sleep': 8, 'misses': 0, 'grade': 100}]
        results = calc.calculate(students)
        assert results[0]['driver'] == "NONE"
