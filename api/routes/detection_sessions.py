from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from db import (get_all_detection_sessions, get_detection_sessions_with_pagination, delete_detection_session_and_related, get_detection_session_by_id)

router = APIRouter(prefix="/detection-sessions", tags=["Detection Sessions"])


@router.get("/{session_id}")
async def get_detection_session(session_id: str):
    """
    Belirtilen session_id'ye göre tek bir detection session getirir.
    """
    try:
        session = get_detection_session_by_id(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return JSONResponse(content=session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_detection_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
):
    """
    Retrieves detection sessions from the database with pagination support.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-100)

    Returns:
        JSON response with records and total count
    """
    try:
        sessions, total_count = get_detection_sessions_with_pagination(
            skip=skip, limit=limit
        )
        return JSONResponse(
            content={
                "records": sessions,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_detection_sessions_endpoint():
    """
    Retrieves all detection sessions from the database (legacy endpoint).
    This endpoint is kept for backward compatibility.
    """
    try:
        sessions = get_all_detection_sessions()
        return JSONResponse(content=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_detection_session(session_id: str):
    """
    Belirtilen detection_session’ı ve ilişkili notification + görselleri siler.
    """
    try:
        deleted = delete_detection_session_and_related(session_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        return JSONResponse(content={"deleted": True})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
