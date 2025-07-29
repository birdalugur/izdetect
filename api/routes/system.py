from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_settings, update_settings
import psutil

router = APIRouter(prefix="/system", tags=["System"])


class Settings(BaseModel):
    memory: int
    sensitivity: float


@router.post("/update-settings", summary="Sistem ayarlarını güncelle")
async def update_system_settings(settings: Settings):
    """
    Veritabanındaki sistem ayarlarını (memory ve sensitivity) günceller.

    Args:
        settings (Settings): Yeni sistem ayarları.

    Returns:
        dict: Güncelleme işlemi sonucunu belirten mesaj.
    """
    try:
        update_settings(settings.memory, settings.sensitivity)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-settings", summary="Mevcut sistem ayarlarını getir")
async def fetch_system_settings():
    """
    Veritabanında kayıtlı olan sistem ayarlarını (memory ve sensitivity) getirir.

    Returns:
        dict: Kayıtlı sistem ayarları.
    """
    try:
        return get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ram", summary="RAM kullanım bilgilerini getir")
def get_ram_usage():
    """
    Sistem RAM kullanım bilgisini getirir.

    Returns:
        dict: Toplam ve kullanılan RAM bilgisi (bayt cinsinden).
    """
    ram = psutil.virtual_memory()
    return {"total": ram.total, "used": ram.used}
