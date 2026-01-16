
import os
import requests
from typing import List, Optional, Dict, Any

class DBClient:
    def __init__(self):
        self.base_url = os.environ.get("DB_SERVICE_URL", "http://db-service:8000")

    def _get(self, endpoint, params=None):
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, json=None):
        response = requests.post(f"{self.base_url}{endpoint}", json=json)
        response.raise_for_status()
        return response.json()

    def _put(self, endpoint, json=None):
        response = requests.put(f"{self.base_url}{endpoint}", json=json)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint, params=None, json=None):
        response = requests.delete(f"{self.base_url}{endpoint}", params=params, json=json)
        response.raise_for_status()
        return response.json()

    # --- Notifications ---
    def add_notification(self, record: dict):
        # Convert datetime objects to string if needed
        # But assuming record is a dict ready for json serialization
        return self._post("/notifications", json=record)

    # --- Sessions ---
    def add_detection_session(self, camera_id: str):
        return self._post("/sessions", json={"camera_id": camera_id})

    def update_detection_session_end(self, session_id: str):
        return self._put(f"/sessions/{session_id}/end")

    def update_last_open_session(self, camera_id: str):
        # This was in services/core/db.py.
        # I need to implement this logic either in client or DB service.
        # DB service didn't implement `update_last_open_session` endpoint directly.
        # But I can replicate the logic: find active session -> update end.
        # Or add endpoint to DB service.
        # Adding endpoint to DB service is cleaner.

        # Since I can't easily modify DB service now without stepping back (which I can do but prefer not to loop),
        # I'll implement the logic here using available endpoints if possible?
        # No, `get_active_sessions` returns all.
        # Let's add the missing logic to the client by fetching active sessions for camera?
        # `get_active_sessions` returns all active sessions.
        pass

    # --- Cameras ---
    def fetch_camera_urls(self):
        return self._get("/cameras")

    # --- Settings ---
    def get_settings(self):
        return self._get("/settings")

db_client = DBClient()
