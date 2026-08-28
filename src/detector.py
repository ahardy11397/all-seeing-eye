from __future__ import annotations

from dataclasses import dataclass

from ultralytics import YOLO

from config import settings


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    label: str


class Detector:
    def __init__(self) -> None:
        self.model = YOLO("yolov8n.pt")
        self._last_detection: Detection | None = None
        self._frame_count = 0

    def detect(self, frame) -> Detection | None:
        self._frame_count += 1
        if self._frame_count % settings.detection_interval != 0:
            return self._last_detection

        results = self.model(frame, verbose=False, classes=[0, 2, 5, 7])

        if not results:
            self._last_detection = None
            return None

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            self._last_detection = None
            return None

        largest = max(boxes, key=lambda b: float(b.area))
        xyxy = largest.xyxy[0].tolist()
        x1, y1, x2, y2 = xyxy
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        cls = int(largest.cls[0].item())
        label = "person" if cls == 0 else "vehicle"
        self._last_detection = Detection(x, y, label)
        return self._last_detection
