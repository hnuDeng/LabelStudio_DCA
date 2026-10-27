from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import hmac
import hashlib
import json
import logging
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

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

LABEL_STUDIO_WEBHOOK_SECRET = os.environ.get("LABEL_STUDIO_WEBHOOK_SECRET", "")

# In-memory instances for demonstration (in production, they'd use a real DB)
al_api = ActiveLearningAPI()
drift_api = DriftDetectionAPI()
dq_api = DataQualityAPI()
anomaly_engine = AnomalyDetectionEngine(project_id=1)

def verify_webhook_token(authorization: Optional[str] = Header(None)):
    """Authenticate the static Bearer header configured in Label Studio."""
    if not LABEL_STUDIO_WEBHOOK_SECRET:
        if os.environ.get("LABEL_STUDIO_ALLOW_UNSIGNED_WEBHOOKS", "false").lower() == "true":
            return True
        raise HTTPException(status_code=503, detail="Webhook authentication is not configured")

    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not hmac.compare_digest(
        token.encode("utf-8"), LABEL_STUDIO_WEBHOOK_SECRET.encode("utf-8")
    ):
        raise HTTPException(status_code=403, detail="Invalid webhook token")
    return True

class WebhookPayload(BaseModel):
    action: str
    project: Dict[str, Any]
    task: Optional[Dict[str, Any]] = None
    annotation: Optional[Dict[str, Any]] = None

def has_annotation_value(value):
    if isinstance(value, dict):
        return any(has_annotation_value(item) for item in value.values())
    if isinstance(value, list):
        return any(has_annotation_value(item) for item in value)
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None and isinstance(value, (bool, int, float))

@app.post("/api/webhooks/label-studio")
async def label_studio_webhook(payload: WebhookPayload, verified: bool = Depends(verify_webhook_token)):
    from backend.database import SessionLocal, DBWebhookQualityEvent

    action = payload.action
    if action not in ("ANNOTATION_CREATED", "ANNOTATION_UPDATED"):
        return {"status": "unsupported", "action": action}
    project_id = payload.project.get("id")
    if not isinstance(project_id, int) or isinstance(project_id, bool) or project_id <= 0:
        return JSONResponse(status_code=422, content={"status": "invalid", "action": action})
    if not payload.task or not payload.annotation or payload.annotation.get("result") == []:
        return JSONResponse(status_code=422, content={"status": "insufficient_data", "action": action})
    task_id, annotation_id = payload.task.get("id"), payload.annotation.get("id")
    result = payload.annotation.get("result")
    task_project = payload.task.get("project")
    if isinstance(task_project, dict):
        task_project = task_project.get("id")
    annotation_project = payload.annotation.get("project")
    if isinstance(annotation_project, dict):
        annotation_project = annotation_project.get("id")
    annotation_task = payload.annotation.get("task")
    if (not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0
            or not isinstance(annotation_id, int) or isinstance(annotation_id, bool) or annotation_id <= 0
            or ("project" in payload.task and (not isinstance(task_project, int)
                or isinstance(task_project, bool) or task_project != project_id))
            or ("project" in payload.annotation and (not isinstance(annotation_project, int)
                or isinstance(annotation_project, bool) or annotation_project != project_id))
            or not isinstance(result, list) or not result
            or not all(isinstance(item, dict) and isinstance(item.get("value"), dict)
                and has_annotation_value(item["value"]) for item in result)
            or ("task" in payload.annotation and (not isinstance(annotation_task, int)
                or isinstance(annotation_task, bool) or annotation_task <= 0 or annotation_task != task_id))):
        return JSONResponse(status_code=422, content={"status": "invalid", "action": action})
    event_hash = hashlib.sha256(json.dumps({"action": action, "project": payload.project,
        "task": payload.task, "annotation": payload.annotation}, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    try:
        with SessionLocal() as db:
            existing = db.get(DBWebhookQualityEvent, event_hash)
            if existing:
                return {"status": "duplicate", "action": action, "report_id": existing.report_id}
        annotation = dict(payload.annotation, task_id=task_id)
        report = dq_api.run_assessment(project_id, [payload.task], [annotation],
            assessors=["completeness"], event_hash=event_hash)
    except IntegrityError:
        try:
            with SessionLocal() as db:
                existing = db.get(DBWebhookQualityEvent, event_hash)
                if existing:
                    return {"status": "duplicate", "action": action, "report_id": existing.report_id}
        except Exception:
            logging.exception("Could not check for duplicate event")
        logging.exception("Could not persist quality report")
        return JSONResponse(status_code=500, content={"status": "failed", "action": action})
    except Exception:
        logging.exception("Could not assess webhook event")
        return JSONResponse(status_code=500, content={"status": "failed", "action": action})
    return {"status": "processed", "action": action, "report_id": report.id}

@app.get("/api/projects/{project_id}/quality-report")
def project_quality_report(project_id: int):
    from backend.database import SessionLocal, DBQualityReport, DBWebhookQualityEvent
    with SessionLocal() as db:
        row = (db.query(DBQualityReport, DBWebhookQualityEvent)
            .join(DBWebhookQualityEvent, DBWebhookQualityEvent.report_id == DBQualityReport.id)
            .filter(DBWebhookQualityEvent.project_id == project_id, DBQualityReport.project_id == project_id)
            .order_by(DBQualityReport.id.desc()).first())
        if row is None:
            return {"project_id": project_id, "has_data": False}
        report, event = row
        return {"project_id": project_id, "has_data": True, "report_id": report.id,
            "completeness_score": report.completeness_score, "tasks_analyzed": event.tasks_analyzed,
            "annotations_analyzed": event.annotations_analyzed, "created_at": report.created_at.isoformat()}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "DCA Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
