from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from server import db, require_admin

router = APIRouter()


@router.get("/status", dependencies=[Depends(require_admin)])
async def credit_safety_status():
    """Simple credit safety status for admin.

    NOTE: This uses jobs_v1 and credits from users collection.
    It looks for inconsistencies between job status and credits_charged flag.
    """
    # Global credits: sum of all users credits (or adjust as needed)
    pipeline = [
        {"$group": {"_id": None, "total_credits": {"$sum": {"$ifNull": ["$credits", 0]}}}}
    ]
    agg = await db.users.aggregate(pipeline).to_list(1)
    total_credits = agg[0]["total_credits"] if agg else 0

    jobs: List[Dict[str, Any]] = await db.jobs_v1.find({}).to_list(200)

    total_jobs = len(jobs)
    success = len([j for j in jobs if j.get("status") == "success"])
    failed = len([j for j in jobs if j.get("status") == "failed"])
    pending = len([j for j in jobs if j.get("status") in {"pending", "validated", "running"}])

    anomalies: List[Dict[str, Any]] = []
    for job in jobs:
        status = job.get("status")
        credits_charged = job.get("credits_charged", False)
        logs = job.get("logs", [])

        # Crédit marqué comme chargé alors que le job n'est pas en succès
        if credits_charged and status != "success":
            anomalies.append({
                "job_id": job.get("_id"),
                "error": "CREDIT_CHARGED_WITHOUT_SUCCESS"
            })

        # Log de décrément mais pas de flag ou inversement
        if "credit_decremented_success" in logs and not credits_charged:
            anomalies.append({
                "job_id": job.get("_id"),
                "error": "LOG_SAYS_DECREMENT_BUT_FLAG_FALSE"
            })

    return {
        "credits_remaining_total": total_credits,
        "jobs": {
            "total": total_jobs,
            "success": success,
            "failed": failed,
            "pending": pending,
        },
        "anomalies": anomalies,
        "health": "OK" if len(anomalies) == 0 else "WARNING",
    }
