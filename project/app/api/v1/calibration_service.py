# project/app/api/v1/calibration_service.py

from fastapi import FastAPI, HTTPException
from project.app.api.v1.schemas import (
    CalibrationRequest,
    CalibrationResponse,
)
from project.app.ml.models.task_difficulty_model_v0 import (
    compute_task_difficulty,
)
from project.app.ml.stability.calibration_registry import (
    record_calibration,
)

MODEL_VERSION = "1.0.0"

app = FastAPI(
    title="HumanOS Calibration Service",
    version=MODEL_VERSION,
)


@app.post("/v1/calibrate", response_model=CalibrationResponse)
def calibrate_task(request: CalibrationRequest):

    try:
        # Inject model version explicitly
        result = compute_task_difficulty(
            {
                "task_id": request.task_id,
                "task_metadata": request.task_metadata,
                "aggregated_metrics": request.aggregated_metrics,
            }
        )

        # Ensure model_version is correct
        result["model_version"] = MODEL_VERSION

        # Record in registry (append-only)
        record_calibration(result)

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
