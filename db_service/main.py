
from fastapi import FastAPI
from core.database import db
from routes.api import router

app = FastAPI(title="DB Service")

@app.on_event("startup")
def startup_db_client():
    db.connect()

@app.on_event("shutdown")
def shutdown_db_client():
    db.close()

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "DB Service is running"}
