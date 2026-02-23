# project/app/api/v1/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Tuple, Dict, Any


# -----------------------------
# Request Schema
# -----------------------------

class CalibrationRequest(BaseModel):
    task_id: str
    task_metadata: Dict[str, Any]
    aggregated_metrics: Dict[str, Any]


# -----------------------------
# Response Schema
# -----------------------------

class CalibrationResponse(BaseModel):
    task_id: str
    model_version: str
    declared_difficulty: Optional[float]
    empirical_difficulty: Optional[float]
    difficulty_delta: Optional[float]

    confidence: Optional[float]
    confidence_interval_95: Optional[Tuple[float, float]]
    confidence_level: Optional[str]

    calibration_flag: Optional[str]

    drift: Optional[Dict[str, Any]]
