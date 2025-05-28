# app/routes/system.py
from fastapi import APIRouter
import psutil
from pydantic import BaseModel
from services.redis_service import RedisService
from fastapi import HTTPException

router = APIRouter(prefix="/system", tags=["System"])
redis_service = RedisService()


class Settings(BaseModel):
    memory: int
    sensitivity: float


@router.post("/update-settings")
async def update_settings(settings: Settings):
    try:
        redis_service.set("tracking:memory", settings.memory)
        redis_service.set("tracking:sensitivity", settings.sensitivity)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {e}")


@router.get("/ram")
def get_ram_usage():
    ram = psutil.virtual_memory()
    return {"total": ram.total, "used": ram.used}
