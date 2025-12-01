from fastapi import APIRouter, Header, HTTPException
from typing import List, Dict, Any, Optional

router = APIRouter()

# Import tardif pour éviter l'import circulaire
def get_db_and_auth():
    from server import db, require_admin
    return db, require_admin

db = None
require_admin = None


@router.get("/status")
async def credit_safety_status(authorization: Optional[str] = Header(default=None)):
    """Simple credit safety status for admin.

    NOTE: This uses jobs_v1 and credits from users collection.
    It looks for inconsistencies between job status and credits_charged flag.
    """
    global db, require_admin
    if db is None:
        db, require_admin = get_db_and_auth()
    
    # Verify admin
    await require_admin(authorization)
    
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


@router.post("/test-workflow", dependencies=[Depends(require_admin)])
async def credit_safety_test_workflow():
    """Create a synthetic job and simulate full workflow for periodic tests.

    This does NOT call external providers. It only exercises the credit/job pipeline
    using an internal test user and a dummy job in jobs_v1.
    """
    from datetime import datetime, timezone
    import uuid

    # Create or reuse a dedicated test admin user with credits
    test_user = await db.users.find_one({"email": "credit-monitor@test.gitpusher"})
    if not test_user:
        now = datetime.now(timezone.utc).isoformat()
        test_user = {
            "_id": uuid.uuid4().hex,
            "email": "credit-monitor@test.gitpusher",
            "credits": 10,
            "is_admin": True,
            "created_at": now,
            "updated_at": now,
        }
        await db.users.insert_one(test_user)

    user_id = test_user["_id"]

    # Synthetic job document
    job_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    job_doc = {
        "_id": job_id,
        "user_id": user_id,
        "status": "pending",
        "required_credits": 1,
        "credits_charged": False,
        "logs": ["test_workflow_created"],
        "created_at": now,
        "updated_at": now,
    }
    await db.jobs_v1.insert_one(job_doc)

    # Simulate the full status transitions without real push
    await db.jobs_v1.update_one({"_id": job_id}, {"$set": {"status": "validated"}, "$push": {"logs": "test_validated"}})
    await db.jobs_v1.update_one({"_id": job_id}, {"$set": {"status": "running"}, "$push": {"logs": "test_running"}})
    await db.jobs_v1.update_one({"_id": job_id}, {"$set": {"status": "success", "credits_charged": True}, "$push": {"logs": "credit_decremented_success"}})

    return {"status": "ok", "test_job_id": job_id}

