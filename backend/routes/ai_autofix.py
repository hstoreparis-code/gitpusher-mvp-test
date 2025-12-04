from fastapi import APIRouter
from fastapi.responses import JSONResponse

from autofix.ai_autofix import run_autofix

router = APIRouter()


@router.post("/admin/ai-autofix")
async def run_ai_autofix():
    result = run_autofix()
    return JSONResponse({"autofix": result})
