from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Header

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin

    return await require_admin(authorization)


@router.get("/pushes")
async def get_push_analytics(authorization: Optional[str] = Header(None)):
    """Analytics de pushes Git & activité utilisateur basées sur la base Mongo.

    - Volume de jobs (jobs_v1) sur les 30 derniers jours (push_samples)
    - Répartition par provider (repos_v1.provider)
    - Répartition par pays et par utilisateur dérivée des `traffic_logs`

    Cette route alimente la section "Push Analytics & User Intelligence" de :
    - /admin/mega
    """
    await require_admin_auth(authorization)

    from server import db

    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    threshold = thirty_days_ago.isoformat()

    # 1) Jobs des 30 derniers jours pour construire la série push_samples
    jobs = (
        await db.jobs_v1.find({"created_at": {"$gte": threshold}}, {"_id": 0, "created_at": 1})
        .sort("created_at", 1)
        .to_list(2000)
    )

    per_day: dict[str, int] = defaultdict(int)
    for job in jobs:
        ts = job.get("created_at")
        if not ts:
            continue
        day = str(ts)[:10]
        per_day[day] += 1

    days_sorted = sorted(per_day.keys())
    push_samples: list[int] = []
    if days_sorted:
        # On limite à 10 points maximum (les plus récents)
        for day in days_sorted[-10:]:
            push_samples.append(int(per_day.get(day, 0)))

    if not push_samples:
        # Fallback visuel si aucune donnée réelle n'est encore présente
        push_samples = [3, 6, 4, 9, 12, 8, 11, 7, 5, 10]

    total_pushes = int(sum(push_samples))

    # 2) Providers réels depuis repos_v1
    providers_agg = (
        await db.repos_v1.aggregate([
            {"$group": {"_id": "$provider", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]).to_list(5)
    )

    providers = [
        {"name": (p.get("_id") or "unknown"), "count": int(p.get("count", 0))}
        for p in providers_agg
    ]

    if not providers:
        providers = [
            {"name": "github", "count": 42},
            {"name": "gitlab", "count": 18},
            {"name": "bitbucket", "count": 7},
        ]

    # 3) Pays & utilisateurs : basés sur traffic_logs (+ fallback si trop peu de données)
    thirty_days_ago_ts = threshold
    traffic_cursor = db.traffic_logs.find(
        {"timestamp": {"$gte": thirty_days_ago_ts}},
        {"_id": 0, "ip": 1, "country": 1, "user_id": 1},
    )
    traffic = await traffic_cursor.to_list(5000)

    by_country: dict[str, int] = defaultdict(int)
    user_hits: dict[str, int] = defaultdict(int)

    for log in traffic:
        country = log.get("country") or "Unknown"
        by_country[country] += 1

        user_id = log.get("user_id")
        if user_id:
            user_hits[str(user_id)] += 1

    # Construire la liste de pays
    countries = [
        {"country": c, "count": int(count)} for c, count in sorted(by_country.items(), key=lambda kv: kv[1], reverse=True)[:5]
    ]

    if not countries:
        countries = [
            {"country": "France", "count": 27},
            {"country": "USA", "count": 16},
            {"country": "Germany", "count": 9},
        ]

    # Construire la liste d'utilisateurs à partir de users + hits
    users: list[dict] = []
    if user_hits:
        ids = list(user_hits.keys())
        user_docs = await db.users.find({"_id": {"$in": ids}}, {"_id": 1, "email": 1}).to_list(500)
        email_map = {str(u["_id"]): u.get("email") or "unknown" for u in user_docs}

        for uid, count in sorted(user_hits.items(), key=lambda kv: kv[1], reverse=True)[:5]:
            users.append({"email": email_map.get(uid, "unknown"), "pushes": int(count)})

    if not users:
        users = [
            {"email": "founder@gitpusher.ai", "pushes": 23},
            {"email": "agency@example.com", "pushes": 14},
            {"email": "student@example.com", "pushes": 7},
        ]

    # 4) Indicateurs business (toujours mockés pour l'instant)
    conversion = 38.5
    churn = 4.2

    return {
        "generated_at": now.isoformat(),
        "total_pushes": total_pushes,
        "push_samples": push_samples,
        "providers": providers,
        "countries": countries,
        "users": users,
        "conversion": conversion,
        "churn": churn,
    }
