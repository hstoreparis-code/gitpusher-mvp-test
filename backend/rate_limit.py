import time
from typing import Dict, Tuple
import os

try:
    import redis
except ImportError:  # noqa: F401
    redis = None

RATE_LIMIT_WINDOW_SEC = 60
RATE_LIMIT_MAX_REQUESTS = 30

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SEC = 15 * 60

_REDIS_URL = os.getenv("REDIS_URL", "")
_redis_client = redis.from_url(_REDIS_URL) if (redis and _REDIS_URL) else None

# Fallback in-memory
_RATE_LIMIT_STORE: Dict[str, Tuple[int, float]] = {}
_LOCKOUT_STORE: Dict[str, float] = {}


def _now():
    return time.time()


def _get_rate_bucket(key: str):
    if _redis_client:
        data = _redis_client.get(key)
        if not data:
            return 0, _now()
        count, start = map(float, data.decode("utf-8").split(":"))
        return int(count), start
    return _RATE_LIMIT_STORE.get(key, (0, _now()))


def _set_rate_bucket(key: str, count: int, start: float, window_sec: int):
    if _redis_client:
        ttl = max(1, int(window_sec - (_now() - start)))
        _redis_client.setex(key, ttl, f"{count}:{start}")
    else:
        _RATE_LIMIT_STORE[key] = (count, start)


def check_rate_limit(key: str, max_requests: int = RATE_LIMIT_MAX_REQUESTS, window_sec: int = RATE_LIMIT_WINDOW_SEC):
    now = _now()
    count, start = _get_rate_bucket(key)
    if now - start > window_sec:
        _set_rate_bucket(key, 1, now, window_sec)
        return
    if count >= max_requests:
        raise Exception("rate_limited")
    _set_rate_bucket(key, count + 1, start, window_sec)


def record_login_failure(identity: str):
    now = _now()
    key = f"login:{identity}"
    count, start = _get_rate_bucket(key)
    if now - start > RATE_LIMIT_WINDOW_SEC:
        count = 0
        start = now
    count += 1
    _set_rate_bucket(key, count, start, RATE_LIMIT_WINDOW_SEC)
    if count >= LOGIN_MAX_ATTEMPTS:
        if _redis_client:
            _redis_client.setex(f"lockout:{identity}", LOGIN_LOCKOUT_SEC, "1")
        else:
            _LOCKOUT_STORE[identity] = now + LOGIN_LOCKOUT_SEC


def check_login_lockout(identity: str) -> bool:
    if _redis_client:
        exists = _redis_client.get(f"lockout:{identity}")
        return bool(exists)
    until = _LOCKOUT_STORE.get(identity)
    if not until:
        return False
    if _now() > until:
        _LOCKOUT_STORE.pop(identity, None)
        return False
    return True
