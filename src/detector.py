from __future__ import annotations

import time
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
        self._positive_count = 0
        self._negative_count = 0

        self._prev_gray: np.ndarray | None = None
        self._parked_until: float = 0.0
        self._motion_history: list[tuple[int, int, float]] = []

    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")

    def _motion_in_box(self, frame: np.ndarray, box: tuple[int, int, int, int]) -> int:
        x1, y1, x2, y2 = box
        h, w = frame.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        if x2 <= x1 or y2 <= y1:
            return 0

        roi = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self._prev_gray is None or self._prev_gray.shape != gray.shape:
            self._prev_gray = gray
            return 0

        diff = cv2.absdiff(self._prev_gray, gray)
        _, diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        motion_pixels = int(np.count_nonzero(diff))
        self._prev_gray = gray
        return motion_pixels

    def detect(self, frame: np.ndarray) -> Detection | None:
        self._frame_count += 1
        if self._frame_count % settings.detection_interval != 0:
            return self._last_detection

        if time.time() < self._parked_until:
            self._prev_gray = None
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
                    area, b, conf, x1, y1, x2, y2 = filtered[0]
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    cls = int(b.cls[0].item())
                    label = "person" if cls == 0 else "vehicle"
                    candidate = Detection(cx, cy, label, box=(x1, y1, x2, y2))

        if candidate:
            motion = self._motion_in_box(frame, candidate.box)
            now = time.time()
            self._motion_history.append((candidate.x, candidate.y, now))
            self._motion_history = [t for t in self._motion_history if now - t[2] <= 2.0]

            if motion < settings.min_motion_pixels and len(self._motion_history) > 8:
                xs = [t[0] for t in self._motion_history]
                ys = [t[1] for t in self._motion_history]
                if max(xs) - min(xs) < 12 and max(ys) - min(ys) < 12:
                    self._positive_count = 0
                    self._negative_count = 0
                    self._last_detection = None
                    self._parked_until = now + settings.parked_cooldown_s
                    self._prev_gray = None
                    return None

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
                self._prev_gray = None
                self._motion_history.clear()
                return None

        return self._last_detection
