from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict

class MessageBroker(ABC):
    """Interface for message broker operations (e.g., Redis, RabbitMQ)."""

    @abstractmethod
    def publish(self, channel: str, message: str) -> None:
        pass

    @abstractmethod
    def subscribe(self, channel: str) -> Any:
        pass

    @abstractmethod
    def lpush(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def rpop(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def flush_all(self) -> None:
        pass

class VideoSource(ABC):
    """Interface for video capturing sources."""

    @abstractmethod
    def open(self) -> bool:
        pass

    @abstractmethod
    def read(self) -> tuple[bool, Any]:
        pass

    @abstractmethod
    def release(self) -> None:
        pass

    @abstractmethod
    def is_opened(self) -> bool:
        pass

class ObjectDetector(ABC):
    """Interface for object detection models."""

    @abstractmethod
    def detect(self, image: Any) -> List[Dict[str, Any]]:
        pass

class DetectionRepository(ABC):
    """Interface for persistent storage operations."""

    @abstractmethod
    def add_notification(self, record: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def add_detection_session(self, camera_id: str) -> str:
        pass

    @abstractmethod
    def update_session_end(self, session_id: str) -> None:
        pass

    @abstractmethod
    def update_last_open_session(self, camera_id: str) -> None:
        pass

    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_camera_urls(self) -> List[str]:
        pass
