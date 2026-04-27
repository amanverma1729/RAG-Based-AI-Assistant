from fastapi import APIRouter, Depends
from app.api.dependencies import get_db
from app.services.evaluation import eval_logger

router = APIRouter()

@router.get("/metrics")
async def get_admin_metrics():
    """
    Returns aggregated Evaluation and latency metrics for the admin dashboard.
    """
    metrics = eval_logger.get_dashboard_metrics()
    return {"status": "success", "data": metrics}

@router.get("/traces")
async def get_raw_traces():
    """Returns raw evaluation traces for RAG pipeline."""
    return {"status": "success", "data": eval_logger.traces}
