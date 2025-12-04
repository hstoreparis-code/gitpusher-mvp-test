from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()


@router.get("/ai/indexers/80")
async def get_80_indexers():
    path = os.path.join("frontend", "public", "ai", "indexers", "ai-80-indexers.json")
    return FileResponse(path)
