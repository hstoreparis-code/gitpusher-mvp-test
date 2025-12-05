from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Header

router = APIRouter(prefix="/admin/stripe", tags=["admin-stripe"])


async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin

    return await require_admin(authorization)


@router.get("/health")
async def get_stripe_health(authorization: Optional[str] = Header(None)):
    """Minimal Stripe health endpoint used by the admin credits dashboard.

    - Vérifie si une clé STRIPE_SECRET_KEY est configurée
    - Vérifie si au moins une transaction réussie existe dans `transactions`
    """
    import os

    from server import db

    await require_admin_auth(authorization)

    secret = os.environ.get("STRIPE_SECRET_KEY", "")
    keys_ok = bool(secret and secret.startswith("sk_"))

    # Check if we have at least one successful transaction in DB
    has_live_tx = False
    last_invoice_date: Optional[str] = None

    try:
        cursor = db.transactions.find({"status": "succeeded"}).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(1)
        if docs:
            has_live_tx = True
            raw_date = docs[0].get("created_at")
            try:
                if isinstance(raw_date, str):
                    dt = datetime.fromisoformat(raw_date)
                else:
                    dt = raw_date
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                last_invoice_date = dt.date().isoformat()
            except Exception:  # noqa: BLE001
                last_invoice_date = None
    except Exception:  # noqa: BLE001
        has_live_tx = False

    return {
        "webhook_ok": has_live_tx,
        "keys_ok": keys_ok,
        "sync_ok": has_live_tx,
        "last_invoice": last_invoice_date,
    }
