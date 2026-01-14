import uuid
import json
import cv2
import numpy as np
from typing import List, Dict
from core import utils


class ImageProcessor:
    @staticmethod
    def decode_image(image_bytes: bytes) -> np.ndarray:
        """Decodes a single image from bytes."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    @staticmethod
    def decode_image_batch(image_bytes_list: List[bytes]) -> List[np.ndarray]:
        """Decodes a batch of images."""
        return [
            ImageProcessor.decode_image(image_bytes) for image_bytes in image_bytes_list
        ]

    @staticmethod
    def serialize_detection_results(results: List[Dict[str, any]]) -> List[str]:
        """Serializes detection results for Redis storage."""
        serialized_results = []
        for result in results:
            serialized_result = {
                "scores": result["scores"].cpu().tolist(),
                "labels": result["labels"].cpu().tolist(),
                "boxes": result["boxes"].cpu().tolist(),
            }
            serialized_results.append(json.dumps(serialized_result))
        return serialized_results

    @staticmethod
    def save_image_with_detections(
        image: np.ndarray, detections: Dict[str, any], output_dir: str = "output"
    ) -> str:
        """Draws detections on the image and saves it."""
        image_with_detections = utils.draw_detections(image, detections)
        unique_id = str(uuid.uuid4())
        output_path = f"{output_dir}/{unique_id}.jpg"
        cv2.imwrite(output_path, image_with_detections)
        return output_path

    @staticmethod
    def encode_img(image_frame: np.ndarray, encoding_method="binary") -> bytes:
        """Encodes an image frame to bytes."""
        _, buffer = cv2.imencode(".jpg", image_frame)
        if encoding_method == "base64":
            import base64

            frame_encoded = base64.b64encode(buffer).decode("utf-8")
            return frame_encoded.encode("utf-8")
        elif encoding_method == "binary":
            return buffer.tobytes()
        else:
            raise ValueError("Unsupported encoding method. Use 'binary' or 'base64'.")


# frame_packet = pickle.loads(frame_data[1])
# frame_number = frame_packet["frame_number"]
# frame = np.frombuffer(frame_packet["frame_data"], dtype=np.uint8)
# frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
