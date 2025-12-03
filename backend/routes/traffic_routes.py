from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import asyncio
from datetime import datetime, timezone

router = APIRouter(prefix="/admin/traffic")

async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin
    return await require_admin(authorization)

@router.get("/stream")
async def traffic_stream(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    
    async def event_generator():
        from real_traffic_monitor import real_traffic_monitor
        
        while True:
            stats = real_traffic_monitor.get_realtime_stats()
            
            data = json.dumps({
                "t": int(datetime.now(timezone.utc).timestamp() * 1000),
                "rps": stats["rps"],
                "users": stats["active_users"],
                "response_ms": stats["avg_response_ms"]
            })
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/stats")
async def traffic_stats(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    from real_traffic_monitor import real_traffic_monitor
    return real_traffic_monitor.get_realtime_stats()
