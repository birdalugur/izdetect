import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from config import Config
from routes import system, cameras, notifications, detection_sessions
from db import cleanup_old_data


app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    #allow_origins=Config.ALLOWED_ORIGINS,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(system.router)
app.include_router(cameras.router)
app.include_router(notifications.router)
app.include_router(detection_sessions.router)


async def run_cleanup_task():
    """
    Arka planda belirli aralıklarla çalışarak eski kayıtları temizler.
    """
    while True:
        try:
            print("Starting scheduled cleanup task...")
            result = cleanup_old_data()
            if result:
                print(f"Cleanup completed. Deleted {result.deleted_count} notifications.")
        except Exception as e:
            print(f"Cleanup task failed: {e}")

        # Her saat başı çalış (3600 saniye)
        await asyncio.sleep(3600)


@app.on_event("startup")
async def startup_event():
    # Uygulama başladığında temizlik görevini arka planda başlat
    # Task referansını saklayarak garbage collector tarafından silinmesini önle
    app.state.cleanup_task = asyncio.create_task(run_cleanup_task())


@app.get("/")
async def index():
    return {"message": "Welcome to the Object Detector!"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
