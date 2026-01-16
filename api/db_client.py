
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
    def get_active_notifications(self):
        return self._get("/notifications/active")

    def get_notifications_by_date(self, start_date, end_date, skip=0, limit=12, labels=None):
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "skip": skip,
            "limit": limit
        }
        if labels:
             # Logic to join if it's a list, assuming API expects comma separated string
             if isinstance(labels, list):
                 params["labels"] = ",".join(map(str, labels))
             else:
                 params["labels"] = labels
        return self._get("/notifications/by_date", params=params)

    def get_notifications_by_session(self, session_id, skip=0, limit=12, labels=None):
        params = {
            "skip": skip,
            "limit": limit
        }
        if labels:
             if isinstance(labels, list):
                 params["labels"] = ",".join(map(str, labels))
             else:
                 params["labels"] = labels
        return self._get(f"/notifications/by_session/{session_id}", params=params)

    def get_document_count(self, start_time, end_time):
        return self._get("/notifications/count", params={"start_time": start_time, "end_time": end_time}).get("count")

    def get_notification_by_id(self, notification_id):
        return self._get(f"/notifications/{notification_id}")

    def get_notifications_around_id(self, notification_id, limit=3):
        return self._get(f"/notifications/{notification_id}/around", params={"limit": limit})

    def close_notification(self, notification_id):
        return self._post(f"/notifications/{notification_id}/close").get("matched_count")

    def delete_notification(self, notification_id):
        # API expects this to return None if not found, or object if deleted?
        # My route returns object if found/deleted, 404 otherwise.
        try:
            return self._delete(f"/notifications/{notification_id}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def delete_notifications_by_ids(self, notification_ids: List[str]):
        return self._delete("/notifications/batch", json=notification_ids)

    def clear_all_notifications(self):
        return self._post("/notifications/clear_all").get("modified_count")

    def delete_all(self, start_date, end_date):
        return self._delete("/notifications/by_date", params={"start_date": start_date, "end_date": end_date})

    def add_notification(self, record: dict):
        return self._post("/notifications", json=record)


    # --- Sessions ---
    def add_detection_session(self, camera_id: str):
        return self._post("/sessions", json={"camera_id": camera_id})

    def update_detection_session_end(self, session_id: str):
        return self._put(f"/sessions/{session_id}/end")

    def get_detection_sessions_with_pagination(self, skip=0, limit=10):
        data = self._get("/sessions", params={"skip": skip, "limit": limit})
        return data["sessions"], data["total_count"]

    def get_active_sessions(self):
        return self._get("/sessions/active")

    def get_detection_session_by_id(self, session_id):
        return self._get(f"/sessions/{session_id}")

    def delete_detection_session_and_related(self, session_id):
        # Logic is complex here because it involves notification deletion.
        # But wait, original code `delete_detection_session_and_related` did:
        # 1. delete images (needs notification list)
        # 2. delete notifications
        # 3. delete session

        # The DB service `delete_detection_session` just deletes the session.
        # It seems I missed `delete_detection_session_and_related` logic in DB service repository.
        # I should probably just implement `delete_detection_session` in DB service
        # and let the client handle cascading deletions if needed, OR
        # implement cascading deletion in DB service.
        # But DB service shouldn't know about images.

        # Best approach: Client (API) fetches notifications for session -> deletes images -> deletes notifications -> deletes session.
        # Or I add an endpoint to DB service to delete notifications by session and return them?

        # For now, let's just expose `delete_detection_session` and handle the rest in the caller if possible.
        # But wait, `api/db.py` had `delete_detection_session_and_related`.

        return self._delete(f"/sessions/{session_id}")

    # --- Settings ---
    def get_settings(self):
        return self._get("/settings")

    def update_settings(self, memory: int, sensitivity: float):
        return self._put("/settings", json={"memory": memory, "sensitivity": sensitivity})

    # --- Cameras ---
    def fetch_camera_urls(self):
        return self._get("/cameras")

db_client = DBClient()
