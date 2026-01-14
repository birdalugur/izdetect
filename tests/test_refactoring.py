import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock external heavy dependencies
sys.modules["cv2"] = MagicMock()
sys.modules["torch"] = MagicMock()
sys.modules["transformers"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["pymongo"] = MagicMock()
sys.modules["bson"] = MagicMock()
sys.modules["bson.objectid"] = MagicMock()
sys.modules["matplotlib"] = MagicMock()
sys.modules["filterpy"] = MagicMock()
sys.modules["filterpy.kalman"] = MagicMock()
sys.modules["scipy"] = MagicMock()
sys.modules["scipy.optimize"] = MagicMock()
sys.modules["lap"] = MagicMock()
sys.modules["skimage"] = MagicMock()
sys.modules["PIL"] = MagicMock()

# Add root to path
sys.path.append(os.getcwd())

from core.interfaces import MessageBroker, VideoSource, DetectionRepository, ObjectDetector
from services.processors.frame_producer import FrameProducer
from services.processors.inference import Inference

class TestRefactoring(unittest.TestCase):
    def test_frame_producer_structure(self):
        # Mock dependencies
        mock_source = MagicMock(spec=VideoSource)
        mock_broker = MagicMock(spec=MessageBroker)

        producer = FrameProducer(
            video_source=mock_source,
            message_broker=mock_broker,
            output_queue="test_q",
            camera_id="cam-1"
        )

        self.assertIsNotNone(producer)
        self.assertEqual(producer.camera_id, "cam-1")

    def test_inference_structure(self):
        mock_detector = MagicMock(spec=ObjectDetector)
        mock_broker = MagicMock(spec=MessageBroker)

        inference = Inference(
            detector=mock_detector,
            message_broker=mock_broker,
            input_queue="in",
            output_queue="out",
            image_bytes_queue="img"
        )
        self.assertIsNotNone(inference)

    def test_repository_structure(self):
        from infrastructure.mongo_repository import MongoDetectionRepository

        repo = MongoDetectionRepository()
        self.assertIsInstance(repo, DetectionRepository)

        # Test add_notification
        mock_collection = repo.db.__getitem__.return_value
        mock_collection.insert_one.return_value.inserted_id = "123"

        res = repo.add_notification({"test": "data"})
        self.assertEqual(res, "123")

    def test_broker_structure(self):
        from infrastructure.redis_broker import RedisBroker
        broker = RedisBroker()
        self.assertIsInstance(broker, MessageBroker)

        broker.publish("chan", "msg")
        broker.client.publish.assert_called_with("chan", "msg")

    def test_api_db_integration(self):
        # Simulate environment where 'config' is available (inside api/ folder)
        api_path = os.path.join(os.getcwd(), "api")
        sys.path.append(api_path)

        try:
            # We import db, which imports config from current path
            import db

            repo_mock = db.repository
            repo_mock.get_settings = MagicMock(return_value={"memory": 10})

            res = db.get_settings()
            self.assertEqual(res, {"memory": 10})
        finally:
            sys.path.remove(api_path)

if __name__ == "__main__":
    unittest.main()
