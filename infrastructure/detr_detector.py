import torch
from transformers import DetrImageProcessorFast, DetrForObjectDetection
import time
from typing import Any, List, Dict, Union
import numpy as np
from core.interfaces import ObjectDetector

class DetrObjectDetector(ObjectDetector):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading DETR model on {self.device}...")
        self.processor = DetrImageProcessorFast.from_pretrained(
            "facebook/detr-resnet-50", revision="no_timm"
        )
        self.model = DetrForObjectDetection.from_pretrained(
            "facebook/detr-resnet-50", revision="no_timm"
        ).to(self.device)
        self.model.half()
        self.model.eval()
        self.batch_count = 1

    def detect(self, image: Any) -> Dict[str, Any]:
        """
        Detects objects in a single image.
        image: numpy array or PIL Image.
        """
        inputs = self.processor(images=image, return_tensors="pt").to(
            self.device, dtype=torch.float16, non_blocking=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)

        target_sizes = torch.tensor([image.shape[:2]]).to(self.device)
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.7
        )[0]

        if self.device.type == "cpu":
            results["scores"] = results["scores"].detach().cpu().numpy()
            results["boxes"] = results["boxes"].detach().cpu().numpy()
            results["labels"] = results["labels"].detach().cpu().numpy()

        del inputs
        del outputs
        if self.device.type == "cuda":
            torch.cuda.empty_cache()

        return results

    def detect_batch(self, frames: List[Any]) -> List[Dict[str, Any]]:
        """
        frames: list of numpy arrays
        """
        inputs = self.processor(images=frames, return_tensors="pt", device=self.device).to(
            self.device, dtype=torch.float16, non_blocking=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        target_sizes = torch.tensor([frame.shape[:2] for frame in frames]).to(self.device)
        results = self.processor.post_process_object_detection(
            outputs, threshold=0.7, target_sizes=target_sizes
        )

        # CPU conversion if needed is tricky for batch list of dicts with tensors
        # But for consistency let's leave them as tensors unless needed,
        # but original code converted to list/json later.

        del inputs
        del outputs
        if self.device.type == "cuda":
            torch.cuda.empty_cache()

        return results
