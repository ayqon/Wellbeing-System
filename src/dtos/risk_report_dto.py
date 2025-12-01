from dataclasses import dataclass

@dataclass
class RiskReportDTO:
    risk_level: str
    grades: float
    reason: str
