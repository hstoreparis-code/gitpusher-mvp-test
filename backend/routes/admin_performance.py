from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Header

router = APIRouter(prefix="/admin/performance", tags=["admin-performance"])


async def require_admin_auth(authorization: Optional[str] = Header(None)):
  """Re-use central admin auth helper from server.py."""
  from server import require_admin

  return await require_admin(authorization)


@router.get("")
async def get_admin_performance(authorization: Optional[str] = Header(None)):
  """Mocked backend performance metrics for admin dashboards.

  Structure is designed to work for:
  - /admin/performance (détails)
  - /admin/mega (vue synthèse)
  """
  await require_admin_auth(authorization)

  now = datetime.now(timezone.utc)
  uptime_hours = 42.5

  # Mock latency / CPU / memory samples (0-100 scale for graphs)
  latency_samples = [32, 45, 40, 52, 47, 39, 60, 55, 43, 38]
  cpu_samples = [35, 48, 52, 46, 50, 41, 58, 62, 49, 44]
  memory_samples = [54, 57, 59, 63, 60, 58, 61, 64, 62, 59]

  return {
    "error": False,
    "uptime": f"{uptime_hours:.1f}h",
    "cpu": 48,
    "memory": 61,
    "queue_size": 3,
    "timestamp": now.isoformat(),
    "latency_samples": latency_samples,
    "cpu_samples": cpu_samples,
    "memory_samples": memory_samples,
  }
