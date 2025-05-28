from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from config import Config
from routes import system, cameras, notifications


app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(system.router)
app.include_router(cameras.router)
app.include_router(notifications.router)


@app.get("/")
async def index():
    return {"message": "Welcome to the Object Detector!"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
