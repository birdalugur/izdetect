from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_settings, update_settings
import psutil

router = APIRouter(prefix="/system", tags=["System"])


class Settings(BaseModel):
    memory: int
    sensitivity: float


@router.post("/update-settings")
async def update_system_settings(settings: Settings):
    try:
        update_settings(settings.memory, settings.sensitivity)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-settings")
async def fetch_system_settings():
    try:
        return get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ram")
def get_ram_usage():
    ram = psutil.virtual_memory()
    return {"total": ram.total, "used": ram.used}
