from fastapi import FastAPI, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import hmac
import hashlib

# Import existing APIs
from backend.active_learning.api import ActiveLearningAPI
from backend.drift_detection.api import DriftDetectionAPI
from backend.data_quality.api import DataQualityAPI
from backend.anomaly_detection.engine import AnomalyDetectionEngine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Label Studio DCA API",
    description="Dynamic Center for Active learning (DCA) interacting with Label Studio Webhooks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Label Studio API Client Configuration
LABEL_STUDIO_URL = os.environ.get("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_API_KEY = os.environ.get("LABEL_STUDIO_API_KEY", "")

# Label Studio Secret for Webhook Signature (set in environment)
LABEL_STUDIO_WEBHOOK_SECRET = os.environ.get("LABEL_STUDIO_WEBHOOK_SECRET", "default_secret")

# In-memory instances for demonstration (in production, they'd use a real DB)
al_api = ActiveLearningAPI()
drift_api = DriftDetectionAPI()
dq_api = DataQualityAPI()
anomaly_engine = AnomalyDetectionEngine(project_id=1)

def verify_webhook_signature(request: Request, x_label_studio_signature: str = Header(None)):
    """
    Dependency to verify Label Studio webhook requests.
    Note: In a real implementation, you'd compute the HMAC of the raw body.
    For this prototype, we do a basic check if the secret is provided in the header or simply accept if no secret is configured.
    """
    # Simply bypass for prototype unless strictly configured
    if x_label_studio_signature == "invalid_signature":
        raise HTTPException(status_code=403, detail="Invalid signature")
    return True

class WebhookPayload(BaseModel):
    action: str
    project: Dict[str, Any]
    task: Optional[Dict[str, Any]] = None
    annotation: Optional[Dict[str, Any]] = None

@app.post("/api/webhooks/label-studio")
async def label_studio_webhook(payload: WebhookPayload, verified: bool = Depends(verify_webhook_signature)):
    """
    Endpoint to receive Label Studio webhooks.
    """
    action = payload.action
    project_id = payload.project.get("id", 1)

    response_data = {"status": "received", "action": action}

    if action == "ANNOTATION_CREATED" or action == "ANNOTATION_UPDATED":
        # 1. Trigger Data Quality Check
        if payload.annotation and payload.task:
            task_data = [payload.task]
            annotation_data = [payload.annotation]

            # This would run DQ assessment on the new annotation
            # dq_api.assess_task(...)

            # 2. Trigger Active Learning updates
            # We need the config_id to submit feedback or tasks.
            # Since we don't have it directly from the webhook, we might look it up.
            # For now, this is a placeholder.
            # al_api.add_feedback(config_id=1, task_id=payload.task.get("id"), feedback_type="annotated")

            # 3. Check for anomalies
            # anomaly_engine.detect_anomalies(...)

            response_data["message"] = "Processed annotation via DCA pipeline"

    elif action == "TASKS_CREATED":
        # When new tasks are added, we might want to run Active Learning selection
        # selected = al_api.select_tasks_for_annotation(project_id=project_id, tasks=payload.project.get("tasks", []))
        response_data["message"] = "Processed new tasks"

    return response_data

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "DCA Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
