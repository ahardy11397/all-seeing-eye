from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import math
import numpy as np
import time

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
        self._tracker: Optional[cv2.TrackerCSRT_create] = None
        self._tracked_box: tuple[int, int, int, int] | None = None
        self._box_history: list[tuple[float, float, float, float]] = []
        self._motion_history: list[float] = []
        self._prev_gray: np.ndarray | None = None
        self._vehicle_idle_frames = 0
        self._vehicle_parked_until = 0.0
        self._roi_mask: np.ndarray | None = None

    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")

    def _ensure_roi_mask(self, frame: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
        x1, y1, x2, y2 = box
        h, w = frame.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255
        return mask

    def _motion_score(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self._prev_gray is None or self._prev_gray.shape != gray.shape:
            self._prev_gray = gray
            return 0.0

        diff = cv2.absdiff(self._prev_gray, gray)
        if self._roi_mask is not None:
            diff = cv2.bitwise_and(diff, diff, mask=self._roi_mask)
        _, diff = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
        motion_pixels = float(np.count_nonzero(diff))
        self._prev_gray = gray
        return motion_pixels

    def _center_shift(self) -> float:
        if len(self._box_history) < 2:
            return 0.0
        x1, y1, x2, y2 = self._box_history[-1]
        px1, py1, px2, py2 = self._box_history[-2]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        pcx = (px1 + px2) / 2
        pcy = (py1 + py2) / 2
        return float(math.hypot(cx - pcx, cy - pcy))

    def detect(self, frame: np.ndarray) -> Detection | None:
        self._frame_count += 1
        if self._frame_count % settings.detection_interval != 0:
            return self._last_detection

        now = time.time()
        if self._vehicle_parked_until and now < self._vehicle_parked_until:
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
            if candidate.box is not None:
                motion = self._motion_score(frame)
                shift = self._center_shift()
                self._motion_history.append(motion)
                if len(self._motion_history) > 12:
                    self._motion_history.pop(0)

                avg_motion = sum(self._motion_history) / len(self._motion_history) if self._motion_history else 0.0

                if avg_motion < 250 and shift < 1.8:
                    self._vehicle_idle_frames += 1
                    if self._vehicle_idle_frames >= settings.parked_frames:
                        self._vehicle_parked_until = now + settings.parked_cooldown_s
                        self._tracked_box = None
                        self._box_history.clear()
                        self._motion_history.clear()
                        self._roi_mask = None
                        self._prev_gray = None
                        self._positive_count = 0
                        self._negative_count = 0
                        self._last_detection = None
                        return None
                else:
                    self._vehicle_idle_frames = 0

            self._tracked_box = candidate.box
            if candidate.box is not None:
                self._roi_mask = self._ensure_roi_mask(frame, candidate.box)
                self._box_history.append(candidate.box)
                if len(self._box_history) > 8:
                    self._box_history.pop(0)

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
                self._tracked_box = None
                self._box_history.clear()
                self._motion_history.clear()
                self._roi_mask = None
                self._prev_gray = None
                return None

        return self._last_detection
