from pymongo import MongoClient, SON
from bson.objectid import ObjectId
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import os
from core.interfaces import DetectionRepository

class MongoDetectionRepository(DetectionRepository):
    def __init__(self):
        mongo_host = os.environ.get("MONGO_HOST", "localhost")
        mongo_port = os.environ.get("MONGO_PORT", "27017")
        mongo_user = os.environ.get("MONGO_USER", "")
        mongo_pass = os.environ.get("MONGO_PASS", "")
        self.mongo_db_name = os.environ.get("MONGO_DB", "object_detection")

        if mongo_user and mongo_pass:
            mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
        else:
            mongo_url = f"mongodb://{mongo_host}:{mongo_port}/"

        self.client = MongoClient(mongo_url)
        self.db = self.client[self.mongo_db_name]

    # --- Write / Core Methods ---

    def add_notification(self, record: Dict[str, Any]) -> str:
        notifications_collection = self.db["notifications"]
        result = notifications_collection.insert_one(record)
        return str(result.inserted_id)

    def add_detection_session(self, camera_id: str) -> str:
        detection_sessions_collection = self.db["detection_sessions"]
        session_data = {
            "camera_id": camera_id,
            "start": datetime.now().isoformat(),
            "end": None,
            "record_count": None,
        }
        result = detection_sessions_collection.insert_one(session_data)
        return str(result.inserted_id)

    def get_notification_count(self, session_id: str) -> int:
        notifications_collection = self.db["notifications"]
        count = notifications_collection.count_documents({"session_id": session_id})
        return count

    def update_session_end(self, session_id: str) -> None:
        detection_sessions_collection = self.db["detection_sessions"]
        record_count = self.get_notification_count(session_id)
        detection_sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"end": datetime.now().isoformat(), "record_count": record_count}},
        )

    def update_last_open_session(self, camera_id: str) -> None:
        detection_sessions_collection = self.db["detection_sessions"]
        last_session = detection_sessions_collection.find_one(
            {"camera_id": camera_id, "end": None},
            sort=SON([("start", -1)]),
        )

        if last_session:
            session_id = str(last_session["_id"])
            record_count = self.get_notification_count(session_id)
            detection_sessions_collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"end": datetime.now().isoformat(), "record_count": record_count}},
            )

    def get_settings(self) -> Dict[str, Any]:
        settings_collection = self.db["system_settings"]
        settings_doc = settings_collection.find_one({"_id": "global_settings"})
        if settings_doc:
            return {
                "memory": settings_doc.get("memory", 5),
                "sensitivity": settings_doc.get("sensitivity", 0.2),
            }
        return {"memory": 5, "sensitivity": 0.2}

    def update_settings(self, memory: int, sensitivity: float):
        settings_collection = self.db["system_settings"]
        settings_collection.update_one(
            {"_id": "global_settings"},
            {"$set": {"memory": memory, "sensitivity": sensitivity}},
            upsert=True,
        )

    def get_camera_urls(self) -> List[str]:
         camera_collection = self.db["cameras"]
         return [cam["ip"] for cam in camera_collection.find()]

    # --- API Read Methods ---

    def _format_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if not doc:
            return doc
        doc["_id"] = str(doc["_id"])
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
        return doc

    def get_detection_sessions_with_pagination(self, skip: int = 0, limit: int = 10) -> Tuple[List[dict], int]:
        total_count = self.db["detection_sessions"].count_documents({})
        sessions = list(self.db["detection_sessions"].find().sort("start", -1).skip(skip).limit(limit))

        for session in sessions:
            session = self._format_doc(session)
            session["record_count"] = self.get_notification_count(session["_id"])

        return sessions, total_count

    def get_all_detection_sessions(self):
        sessions = list(self.db["detection_sessions"].find().sort("start", -1))
        return [self._format_doc(s) for s in sessions]

    def get_active_sessions(self):
        sessions = list(self.db["detection_sessions"].find({"end": None}))
        return [self._format_doc(s) for s in sessions]

    def get_active_notifications(self):
        notifications = list(self.db["notifications"].find({"status": "active"}))
        return [self._format_doc(n) for n in notifications]

    def close_notification(self, notification_id: str):
        result = self.db["notifications"].update_one(
            {"_id": ObjectId(notification_id)}, {"$set": {"status": "closed"}}
        )
        return result.matched_count

    def get_notification(self, notification_id: str):
        try:
            return self._format_doc(self.db["notifications"].find_one({"_id": ObjectId(notification_id)}))
        except:
            return None

    def delete_notification(self, notification_id: str):
        # Returns the document so caller can get image_url
        try:
            return self.db["notifications"].find_one_and_delete({"_id": ObjectId(notification_id)})
        except:
            return None

    def delete_notifications_by_ids(self, notification_ids: List[str]):
        object_ids = [ObjectId(id) for id in notification_ids]
        # Return docs to process images
        notifications = list(self.db["notifications"].find({"_id": {"$in": object_ids}}))
        result = self.db["notifications"].delete_many({"_id": {"$in": object_ids}})
        return result, notifications

    def get_notifications_by_session_id(self, session_id: str):
         return list(self.db["notifications"].find({"session_id": session_id}))

    def delete_notifications_by_session_id(self, session_id: str):
        return self.db["notifications"].delete_many({"session_id": session_id})

    def delete_session(self, session_id: str):
        return self.db["detection_sessions"].delete_one({"_id": ObjectId(session_id)})

    def update_notifications_status(self, query: Dict, status: str):
        return self.db["notifications"].update_many(query, {"$set": {"status": status}})

    def delete_notifications(self, query: Dict) -> List[Dict]:
        docs = list(self.db["notifications"].find(query))
        self.db["notifications"].delete_many(query)
        return docs

    def find_notifications(self, query: Dict, skip=0, limit=0, sort=None):
        cursor = self.db["notifications"].find(query)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return [self._format_doc(doc) for doc in cursor]

    def count_notifications(self, query: Dict):
        return self.db["notifications"].count_documents(query)

    def get_detection_session(self, session_id: str):
        try:
            return self._format_doc(self.db["detection_sessions"].find_one({"_id": ObjectId(session_id)}))
        except:
            return None
