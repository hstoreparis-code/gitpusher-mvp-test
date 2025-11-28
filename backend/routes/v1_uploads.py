from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional
from models.schemas import (
    UploadInitRequest, UploadInitResponse, UploadStatus,
    UploadCompleteRequest
)
from services.storage_service import StorageService
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/uploads", tags=["uploads"])
storage = StorageService()


@router.post("/init", response_model=UploadInitResponse)
async def init_upload(payload: UploadInitRequest, db=None, user_id: str = None):
    """
    Initialize upload and get presigned URL.
    """
    upload_id, presigned_url = await storage.init_upload(payload.filename, payload.contentType)
    
    # Store upload metadata in DB
    await db.uploads_v1.insert_one({
        "_id": upload_id,
        "user_id": user_id,
        "filename": payload.filename,
        "content_type": payload.contentType,
        "status": "initialized",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return UploadInitResponse(
        uploadId=upload_id,
        presignedUrl=presigned_url,
        expiresIn=3600
    )


@router.post("", response_model=UploadStatus)
async def upload_direct(file: UploadFile = File(...), db=None, user_id: str = None):
    """
    Direct upload endpoint (fallback).
    """
    upload_id = uuid.uuid4().hex
    
    # Read file content
    content = await file.read()
    
    # Save to storage
    result = await storage.save_upload(upload_id, content, file.filename)
    
    # Extract files if ZIP
    extracted_files = await storage.extract_files(upload_id, file.filename)
    
    # Store in DB
    await db.uploads_v1.insert_one({
        "_id": upload_id,
        "user_id": user_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "processed",
        "size": result["size"],
        "mime_type": result["mime_type"],
        "extracted_files": extracted_files,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return UploadStatus(
        uploadId=upload_id,
        status="processed",
        extractedFiles=extracted_files,
        size=result["size"]
    )


@router.get("/{upload_id}", response_model=UploadStatus)
async def get_upload_status(upload_id: str, db=None):
    """
    Get upload status.
    """
    upload = await db.uploads_v1.find_one({"_id": upload_id}, {"_id": 0})
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return UploadStatus(
        uploadId=upload_id,
        status=upload.get("status", "unknown"),
        extractedFiles=upload.get("extracted_files", []),
        size=upload.get("size", 0)
    )


@router.post("/complete")
async def complete_upload(payload: UploadCompleteRequest, db=None, user_id: str = None):
    """
    Signal upload completion and create analysis job.
    """
    upload = await db.uploads_v1.find_one({"_id": payload.uploadId, "user_id": user_id})
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Mark as completed
    await db.uploads_v1.update_one(
        {"_id": payload.uploadId},
        {"$set": {"status": "processed"}}
    )
    
    # Create a job (placeholder)
    job_id = str(uuid.uuid4())
    await db.jobs_v1.insert_one({
        "_id": job_id,
        "user_id": user_id,
        "upload_id": payload.uploadId,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"jobId": job_id}
