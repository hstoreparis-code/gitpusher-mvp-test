from fastapi import APIRouter

from seo.monitor import get_seo_overview

router = APIRouter()


@router.get("/seo/monitor")
async def seo_monitor():
    """Lightweight SEO monitor endpoint.

    Structure prête pour être reliée à Google Search Console plus tard.
    Pour l'instant, renvoie des valeurs neutres mais un payload complet
    pour alimenter le dashboard frontend.
    """
    from server import db  # import local pour éviter les cycles

    return await get_seo_overview(db)
