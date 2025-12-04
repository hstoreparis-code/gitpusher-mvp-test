from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, Header, HTTPException

from security_config import is_secure_env

router = APIRouter()


DEFAULT_LEGAL_INFO: Dict[str, str] = {
    "editor": "[Nom ou raison sociale à renseigner]",
    "legalForm": "[Auto‑entrepreneur / SAS / SARL / …]",
    "address": "[Adresse complète à renseigner]",
    "siren": "[SIREN / SIRET à renseigner]",
    "vat": "[Numéro de TVA le cas échéant]",
    "director": "[Nom du responsable légal]",
    "contact": "[Adresse e‑mail de contact officielle]",
    "host": "[Nom de l'hébergeur, adresse, téléphone ou site web]",
}

DEFAULT_CGU: Dict[str, str] = {
    "service": "Texte de l'objet du service (CGU section 2.1)",
    "oauth": "Texte sur la création de compte et connexions OAuth (section 2.2)",
    "data": "Texte sur les données traitées (section 2.3)",
    "repos": "Texte sur l'accès à vos dépôts Git (section 2.4)",
    "responsibility": "Texte sur les responsabilités (section 2.5)",
    "security": "Texte sur la sécurité (section 2.6)",
    "retention": "Texte sur la conservation & suppression (section 2.7)",
    "changes": "Texte sur les modifications des conditions (section 2.8)",
}

DEFAULT_CONTACT = "Texte sur la politique de contact & réclamations (section 3)."


async def _get_db():
    # Import tardif pour éviter les boucles
    from server import db  # type: ignore

    return db


@router.get("/api/legal/terms")
async def get_public_terms():
    db = await _get_db()
    doc = await db.legal_terms.find_one({"id": "main"}, {"_id": 0})
    if not doc:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "id": "main",
            "legalInfo": DEFAULT_LEGAL_INFO,
            "cgu": DEFAULT_CGU,
            "contact": DEFAULT_CONTACT,
            "updated_at": now,
        }
    return doc


@router.post("/api/admin/legal/terms")
async def save_admin_terms(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(None),
):
    # Vérification admin via helper existant
    from server import require_admin  # type: ignore

    await require_admin(authorization)

    db = await _get_db()

    update_fields: Dict[str, Any] = {}
    for key in ("legalInfo", "cgu", "contact"):
        if key in body and body[key] is not None:
            update_fields[key] = body[key]

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.legal_terms.update_one(
        {"id": "main"},
        {"$set": update_fields, "$setOnInsert": {"id": "main"}},
        upsert=True,
    )

    doc = await db.legal_terms.find_one({"id": "main"}, {"_id": 0})
    return doc or {
        "id": "main",
        "legalInfo": DEFAULT_LEGAL_INFO,
        "cgu": DEFAULT_CGU,
        "contact": DEFAULT_CONTACT,
    }
