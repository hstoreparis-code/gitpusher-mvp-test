from fastapi import APIRouter, Header
from typing import Optional
import os

router = APIRouter(prefix="/admin/features")

async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin
    return await require_admin(authorization)

@router.get("/health")
async def features_health(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    from server import db
    
    health = {}
    
    # Check Stripe
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        if stripe.api_key and stripe.api_key.startswith("sk_live_"):
            health["stripe"] = {"status": "ON", "mode": "LIVE"}
        else:
            health["stripe"] = {"status": "OFF", "issue": "No live key"}
    except:
        health["stripe"] = {"status": "OFF", "issue": "Import failed"}
    
    # Check Credits Workflow
    try:
        from jobs import JobManager
        health["credits_workflow"] = {"status": "ON", "issue": None}
    except:
        health["credits_workflow"] = {"status": "OFF", "issue": "JobManager import failed"}
    
    # Check AI Indexation
    from pathlib import Path
    ai_files = [
        Path("/app/frontend/public/.well-known/ai-actions.json"),
        Path("/app/backend/api/openapi.yaml")
    ]
    if all(f.exists() for f in ai_files):
        health["ai_indexation"] = {"status": "ON", "issue": None}
    else:
        health["ai_indexation"] = {"status": "OFF", "issue": "Missing files"}
    
    # Check MongoDB
    try:
        await db.users.find_one({})
        health["database"] = {"status": "ON", "issue": None}
    except:
        health["database"] = {"status": "OFF", "issue": "Connection failed"}
    
    # Check Email System
    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        health["email_system"] = {"status": "ON", "issue": None}
    else:
        health["email_system"] = {"status": "OFF", "issue": "SMTP not configured"}
    
    return {"health": health, "overall": "OK" if all(h["status"] == "ON" for h in health.values()) else "ISSUES"}

@router.post("/autofix")
async def autofix_features(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    
    fixes_applied = []
    
    # Auto-fix: Stripe
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not stripe_key or not stripe_key.startswith("sk_"):
        fixes_applied.append({"feature": "stripe", "action": "Cannot auto-fix - requires manual key setup", "fixed": False})
    else:
        fixes_applied.append({"feature": "stripe", "action": "Key present", "fixed": True})
    
    # Auto-fix: AI Indexation files
    from pathlib import Path
    ai_actions = Path("/app/frontend/public/.well-known/ai-actions.json")
    if not ai_actions.exists():
        try:
            ai_actions.parent.mkdir(parents=True, exist_ok=True)
            ai_actions.write_text('{"actions":[{"name":"gitpusher.push","path":"/api/push"}]}')
            fixes_applied.append({"feature": "ai_indexation", "action": "Created ai-actions.json", "fixed": True})
        except:
            fixes_applied.append({"feature": "ai_indexation", "action": "Failed to create file", "fixed": False})
    else:
        fixes_applied.append({"feature": "ai_indexation", "action": "Files OK", "fixed": True})
    
    # Auto-fix: Email templates
    from server import db
    from services.email_service import EmailService
    email_service = EmailService(db)
    welcome_tmpl = await email_service.get_template("welcome_email")
    if not welcome_tmpl:
        try:
            await email_service.create_or_update_template({
                "key": "welcome_email",
                "name": "Welcome",
                "subject": "Bienvenue !",
                "body_html": "<p>Bienvenue !</p>",
                "body_text": "Bienvenue !"
            }, "autofix")
            fixes_applied.append({"feature": "email_templates", "action": "Created welcome template", "fixed": True})
        except:
            fixes_applied.append({"feature": "email_templates", "action": "Failed to create", "fixed": False})
    else:
        fixes_applied.append({"feature": "email_templates", "action": "Template exists", "fixed": True})
    
    all_fixed = all(f["fixed"] for f in fixes_applied)
    
    return {
        "status": "FIXED" if all_fixed else "PARTIAL",
        "fixes_applied": fixes_applied,
        "recommendation": "All issues resolved" if all_fixed else "Manual intervention required for some features"
    }
