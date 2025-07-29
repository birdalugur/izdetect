from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
from utils.helpers import map_labels
from config import Config
from db import (
    get_active_notifications,
    close_notification,
    clear_all_notifications,
    get_notifications_by_date,
    delete_notification,
    delete_all,
    delete_notifications_by_ids,
    get_notifications_by_session,
    get_notification_by_id,
    get_notifications_around_id,
    get_document_count,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class BatchDeleteRequest(BaseModel):
    notification_ids: List[str]


@router.post("/{notification_id}/close", summary="Bildirim kapat")
async def close_notification_route(
    notification_id: str = Path(..., description="Kapatılacak bildirimin ID'si"),
):
    """
    Belirtilen bildirimin durumunu 'closed' yapar.

    Returns:
        dict: İşlem sonucu mesajı.
    """
    if close_notification(notification_id) == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification closed successfully"}


@router.get("/", summary="Aktif bildirimleri getir")
async def get_notifications():
    """
    Durumu 'active' olan bildirimleri getirir (anlık bildirimler).

    Returns:
        List[dict]: Etiketlenmiş bildirim listesi.
    """
    notifications = get_active_notifications()
    notifications = [
        map_labels(notification, Config.LABEL_MAP) for notification in notifications
    ]
    return JSONResponse(notifications)


@router.get("/by_date", summary="Tarihe göre bildirimleri getir")
async def get_notifications_by_date_endpoint(
    start_date: str,
    end_date: str,
    skip: int = 0,
    limit: int = 12,
    labels: Optional[str] = None,
):
    """
    Belirtilen tarih aralığına ve isteğe bağlı etiketlere göre bildirimleri döner.

    Args:
        start_date (str): Başlangıç tarihi (ISO format).
        end_date (str): Bitiş tarihi (ISO format).
        skip (int): Atlanacak kayıt sayısı.
        limit (int): Döndürülecek kayıt sayısı.
        labels (str, optional): Virgülle ayrılmış label ID'leri.

    Returns:
        List[dict]: Etiketlenmiş bildirim listesi.
    """
    try:
        label_list = [int(label) for label in labels.split(",")] if labels else None
        notifications = get_notifications_by_date(
            start_date, end_date, skip, limit, label_list
        )
        notifications = [
            map_labels(notification, Config.LABEL_MAP) for notification in notifications
        ]
        return JSONResponse(notifications)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid label format: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/record_count", summary="Tarihler arasındaki kayıt sayısını getir")
async def get_record_count(
    start_time: str = Query(..., description="Başlangıç zamanı (ISO format)"),
    end_time: str = Query(..., description="Bitiş zamanı (ISO format)"),
):
    """
    Belirtilen zaman aralığındaki toplam kayıt sayısını döner.

    Returns:
        dict: Kayıt sayısı.
    """
    try:
        count = get_document_count(start_time, end_time)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by_session/{session_id}", summary="Oturuma göre bildirimleri getir")
async def get_notifications_by_session_endpoint(
    session_id: str,
    skip: int = 0,
    limit: int = 12,
    labels: Optional[str] = None,
):
    """
    Belirtilen oturum ID'sine ait bildirimleri getirir.

    Args:
        session_id (str): Oturum ID'si.
        skip (int): Atlanacak kayıt sayısı.
        limit (int): Döndürülecek kayıt sayısı.
        labels (str, optional): Virgülle ayrılmış label ID'leri.

    Returns:
        List[dict]: Bildirim listesi.
    """
    try:
        if labels and labels.strip():
            label_list = [str(label.strip()) for label in labels.split(",") if label.strip()]
        else:
            label_list = None

        notifications = get_notifications_by_session(
            session_id, skip, limit, label_list
        )
        notifications = [
            map_labels(notification, Config.LABEL_MAP) for notification in notifications
        ]
        return JSONResponse(notifications)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/clear-all", summary="Tüm aktif bildirimleri kapat")
async def clear_all_notifications_route():
    """
    Durumu 'active' olan tüm bildirimleri 'closed' yapar.

    Returns:
        dict: Kapatılan bildirim sayısı.
    """
    modified_count = clear_all_notifications()
    return {"message": f"{modified_count} notifications cleared"}


@router.delete("/by_date", summary="Tarihe göre bildirimleri sil")
async def delete_notifications_by_date(start_date: str, end_date: str):
    """
    Belirtilen tarih aralığındaki tüm bildirimleri siler.

    Returns:
        dict: Silinen kayıt sayısı mesajı.
    """
    try:
        result = delete_all(start_date, end_date)
        return {"message": f"{result.deleted_count} notifications deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/batch_delete", summary="ID listesine göre bildirimleri sil")
async def delete_notifications_batch(request: BatchDeleteRequest):
    """
    Belirtilen ID listesine göre birden fazla bildirimi siler.

    Args:
        request (BatchDeleteRequest): Silinecek bildirim ID'leri listesi.

    Returns:
        dict: Silinen bildirim sayısı mesajı.
    """
    try:
        result = delete_notifications_by_ids(request.notification_ids)
        return {"message": f"{result.deleted_count} notifications deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notification_id}", summary="Tekil bildirimi getir")
async def get_notification_route(notification_id: str):
    """
    Belirtilen ID'ye sahip bildirimi getirir.

    Args:
        notification_id (str): Bildirim ID'si.

    Returns:
        dict: Bildirim verisi.
    """
    notification = get_notification_by_id(notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification = map_labels(notification, Config.LABEL_MAP)
    return JSONResponse(notification)


@router.get("/{notification_id}/around", summary="Çevresel bildirimleri getir")
async def get_notifications_around_route(
    notification_id: str,
    limit: int = 3,
):
    """
    Belirtilen bildirimin etrafındaki (öncesi/sonrası) kayıtları getirir.

    Args:
        notification_id (str): Referans bildirimin ID'si.
        limit (int): Kaç adet çevresel kayıt getirileceği.

    Returns:
        List[dict]: Etiketlenmiş bildirimler.
    """
    notifications = get_notifications_around_id(notification_id, limit)
    if not notifications:
        raise HTTPException(status_code=404, detail="Notifications not found")
    notifications = [map_labels(n, Config.LABEL_MAP) for n in notifications]
    return JSONResponse(notifications)


@router.delete("/{notification_id}", summary="Tekil bildirimi sil")
async def delete_notification_route(notification_id: str):
    """
    Belirtilen ID'ye sahip bildirimi siler.

    Args:
        notification_id (str): Silinecek bildirim ID'si.

    Returns:
        dict: Başarı mesajı.
    """
    result = delete_notification(notification_id)
    if result is not None:
        return {"message": "Notification deleted successfully"}
    raise HTTPException(status_code=404, detail="Notification not found")
