from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

from pathlib import Path

BASE_PUBLIC = Path(__file__).resolve().parents[2] / "frontend" / "public" / "ai"


@router.get("/ai/knowledge/priority-map")
async def get_priority_map():
    path = BASE_PUBLIC / "knowledge" / "priority-map.json"
    return FileResponse(str(path))


@router.get("/ai/knowledge/tool-catalog")
async def get_tool_catalog():
    path = BASE_PUBLIC / "knowledge" / "tool-catalog.json"
    return FileResponse(str(path))


@router.get("/ai/agents/toolpack")
async def get_toolpack():
    path = BASE_PUBLIC / "agents" / "toolpack.json"
    return FileResponse(str(path))


@router.get("/ai/agents/openai-tools")
async def get_openai_tools():
    path = BASE_PUBLIC / "agents" / "openai-tools.json"
    return FileResponse(str(path))
