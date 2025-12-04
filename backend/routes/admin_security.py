from fastapi import APIRouter
import os

from logging_config import LOG_FILE_SECURITY

router = APIRouter()


@router.get("/api/admin/security/logs")
async def get_security_logs(limit: int = 100):
    if not os.path.exists(LOG_FILE_SECURITY):
        return {"logs": []}
    with open(LOG_FILE_SECURITY, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    tail = lines[-limit:]
    return {"logs": tail}


@router.get("/api/admin/security/status")
async def security_status():
    exists = os.path.exists(LOG_FILE_SECURITY)
    return {"security_log_exists": exists}
