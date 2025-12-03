from fastapi import Request
from datetime import datetime, timezone
import asyncio
import random

traffic_queue = asyncio.Queue(maxsize=1000)

class TrafficMonitor:
    def __init__(self):
        self.recent_requests = []
        self.stats = {"total": 0, "by_endpoint": {}, "by_method": {}}
    
    async def log_request(self, method: str, path: str, status: int, duration_ms: float):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "path": path,
            "status": status,
            "duration_ms": duration_ms
        }
        self.recent_requests.append(event)
        self.recent_requests = self.recent_requests[-100:]
        self.stats["total"] += 1
        self.stats["by_endpoint"][path] = self.stats["by_endpoint"].get(path, 0) + 1
        self.stats["by_method"][method] = self.stats["by_method"].get(method, 0) + 1
        
        try:
            traffic_queue.put_nowait(event)
        except:
            pass
    
    def get_stats(self):
        return {
            "total_requests": self.stats["total"],
            "recent_requests": self.recent_requests[-50:],
            "by_endpoint": dict(sorted(self.stats["by_endpoint"].items(), key=lambda x: x[1], reverse=True)[:10]),
            "by_method": self.stats["by_method"]
        }

traffic_monitor = TrafficMonitor()
