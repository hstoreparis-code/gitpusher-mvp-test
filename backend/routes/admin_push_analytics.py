from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Header

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


async def require_admin_auth(authorization: Optional[str] = Header(None)):
  from server import require_admin

  return await require_admin(authorization)


@router.get("/pushes")
async def get_push_analytics(authorization: Optional[str] = Header(None)):
  """Mocked analytics for Git pushes and user activity.

  Designed to power:
  - /admin/mega (section Push Analytics & User Intelligence)
  """
  await require_admin_auth(authorization)

  now = datetime.now(timezone.utc)

  # Petite série pour les graphes de volume de pushes
  push_samples = [3, 6, 4, 9, 12, 8, 11, 7, 5, 10]

  providers = [
    {"name": "github", "count": 42},
    {"name": "gitlab", "count": 18},
    {"name": "bitbucket", "count": 7},
  ]

  countries = [
    {"country": "France", "count": 27},
    {"country": "USA", "count": 16},
    {"country": "Germany", "count": 9},
  ]

  users = [
    {"email": "founder@gitpusher.ai", "pushes": 23},
    {"email": "agency@example.com", "pushes": 14},
    {"email": "student@example.com", "pushes": 7},
  ]

  return {
    "generated_at": now.isoformat(),
    "total_pushes": sum(push_samples),
    "push_samples": push_samples,
    "providers": providers,
    "countries": countries,
    "users": users,
    "conversion": 38.5,
    "churn": 4.2,
  }
