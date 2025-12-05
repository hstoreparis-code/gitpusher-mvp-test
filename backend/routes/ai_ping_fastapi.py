from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Request

router = APIRouter()

LOG_PATH = Path("/app/logs/ai_ping_log.json")


@router.get("/ai/ping")
async def ai_ping(request: Request) -> Dict[str, Any]:
    """Lightweight AI ping endpoint for production (FastAPI).

    - Logs timestamp, IP, and user agent into /app/logs/ai_ping_log.json
    - Keeps a simple JSON array structure for compatibility with analyzers
    """
    now = datetime.now(timezone.utc).isoformat()

    try:
        if LOG_PATH.exists():
            raw = LOG_PATH.read_text(encoding="utf-8") or "[]"
            data = json.loads(raw)
            if not isinstance(data, list):
                data = []
        else:
            data = []
    except Exception:
        data = []

    entry = {
        "timestamp": now,
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", ""),
    }
    data.append(entry)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"ok": True, "ts": now, "total": len(data)}
