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

class Track:
    def __init__(self, cx, cy, box, label, now):
        self.history = [(cx, cy, now)]
        self.box = box
        self.label = label
        self.parked_until = 0.0
        self.last_seen = now

class Detector:
    def __init__(self) -> None:
        self.model = None
        self._last_detection: Detection | None = None
        self._frame_count = 0
        self._positive_count = 0
        self._negative_count = 0

        self.tracks: list[Track] = []
        

    @property
    def _vehicle_parked_until(self) -> float:
        # Compatibility property: returns max parked_until of any track
        if not self.tracks:
            return 0.0
        parked_times = [t.parked_until for t in self.tracks if t.parked_until > 0]
        return max(parked_times) if parked_times else 0.0

    def _update_tracks(self, detections, now: float):
        # detections is list of (cx, cy, label, box)
        matched_indices = set()
        
        # simple greedy match
        for track in self.tracks:
            best_dist = 999999
            best_idx = -1
            for i, (cx, cy, label, box) in enumerate(detections):
                if i in matched_indices or label != track.label:
                    continue
                # Center distance
                dist = math.hypot(cx - track.history[-1][0], cy - track.history[-1][1])
                if dist < 120 and dist < best_dist:
                    best_dist = dist
                    best_idx = i
                    
            if best_idx != -1:
                cx, cy, label, box = detections[best_idx]
                track.history.append((cx, cy, now))
                # keep last 15 history points max
                if len(track.history) > 15:
                    track.history.pop(0)
                track.box = box
                track.last_seen = now
                matched_indices.add(best_idx)
                
                # Check parked
                if track.label == "vehicle" and len(track.history) >= 6:
                    xs = [p[0] for p in track.history]
                    ys = [p[1] for p in track.history]
                    shift = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
                    if shift < settings.parked_drift_px:
                        track.parked_until = now + settings.parked_cooldown_s
                        track.history = [track.history[-1]] # keep last position
                    else:
                        track.parked_until = 0.0
            
        # Add unmatched as new tracks
        for i, (cx, cy, label, box) in enumerate(detections):
            if i not in matched_indices:
                self.tracks.append(Track(cx, cy, box, label, now))
                
        # Remove old tracks unseen for 2 seconds
        self.tracks = [t for t in self.tracks if now - t.last_seen < 2.0]

    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")

    def detect(self, frame: np.ndarray) -> Detection | None:
        self._frame_count += 1
        if self._frame_count % settings.detection_interval != 0:
            return self._last_detection

        now = time.time()
        self._load_model()
        results = self.model(frame, verbose=False, classes=[0, 2, 5, 7])

        # extract all raw valid detections
        raw_detections = []
        if results:
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                for b in boxes:
                    conf = float(b.conf[0].item())
                    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                    area = (x2 - x1) * (y2 - y1)
                    if conf >= settings.min_confidence and area >= settings.min_box_area:
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        cls = int(b.cls[0].item())
                        label = "person" if cls == 0 else "vehicle"
                        raw_detections.append({
                            "area": area, "conf": conf, "box": (x1, y1, x2, y2),
                            "cx": cx, "cy": cy, "label": label
                        })
                        
        # Update tracks with these detections
        track_inputs = [(d["cx"], d["cy"], d["label"], d["box"]) for d in raw_detections]
        self._update_tracks(track_inputs, now)
        
        # Sort raw by area to find candidate
        raw_detections.sort(key=lambda d: d["area"], reverse=True)
        
        candidate = None
        for d in raw_detections:
            # Find the track for this detection
            track_for_d = None
            for t in self.tracks:
                if t.box == d["box"] and t.label == d["label"]:
                    track_for_d = t
                    break
                    
            if track_for_d and track_for_d.parked_until > now:
                continue # ignore parked vehicles
                
            candidate = Detection(d["cx"], d["cy"], d["label"], box=d["box"], conf=d["conf"])
            break

        if candidate:
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
                return None

        return self._last_detection
