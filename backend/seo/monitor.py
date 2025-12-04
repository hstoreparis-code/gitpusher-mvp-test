from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


async def get_seo_overview(db) -> Dict[str, Any]:
    """Return a lightweight SEO overview payload.

    This is designed to be plugged into Google Search Console later.
    For l'instant, on renvoie une structure propre avec des valeurs neutres,
    pour alimenter le dashboard frontend sans dépendre d'une intégration externe.
    """
    now = datetime.now(timezone.utc)
    start_28d = (now - timedelta(days=28)).date().isoformat()
    today = now.date().isoformat()

    # Placeholder summary (zéro = pas encore connecté à GSC)
    summary = {
        "start_date": start_28d,
        "end_date": today,
        "total_clicks_28d": 0,
        "total_impressions_28d": 0,
        "avg_ctr": 0.0,
        "avg_position": 0.0,
    }

    # Placeholder by_page / by_country / by_device
    by_page: List[Dict[str, Any]] = []
    by_country: List[Dict[str, Any]] = []
    by_device: List[Dict[str, Any]] = []

    # Petite série temporelle neutre (permet d'afficher un graphe même sans GSC)
    timeseries: List[Dict[str, Any]] = []
    for i in range(28):
        day = (now - timedelta(days=27 - i)).date().isoformat()
        timeseries.append({
            "date": day,
            "clicks": 0,
            "impressions": 0,
            "ctr": 0.0,
            "position": 0.0,
        })

    return {
        "search_console_connected": False,
        "summary": summary,
        "timeseries": timeseries,
        "by_page": by_page,
        "by_country": by_country,
        "by_device": by_device,
    }
