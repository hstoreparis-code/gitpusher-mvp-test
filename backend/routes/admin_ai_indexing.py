from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Header

router = APIRouter(prefix="/admin/ai-indexing", tags=["admin-ai-indexing"])


async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin

    return await require_admin(authorization)


@router.get("")
async def get_admin_ai_indexing(authorization: Optional[str] = Header(None)):
    """AI indexing basée sur les vraies données de trafic IA.

    On réutilise `compute_ai_health` qui agrège `traffic_logs` et le score de
    visibilité AI. À partir des sources IA réellement détectées sur 7 jours,
    on déduit les drapeaux de couverture (ChatGPT, Claude, Gemini, etc.).
    """
    await require_admin_auth(authorization)

    from server import db
    from ai.health import compute_ai_health

    now = datetime.now(timezone.utc)

    health = await compute_ai_health(db)
    visibility = health.get("visibility") or {}
    ai_traffic = health.get("ai_traffic") or {}

    score = int(visibility.get("score", 0) or 0)
    top_sources = ai_traffic.get("top_ai_sources_7d") or []

    # Normaliser les noms de providers pour faciliter les tests
    names = set()
    for item in top_sources:
        raw = (item.get("_id") or "").lower()
        if raw:
            names.add(raw)

    def has_any(*keywords: str) -> bool:
        for n in names:
            for kw in keywords:
                if kw.lower() in n:
                    return True
        return False

    chatgpt = has_any("chatgpt", "openai")
    claude = has_any("claude")
    gemini = has_any("gemini", "google")
    mistral = has_any("mistral")
    perplexity = has_any("perplexity")

    qwen = has_any("qwen")
    kimi = has_any("kimi")
    ernie = has_any("ernie", "baidu")
    spark = has_any("spark")

    huggingface = has_any("huggingface")
    cursor = has_any("cursor")
    replit = has_any("replit")
    copilot = has_any("copilot")

    bing = has_any("bing", "microsoft", "copilot")
    ddg = has_any("duckduck", "ddg")
    arxiv = has_any("arxiv", "paper")

    missing_major = []
    if not chatgpt:
        missing_major.append("ChatGPT / OpenAI")
    if not claude:
        missing_major.append("Claude")
    if not gemini:
        missing_major.append("Google Gemini")
    if not mistral:
        missing_major.append("Mistral")
    if not perplexity:
        missing_major.append("Perplexity")

    if missing_major:
        autofix = (
            "Sources IA détectées mais certaines majors manquent encore : "
            + ", ".join(missing_major)
            + ". Analyse basée sur le trafic IA réel des 7 derniers jours."
        )
    else:
        autofix = "Couverture IA principale OK sur les 7 derniers jours (trafic IA réel)."

    return {
        "score": score,
        "autofix": autofix,
        # LLMs principaux
        "chatgpt": chatgpt,
        "claude": claude,
        "gemini": gemini,
        "mistral": mistral,
        "perplexity": perplexity,
        # Écosystème Asie / autres agents
        "qwen": qwen,
        "kimi": kimi,
        "ernie": ernie,
        "spark": spark,
        # Agents / outils dev
        "huggingface": huggingface,
        "cursor": cursor,
        "replit": replit,
        "copilot": copilot,
        # Search / meta crawlers
        "bing": bing,
        "ddg": ddg,
        "arxiv": arxiv,
        "updated_at": now.isoformat(),
        "raw_sources": top_sources,
    }
