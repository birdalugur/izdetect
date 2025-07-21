# app/routes/notifications.py
from fastapi import APIRouter, HTTPException, Path
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
    get_notification_by_id,  # Yeni import
    get_notifications_around_id,  # Yeni import
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class BatchDeleteRequest(BaseModel):
    notification_ids: List[str]


@router.post("/{notification_id}/close")
async def close_notification_route(
    notification_id: str = Path(..., description="The ID of the notification to close"),
):
    if close_notification(notification_id) == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification closed successfully"}


@router.get("/")
async def get_notifications():
    notifications = get_active_notifications()
    notifications = [
        map_labels(notification, Config.LABEL_MAP) for notification in notifications
    ]
    return JSONResponse(notifications)


@router.get("/by_date")
async def get_notifications_by_date_endpoint(
    start_date: str,
    end_date: str,
    skip: int = 0,
    limit: int = 12,
    labels: Optional[str] = None,
):
    try:
        # Boş string kontrolü ekle
        if labels and labels.strip():
            label_list = [str(label.strip()) for label in labels.split(",") if label.strip()]
        else:
            label_list = None
            
        notifications, total_count = get_notifications_by_date(
            start_date, end_date, skip, limit, label_list
        )
        notifications = [
            map_labels(notification, Config.LABEL_MAP) for notification in notifications
        ]
        return JSONResponse({
            "notifications": notifications,
            "total": total_count,
            "skip": skip,
            "limit": limit
        })
    except Exception as e:
        # Debug için detaylı hata mesajı
        import traceback
        print(f"Error in by_date endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/by_session/{session_id}")
async def get_notifications_by_session_endpoint(
    session_id: str,
    skip: int = 0,
    limit: int = 12,
    labels: Optional[str] = None,
):
    try:
        # Boş string kontrolü ekle
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
        # Debug için detaylı hata mesajı
        import traceback
        print(f"Error in by_session endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/clear-all")
async def clear_all_notifications_route():
    modified_count = clear_all_notifications()
    return {"message": f"{modified_count} notifications cleared"}


@router.delete("/by_date")
async def delete_notifications_by_date(start_date: str, end_date: str):
    """Deletes all notifications within the specified date range."""
    try:
        result = delete_all(start_date, end_date)
        return {"message": f"{result.deleted_count} notifications deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/batch_delete")
async def delete_notifications_batch(request: BatchDeleteRequest):
    """Deletes notifications by a list of IDs."""
    try:
        result = delete_notifications_by_ids(request.notification_ids)
        return {"message": f"{result.deleted_count} notifications deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notification_id}")
async def get_notification_route(notification_id: str):
    """Gets a single notification by ID."""
    notification = get_notification_by_id(notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification = map_labels(notification, Config.LABEL_MAP)
    return JSONResponse(notification)


@router.get("/{notification_id}/around")
async def get_notifications_around_route(
    notification_id: str,
    limit: int = 3,
):
    """Gets notifications around a specific notification ID."""
    notifications = get_notifications_around_id(notification_id, limit)
    if not notifications:
        raise HTTPException(status_code=404, detail="Notifications not found")
    notifications = [map_labels(n, Config.LABEL_MAP) for n in notifications]
    return JSONResponse(notifications)





@router.delete("/{notification_id}")
async def delete_notification_route(notification_id: str):
    """Deletes a notification by ID."""
    result = delete_notification(notification_id)
    if result is not None:
        return {"message": "Notification deleted successfully"}
    raise HTTPException(status_code=404, detail="Notification not found")
