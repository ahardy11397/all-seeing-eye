from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from config import settings


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    label: str
    box: tuple[int, int, int, int] | None = None


class Detector:
    def __init__(self) -> None:
        self.model = None
        self._last_detection: Detection | None = None
        self._frame_count = 0

    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")

    def detect(self, frame: np.ndarray) -> Detection | None:
        self._frame_count += 1
        if self._frame_count % settings.detection_interval != 0:
            return self._last_detection

        self._load_model()
        results = self.model(frame, verbose=False, classes=[0, 2, 5, 7])

        if not results:
            self._last_detection = None
            return None

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            self._last_detection = None
            return None

        largest = max(boxes, key=lambda b: float((b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1])))
        xyxy = largest.xyxy[0].tolist()
        x1, y1, x2, y2 = map(int, xyxy)
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        cls = int(largest.cls[0].item())
        label = "person" if cls == 0 else "vehicle"
        self._last_detection = Detection(x, y, label, box=(x1, y1, x2, y2))
        return self._last_detection
