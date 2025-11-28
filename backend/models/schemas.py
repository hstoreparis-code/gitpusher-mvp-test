from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class GitHubTokenRequest(BaseModel):
    githubToken: str

class GitHubTokenResponse(BaseModel):
    userId: str
    githubScopes: List[str]

# Upload Schemas
class UploadInitRequest(BaseModel):
    filename: str
    contentType: Optional[str] = "application/octet-stream"

class UploadInitResponse(BaseModel):
    uploadId: str
    presignedUrl: str
    expiresIn: int = 3600

class UploadStatus(BaseModel):
    uploadId: str
    status: str
    extractedFiles: Optional[List[str]] = []
    size: Optional[int] = 0

class UploadCompleteRequest(BaseModel):
    uploadId: str
    meta: Optional[Dict[str, Any]] = {}

# Job Schemas
class AutoPrompts(BaseModel):
    readme: bool = True
    gitignore: bool = True
    license: bool = True
    changelog: bool = True

class JobCreateRequest(BaseModel):
    uploadId: str
    repoName: str
    visibility: str = "public"
    autoPrompts: Optional[AutoPrompts] = AutoPrompts()

class JobCreateResponse(BaseModel):
    jobId: str
    startedAt: str

class JobStatus(BaseModel):
    jobId: str
    status: str
    logs: List[str] = []
    repoUrl: Optional[str] = None
    errors: Optional[List[Dict[str, str]]] = []

# Repo Schemas
class Repo(BaseModel):
    id: str
    name: str
    url: str
    private: bool
    createdAt: str

class RepoCreateRequest(BaseModel):
    repoName: str
    private: bool = False

class RepoCreateResponse(BaseModel):
    repoUrl: str
    repoId: str

# Billing Schemas
class BillingCreditsResponse(BaseModel):
    credits: int
    currency: str = "EUR"

class BillingPurchaseRequest(BaseModel):
    packId: str

class BillingPurchaseResponse(BaseModel):
    checkoutUrl: str
    sessionId: str

class BillingTransaction(BaseModel):
    id: str
    amount: int
    type: str
    credits: int
    createdAt: str

# Autopush Schemas
class AutopushSettings(BaseModel):
    enabled: bool = False
    frequency: str = "every_upload"
    autoCommitMessage: bool = True
    autoReadme: bool = True
    autoChangelog: bool = True

class AutopushLogItem(BaseModel):
    id: str
    repoName: str
    status: str
    triggeredAt: str
    commitId: Optional[str] = None

class AutopushTriggerRequest(BaseModel):
    uploadId: Optional[str] = None
    repoName: Optional[str] = None

# Partner Schemas
class PartnerRepoCreateRequest(BaseModel):
    partnerApiKey: str
    userIdentifier: str
    s3ArtifactUrl: str
    repoName: str
    visibility: str = "public"

# Webhook Schemas
class WebhookJobCompleted(BaseModel):
    jobId: str
    status: str
    repoUrl: Optional[str] = None
    summary: Optional[Dict[str, Any]] = {}

# Error Schema
class ErrorResponse(BaseModel):
    code: str
    message: str
