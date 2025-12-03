from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

router = APIRouter(prefix="/admin/smtp")

class SMTPConfig(BaseModel):
    smtp_host: str
    smtp_port: str
    smtp_user: str
    smtp_pass: str
    email_from: str

async def require_admin_auth(authorization: Optional[str] = Header(None)):
    from server import require_admin
    return await require_admin(authorization)

@router.get("/config")
async def get_smtp_config(authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    
    return {
        "smtp_host": os.environ.get("SMTP_HOST", ""),
        "smtp_port": os.environ.get("SMTP_PORT", "587"),
        "smtp_user": os.environ.get("SMTP_USER", ""),
        "smtp_pass": "***" if os.environ.get("SMTP_PASS") else "",
        "email_from": os.environ.get("EMAIL_FROM", "welcome@gitpusher.ai")
    }

@router.post("/config")
async def save_smtp_config(config: SMTPConfig, authorization: Optional[str] = Header(None)):
    await require_admin_auth(authorization)
    from server import db
    
    # Save to database
    await db.admin_settings.update_one(
        {"_id": "smtp_config"},
        {"$set": {
            "smtp_host": config.smtp_host,
            "smtp_port": config.smtp_port,
            "smtp_user": config.smtp_user,
            "smtp_pass": config.smtp_pass,
            "email_from": config.email_from,
            "updated_at": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip()
        }},
        upsert=True
    )
    
    # Update environment variables for current process
    os.environ["SMTP_HOST"] = config.smtp_host
    os.environ["SMTP_PORT"] = config.smtp_port
    os.environ["SMTP_USER"] = config.smtp_user
    os.environ["SMTP_PASS"] = config.smtp_pass
    os.environ["EMAIL_FROM"] = config.email_from
    
    return {"status": "saved", "message": "Configuration SMTP enregistrée. Redémarrez le backend pour appliquer."}
