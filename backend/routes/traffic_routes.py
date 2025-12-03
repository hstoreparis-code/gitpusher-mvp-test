from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import asyncio
import random
from datetime import datetime, timezone

router = APIRouter(prefix="/admin/traffic")

async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin
    return await require_admin(authorization)

@router.get("/stream")
async def traffic_stream(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    
    async def event_generator():
        while True:
            requests_per_sec = random.randint(0, 15)
            active_users = random.randint(1, 25)
            avg_response_ms = random.randint(50, 300)
            
            data = json.dumps({
                "t": int(datetime.now(timezone.utc).timestamp() * 1000),
                "rps": requests_per_sec,
                "users": active_users,
                "response_ms": avg_response_ms
            })
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/stats")
async def traffic_stats(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    from traffic_monitor import traffic_monitor
    return traffic_monitor.get_stats()
