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


@router.delete("/{notification_id}")
async def delete_notification_route(notification_id: str):
    """Deletes a notification by ID."""
    result = delete_notification(notification_id)
    if result is not None:
        return {"message": "Notification deleted successfully"}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/clear-all")
async def clear_all_notifications_route():
    modified_count = clear_all_notifications()
    return {"message": f"{modified_count} notifications cleared"}
