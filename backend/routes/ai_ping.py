from fastapi import APIRouter
import json, os, datetime

router = APIRouter()

LOG_PATH = "backend/logs/ai_ping_log.json"

def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r") as f:
            return json.load(f)
    except:
        return []


def save_log(data):
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)


@router.get("/ai/ping")
def ai_ping():
    log = load_log()
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "source": "internal-test",
    }
    log.append(entry)
    save_log(log)
    return {"ok": True, "ts": entry["ts"], "total": len(log)}
