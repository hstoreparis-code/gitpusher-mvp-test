"""
Canonical Job Management Module
================================
This module provides a robust state machine for job lifecycle management
with atomic credit consumption that only occurs on successful completion.

Job States:
- pending: Job created, awaiting validation
- validated: Job validated, ready to run (credits checked but not consumed)
- running: Job is currently executing
- success: Job completed successfully (credits consumed)
- failed: Job failed (credits NOT consumed)

Key Features:
- Atomic credit consumption (only on success)
- Idempotent operations (safe to retry)
- Transaction logging for audit trail
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    VALIDATED = "validated"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class JobManager:
    """
    Manages job lifecycle with robust credit handling.
    
    Credits are only consumed when a job successfully completes,
    preventing credit loss on failures.
    """
    
    def __init__(self, db, credits_service):
        self.db = db
        self.credits_service = credits_service
    
    async def create_job(
        self,
        user_id: str,
        job_type: str,
        job_data: Dict[str, Any],
        required_credits: int = 1
    ) -> Dict[str, Any]:
        """
        Create a new job and verify sufficient credits (but don't consume yet).
        
        Args:
            user_id: User ID
            job_type: Type of job (e.g., 'upload', 'autopush', 'partner')
            job_data: Job-specific data (upload_id, repo_name, etc.)
            required_credits: Credits required for this job
        
        Returns:
            Dict containing the created job
            
        Raises:
            ValueError: If user has insufficient credits
        """
        # Check if user has sufficient credits
        user_credits = await self.credits_service.get_user_credits(user_id)
        if user_credits < required_credits:
            raise ValueError(
                f"Insufficient credits. Required: {required_credits}, Available: {user_credits}"
            )
        
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        job = {
            "_id": job_id,
            "user_id": user_id,
            "type": job_type,
            "status": JobStatus.PENDING,
            "required_credits": required_credits,
            "credits_charged": False,  # Flag to prevent double-charging
            "logs": ["Job created"],
            "error": None,
            "created_at": now,
            "updated_at": now,
            **job_data  # Merge job-specific data
        }
        
        await self.db.jobs_v1.insert_one(job)
        
        logger.info(
            f"Job created: {job_id} for user {user_id}, "
            f"type={job_type}, required_credits={required_credits}"
        )
        
        return job
    
    async def validate_job(self, job_id: str) -> bool:
        """
        Validate job and transition to 'validated' state.
        Re-checks credits before marking as validated.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if validation successful
        """
        job = await self.db.jobs_v1.find_one({"_id": job_id})
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        if job["status"] != JobStatus.PENDING:
            logger.warning(f"Job {job_id} not in pending state: {job['status']}")
            return False
        
        # Re-check credits
        user_credits = await self.credits_service.get_user_credits(job["user_id"])
        required_credits = job.get("required_credits", 1)
        
        if user_credits < required_credits:
            await self._update_job_status(
                job_id,
                JobStatus.FAILED,
                error="Insufficient credits at validation time"
            )
            return False
        
        await self._update_job_status(job_id, JobStatus.VALIDATED)
        logger.info(f"Job validated: {job_id}")
        return True
    
    async def start_job(self, job_id: str) -> bool:
        """
        Transition job to 'running' state.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if transition successful
        """
        job = await self.db.jobs_v1.find_one({"_id": job_id})
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        # Allow starting from either pending or validated state
        if job["status"] not in [JobStatus.PENDING, JobStatus.VALIDATED]:
            logger.warning(f"Job {job_id} cannot start from state: {job['status']}")
            return False
        
        await self._update_job_status(job_id, JobStatus.RUNNING)
        logger.info(f"Job started: {job_id}")
        return True
    
    async def complete_job(
        self,
        job_id: str,
        success: bool,
        result_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Complete a job and consume credits ONLY if successful.
        
        This operation is atomic and idempotent:
        - Uses credits_charged flag to prevent double-charging
        - Only charges credits on first successful completion
        - Can be safely retried
        
        Args:
            job_id: Job ID
            success: Whether the job succeeded
            result_data: Optional result data (e.g., repo_url)
            error: Optional error message
            
        Returns:
            True if completion successful
        """
        job = await self.db.jobs_v1.find_one({"_id": job_id})
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        # Check if already completed
        if job["status"] in [JobStatus.SUCCESS, JobStatus.FAILED]:
            logger.warning(f"Job {job_id} already completed with status: {job['status']}")
            return False
        
        new_status = JobStatus.SUCCESS if success else JobStatus.FAILED
        update_data = {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if result_data:
            update_data.update(result_data)
        
        if error:
            update_data["error"] = error
        
        # CRITICAL: Only consume credits on success AND if not already charged
        if success and not job.get("credits_charged", False):
            required_credits = job.get("required_credits", 1)
            
            # Atomic credit consumption
            consumed = await self.credits_service.consume_credits(
                job["user_id"],
                required_credits
            )
            
            if not consumed:
                # This shouldn't happen (we validated earlier), but handle gracefully
                logger.error(
                    f"Failed to consume credits for job {job_id}. "
                    f"Marking job as failed."
                )
                update_data["status"] = JobStatus.FAILED
                update_data["error"] = "Failed to consume credits"
                await self.db.jobs_v1.update_one(
                    {"_id": job_id},
                    {"$set": update_data, "$push": {"logs": "Credit consumption failed"}}
                )
                return False
            
            # Mark credits as charged (idempotent flag)
            update_data["credits_charged"] = True
            
            logger.info(
                f"Credits consumed for job {job_id}: {required_credits} credits "
                f"for user {job['user_id']}"
            )
        
        # Update job
        await self.db.jobs_v1.update_one(
            {"_id": job_id},
            {
                "$set": update_data,
                "$push": {
                    "logs": f"Job completed: {'success' if success else 'failed'}"
                }
            }
        )
        
        logger.info(
            f"Job completed: {job_id}, status={new_status}, "
            f"credits_charged={update_data.get('credits_charged', False)}"
        )
        
        return True
    
    async def add_log(self, job_id: str, log_message: str) -> bool:
        """
        Add a log entry to the job.
        
        Args:
            job_id: Job ID
            log_message: Log message to add
            
        Returns:
            True if log added successfully
        """
        result = await self.db.jobs_v1.update_one(
            {"_id": job_id},
            {
                "$push": {"logs": log_message},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        return result.modified_count > 0
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job document or None if not found
        """
        return await self.db.jobs_v1.find_one({"_id": job_id})
    
    async def list_user_jobs(
        self,
        user_id: str,
        limit: int = 50,
        status: Optional[JobStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        List jobs for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of jobs to return
            status: Optional status filter
            
        Returns:
            List of job documents
        """
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = self.db.jobs_v1.find(query).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        error: Optional[str] = None
    ) -> bool:
        """
        Internal helper to update job status.
        
        Args:
            job_id: Job ID
            status: New status
            error: Optional error message
            
        Returns:
            True if update successful
        """
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if error:
            update_data["error"] = error
        
        result = await self.db.jobs_v1.update_one(
            {"_id": job_id},
            {
                "$set": update_data,
                "$push": {"logs": f"Status changed to: {status}"}
            }
        )
        
        return result.modified_count > 0
