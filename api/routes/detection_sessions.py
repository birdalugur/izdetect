from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from db import get_all_detection_sessions

router = APIRouter(prefix="/detection-sessions", tags=["Detection Sessions"])


@router.get("/")
async def get_detection_sessions():
    """
    Retrieves all detection sessions from the database.
    """
    try:
        sessions = get_all_detection_sessions()
        return JSONResponse(content=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
