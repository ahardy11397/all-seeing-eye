from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import math
import numpy as np
import time

from config import settings


@dataclass
class Detection:
    x: int
    y: int
    label: str
    box: tuple[int, int, int, int] | None = None
    conf: float = 0.0


class Detector:
    def __init__(self) -> None:
        self.model = None
        self._last_detection: Detection | None = None
        self._frame_count = 0
        self._positive_count = 0
        self._negative_count = 0

        self._candidate_history: list[tuple[int, int, float]] = []
        self._vehicle_parked_until: float = 0.0
        # tunable live from the settings panel
        self.parked_drift_px: int = 8

    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")

    def _is_vehicle_parked(self, now: float) -> bool:
        if len(self._candidate_history) < 6:
            return False

        xs = [p[0] for p in self._candidate_history]
        ys = [p[1] for p in self._candidate_history]
        total_shift = math.hypot(max(xs) - min(xs), max(ys) - min(ys))

        # If the vehicle center has barely moved across recent detections, it's parked
        return total_shift < self.parked_drift_px

    def detect(self, frame: np.ndarray) -> Detection | None:
        self._frame_count += 1
        if self._frame_count % settings.detection_interval != 0:
            return self._last_detection

        now = time.time()
        if self._vehicle_parked_until and now < self._vehicle_parked_until:
            self._last_detection = None
            return None

        self._load_model()
        results = self.model(frame, verbose=False, classes=[0, 2, 5, 7])

        candidate = None
        if results:
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                filtered = []
                for b in boxes:
                    conf = float(b.conf[0].item())
                    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                    area = (x2 - x1) * (y2 - y1)
                    if conf >= settings.min_confidence and area >= settings.min_box_area:
                        filtered.append((area, b, conf, x1, y1, x2, y2))

                if filtered:
                    filtered.sort(key=lambda t: t[0], reverse=True)
                    _, b, conf, x1, y1, x2, y2 = filtered[0]
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    cls = int(b.cls[0].item())
                    label = "person" if cls == 0 else "vehicle"
                    candidate = Detection(cx, cy, label, box=(x1, y1, x2, y2), conf=conf)

        if candidate:
            if candidate.label == "vehicle" and self._is_vehicle_parked(now):
                self._vehicle_parked_until = now + settings.parked_cooldown_s
                self._candidate_history.clear()
                self._positive_count = 0
                self._negative_count = 0
                self._last_detection = None
                return None

            self._candidate_history.append((candidate.x, candidate.y, now))
            if len(self._candidate_history) > 20:
                self._candidate_history.pop(0)

            self._positive_count += 1
            self._negative_count = 0
            if self._positive_count >= settings.required_detections:
                self._last_detection = candidate
                return self._last_detection
        else:
            self._negative_count += 1
            self._positive_count = 0
            if self._negative_count >= settings.required_detections:
                self._last_detection = None
                self._candidate_history.clear()
                return None

        return self._last_detection
