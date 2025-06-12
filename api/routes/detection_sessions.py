from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from db import get_all_detection_sessions, get_detection_sessions_with_pagination

router = APIRouter(prefix="/detection-sessions", tags=["Detection Sessions"])


@router.get("/")
async def get_detection_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return")
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
        sessions, total_count = get_detection_sessions_with_pagination(skip=skip, limit=limit)
        return JSONResponse(content={
            "records": sessions,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total_count
        })
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