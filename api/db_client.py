import requests
from config import Config
from typing import List, Optional, Tuple

BASE_URL = Config.DB_SERVICE_URL

def get_settings():
    return requests.get(f"{BASE_URL}/settings").json()

def update_settings(memory: int, sensitivity: float):
    requests.post(f"{BASE_URL}/settings", json={"memory": memory, "sensitivity": sensitivity}).raise_for_status()

def get_detection_sessions_with_pagination(skip: int = 0, limit: int = 10) -> Tuple[List[dict], int]:
    data = requests.get(f"{BASE_URL}/detection-sessions", params={"skip": skip, "limit": limit}).json()
    return data["sessions"], data["total_count"]

def get_all_detection_sessions():
    return requests.get(f"{BASE_URL}/detection-sessions/all").json()

def get_active_sessions():
    return requests.get(f"{BASE_URL}/detection-sessions/active").json()

def get_active_notifications():
    return requests.get(f"{BASE_URL}/notifications/active").json()

def close_notification(notification_id):
    resp = requests.post(f"{BASE_URL}/notifications/{notification_id}/close").json()
    return resp["matched_count"]

def delete_notification(notification_id: str):
    requests.delete(f"{BASE_URL}/notifications/{notification_id}")

def delete_notifications_by_ids(notification_ids: List[str]):
    resp = requests.post(f"{BASE_URL}/notifications/delete-batch", json=notification_ids).json()
    return resp["deleted_count"]

def delete_detection_session_and_related(session_id: str) -> int:
    resp = requests.delete(f"{BASE_URL}/detection-sessions/{session_id}").json()
    return resp["deleted_count"]

def delete_all(start_date, end_date):
    if not isinstance(start_date, str):
        start_date = start_date.isoformat()
    if not isinstance(end_date, str):
        end_date = end_date.isoformat()

    resp = requests.delete(f"{BASE_URL}/all", params={"start_date": start_date, "end_date": end_date}).json()
    return resp["deleted_count"]

def clear_all_notifications():
    resp = requests.post(f"{BASE_URL}/notifications/clear-all").json()
    return resp["modified_count"]

def get_notifications_by_date(start_date, end_date, skip=0, limit=12, label_list: Optional[List[str]] = None):
    if not isinstance(start_date, str):
        start_date = start_date.isoformat()
    if not isinstance(end_date, str):
        end_date = end_date.isoformat()

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "skip": skip,
        "limit": limit
    }
    if label_list:
        params["label_list"] = label_list

    return requests.get(f"{BASE_URL}/notifications/by-date", params=params).json()

def get_document_count(start_time, end_time):
    if not isinstance(start_time, str):
        start_time = start_time.isoformat()
    if not isinstance(end_time, str):
        end_time = end_time.isoformat()
    return requests.get(f"{BASE_URL}/notifications/count", params={"start_time": start_time, "end_time": end_time}).json()

def get_notifications_by_session(session_id: str, skip: int = 0, limit: int = 12, label_list: Optional[List[str]] = None):
    params = {"skip": skip, "limit": limit}
    if label_list:
        params["label_list"] = label_list
    return requests.get(f"{BASE_URL}/notifications/by-session/{session_id}", params=params).json()

def get_notification_by_id(notification_id: str) -> Optional[dict]:
    resp = requests.get(f"{BASE_URL}/notifications/{notification_id}")
    if resp.status_code == 404:
        return None
    return resp.json()

def get_notifications_around_id(notification_id: str, limit: int = 3) -> List[dict]:
    return requests.get(f"{BASE_URL}/notifications/{notification_id}/around", params={"limit": limit}).json()

def get_detection_session_by_id(session_id: str) -> Optional[dict]:
    resp = requests.get(f"{BASE_URL}/detection-sessions/{session_id}")
    if resp.status_code == 404:
        return None
    return resp.json()

# New Camera methods
def get_cameras() -> List[dict]:
    return requests.get(f"{BASE_URL}/cameras/all").json()

def add_camera(camera_data: dict):
    requests.post(f"{BASE_URL}/cameras", json=camera_data).raise_for_status()

def delete_camera(camera_id: str):
    requests.delete(f"{BASE_URL}/cameras/{camera_id}").raise_for_status()
