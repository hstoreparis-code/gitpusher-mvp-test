"""
Unit tests for the Jobs module.

Tests the job state machine and ensures credits are only consumed on success.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from jobs import JobManager, JobStatus


@pytest.fixture
def mock_db():
    """Mock MongoDB database"""
    db = MagicMock()
    db.jobs_v1 = MagicMock()
    db.jobs_v1.insert_one = AsyncMock()
    db.jobs_v1.find_one = AsyncMock()
    db.jobs_v1.update_one = AsyncMock()
    db.jobs_v1.find = MagicMock()
    return db


@pytest.fixture
def mock_credits_service():
    """Mock CreditsService"""
    service = MagicMock()
    service.get_user_credits = AsyncMock(return_value=10)
    service.consume_credits = AsyncMock(return_value=True)
    return service


@pytest.fixture
def job_manager(mock_db, mock_credits_service):
    """Create JobManager instance with mocks"""
    return JobManager(mock_db, mock_credits_service)


@pytest.mark.asyncio
async def test_create_job_success(job_manager, mock_db, mock_credits_service):
    """Test successful job creation"""
    user_id = "user_123"
    job_data = {"upload_id": "upload_123", "repo_name": "test-repo"}
    
    job = await job_manager.create_job(
        user_id=user_id,
        job_type="upload",
        job_data=job_data,
        required_credits=1
    )
    
    # Verify credits were checked
    mock_credits_service.get_user_credits.assert_called_once_with(user_id)
    
    # Verify job was created with correct fields
    assert job["user_id"] == user_id
    assert job["type"] == "upload"
    assert job["status"] == JobStatus.PENDING
    assert job["required_credits"] == 1
    assert job["credits_charged"] is False
    assert job["upload_id"] == "upload_123"
    assert job["repo_name"] == "test-repo"
    
    # Verify job was inserted into DB
    mock_db.jobs_v1.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_create_job_insufficient_credits(job_manager, mock_credits_service):
    """Test job creation fails with insufficient credits"""
    mock_credits_service.get_user_credits = AsyncMock(return_value=0)
    
    with pytest.raises(ValueError, match="Insufficient credits"):
        await job_manager.create_job(
            user_id="user_123",
            job_type="upload",
            job_data={},
            required_credits=1
        )


@pytest.mark.asyncio
async def test_validate_job_success(job_manager, mock_db, mock_credits_service):
    """Test job validation"""
    job_id = "job_123"
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "user_id": "user_123",
        "status": JobStatus.PENDING,
        "required_credits": 1
    })
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.validate_job(job_id)
    
    assert result is True
    mock_credits_service.get_user_credits.assert_called_once()
    mock_db.jobs_v1.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_validate_job_insufficient_credits(job_manager, mock_db, mock_credits_service):
    """Test job validation fails with insufficient credits"""
    job_id = "job_123"
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "user_id": "user_123",
        "status": JobStatus.PENDING,
        "required_credits": 5
    })
    mock_credits_service.get_user_credits = AsyncMock(return_value=2)
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.validate_job(job_id)
    
    assert result is False
    # Should update job to failed status
    mock_db.jobs_v1.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_start_job(job_manager, mock_db):
    """Test starting a job"""
    job_id = "job_123"
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "status": JobStatus.VALIDATED
    })
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.start_job(job_id)
    
    assert result is True
    mock_db.jobs_v1.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_complete_job_success_consumes_credits(job_manager, mock_db, mock_credits_service):
    """Test completing job successfully consumes credits"""
    job_id = "job_123"
    user_id = "user_123"
    
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "user_id": user_id,
        "status": JobStatus.RUNNING,
        "required_credits": 2,
        "credits_charged": False
    })
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.complete_job(
        job_id=job_id,
        success=True,
        result_data={"repo_url": "https://github.com/user/repo"}
    )
    
    assert result is True
    
    # CRITICAL: Verify credits were consumed
    mock_credits_service.consume_credits.assert_called_once_with(user_id, 2)
    
    # Verify job was updated with success status and credits_charged flag
    update_call = mock_db.jobs_v1.update_one.call_args
    assert update_call[0][0] == {"_id": job_id}
    assert update_call[0][1]["$set"]["status"] == JobStatus.SUCCESS
    assert update_call[0][1]["$set"]["credits_charged"] is True
    assert "repo_url" in update_call[0][1]["$set"]


@pytest.mark.asyncio
async def test_complete_job_failure_no_credit_consumption(job_manager, mock_db, mock_credits_service):
    """Test completing job with failure does NOT consume credits"""
    job_id = "job_123"
    
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "user_id": "user_123",
        "status": JobStatus.RUNNING,
        "required_credits": 1,
        "credits_charged": False
    })
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.complete_job(
        job_id=job_id,
        success=False,
        error="Job execution failed"
    )
    
    assert result is True
    
    # CRITICAL: Verify credits were NOT consumed
    mock_credits_service.consume_credits.assert_not_called()
    
    # Verify job was updated with failed status
    update_call = mock_db.jobs_v1.update_one.call_args
    assert update_call[0][1]["$set"]["status"] == JobStatus.FAILED
    assert update_call[0][1]["$set"]["error"] == "Job execution failed"


@pytest.mark.asyncio
async def test_complete_job_idempotent(job_manager, mock_db, mock_credits_service):
    """Test completing a job twice doesn't double-charge credits"""
    job_id = "job_123"
    
    # First call: job not yet charged
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "user_id": "user_123",
        "status": JobStatus.SUCCESS,  # Already completed
        "required_credits": 1,
        "credits_charged": True
    })
    
    result = await job_manager.complete_job(
        job_id=job_id,
        success=True
    )
    
    assert result is False  # Already completed
    
    # CRITICAL: Credits should NOT be consumed again
    mock_credits_service.consume_credits.assert_not_called()


@pytest.mark.asyncio
async def test_complete_job_prevents_double_charging(job_manager, mock_db, mock_credits_service):
    """Test that credits_charged flag prevents double-charging"""
    job_id = "job_123"
    
    mock_db.jobs_v1.find_one = AsyncMock(return_value={
        "_id": job_id,
        "user_id": "user_123",
        "status": JobStatus.RUNNING,
        "required_credits": 1,
        "credits_charged": True  # Already charged
    })
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.complete_job(
        job_id=job_id,
        success=True
    )
    
    assert result is True
    
    # CRITICAL: Credits should NOT be consumed (already charged)
    mock_credits_service.consume_credits.assert_not_called()


@pytest.mark.asyncio
async def test_add_log(job_manager, mock_db):
    """Test adding a log entry to a job"""
    job_id = "job_123"
    mock_db.jobs_v1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    result = await job_manager.add_log(job_id, "Processing file...")
    
    assert result is True
    mock_db.jobs_v1.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_job(job_manager, mock_db):
    """Test getting a job by ID"""
    job_id = "job_123"
    expected_job = {"_id": job_id, "status": JobStatus.RUNNING}
    mock_db.jobs_v1.find_one = AsyncMock(return_value=expected_job)
    
    job = await job_manager.get_job(job_id)
    
    assert job == expected_job
    mock_db.jobs_v1.find_one.assert_called_once_with({"_id": job_id})


@pytest.mark.asyncio
async def test_list_user_jobs(job_manager, mock_db):
    """Test listing jobs for a user"""
    user_id = "user_123"
    expected_jobs = [
        {"_id": "job_1", "status": JobStatus.SUCCESS},
        {"_id": "job_2", "status": JobStatus.RUNNING}
    ]
    
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=expected_jobs)
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_db.jobs_v1.find = MagicMock(return_value=mock_cursor)
    
    jobs = await job_manager.list_user_jobs(user_id)
    
    assert jobs == expected_jobs
    mock_db.jobs_v1.find.assert_called_once_with({"user_id": user_id})
