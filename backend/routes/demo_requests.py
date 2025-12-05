from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, EmailStr, Field


async def _get_db():  # lazy import to avoid circular import
    from server import db

    return db


async def _require_admin(authorization: str | None = Header(default=None)):
    from server import require_admin as core_require_admin

    # We don’t inject Request here to avoid FastAPI dependency issues; core_require_admin can handle None.
    return await core_require_admin(authorization, None)

router = APIRouter(prefix="/public", tags=["demo-requests-public"])
admin_router = APIRouter(prefix="/admin/demo-requests", tags=["demo-requests-admin"])


class DemoRequestCreate(BaseModel):
    name: str = Field(..., max_length=200)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=200)
    website: str = Field(..., max_length=300)
    role: Optional[str] = Field(None, max_length=120)
    team_size: Optional[str] = Field(None, max_length=50)
    use_case: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = Field(None, max_length=2000)


class DemoRequest(BaseModel):
    id: str
    created_at: str
    updated_at: str
    name: str
    email: EmailStr
    company: Optional[str] = None
    website: Optional[str] = None
    role: Optional[str] = None
    team_size: Optional[str] = None
    use_case: Optional[str] = None
    message: Optional[str] = None
    status: str = "new"


@router.post("/demo-request", response_model=DemoRequest)
async def create_demo_request(payload: DemoRequestCreate, db=Depends(_get_db)):
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": f"demo_{int(datetime.now(timezone.utc).timestamp())}",
        "created_at": now,
        "updated_at": now,
        "status": "new",
        **payload.model_dump(),
    }
    await db.demo_requests.insert_one(doc)
    # Ne jamais retourner _id mongo
    return DemoRequest(**{k: v for k, v in doc.items() if k != "_id"})


@admin_router.get("", response_model=List[DemoRequest])
async def list_demo_requests(db=Depends(_get_db), admin=Depends(_require_admin)):
    _ = admin
    docs = await db.demo_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return [DemoRequest(**doc) for doc in docs]
