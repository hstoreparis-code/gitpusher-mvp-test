from datetime import datetime, timedelta, timezone
import uuid
from pydantic import BaseModel


class Session(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime

    @staticmethod
    def new(user_id: str, ttl_minutes: int = 60) -> "Session":
        now = datetime.now(timezone.utc)
        return Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
        )
