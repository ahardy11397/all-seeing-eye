from __future__ import annotations

import math
import random
import time

from PIL import Image, ImageDraw

from config import settings


class Eye:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2
        self.iris_x = self.cx
        self.iris_y = self.cy
        self.next_blink_at = self._next_blink_time()
        self.blink_started_at: float | None = None
        self.blink_duration: float = 0.0

    def _next_blink_time(self) -> float:
        return time.time() + random.uniform(*settings.blink_interval_s)

    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        tx = self.cx if target_x is None else max(0, min(self.width, target_x))
        ty = self.cy if target_y is None else max(0, min(self.height, target_y))

        self.iris_x += (tx - self.iris_x) * settings.smoothing
        self.iris_y += (ty - self.iris_y) * settings.smoothing

        if self.blink_started_at is None and now >= self.next_blink_at:
            self.blink_started_at = now
            self.blink_duration = random.uniform(*settings.blink_duration_s)

        if self.blink_started_at is not None:
            if now - self.blink_started_at >= self.blink_duration:
                self.blink_started_at = None
                self.next_blink_at = self._next_blink_time()

    def render(self) -> Image.Image:
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        eye_bbox = [
            self.cx - settings.eye_radius,
            self.cy - settings.eye_radius,
            self.cx + settings.eye_radius,
            self.cy + settings.eye_radius,
        ]
        draw.ellipse(eye_bbox, fill=(240, 240, 235, 255))
        draw.ellipse(eye_bbox, outline=(20, 20, 20, 255), width=6)

        dx = self.iris_x - self.cx
        dy = self.iris_y - self.cy
        dist = math.hypot(dx, dy) or 1.0
        max_offset = settings.max_pupil_offset
        scale = min(max_offset / dist, 1.0)
        iris_cx = int(self.cx + dx * scale)
        iris_cy = int(self.cy + dy * scale)

        iris_bbox = [
            iris_cx - settings.iris_radius,
            iris_cy - settings.iris_radius,
            iris_cx + settings.iris_radius,
            iris_cy + settings.iris_radius,
        ]
        draw.ellipse(iris_bbox, fill=(60, 120, 200, 255))
        draw.ellipse(iris_bbox, outline=(10, 30, 80, 255), width=4)

        pupil_bbox = [
            iris_cx - settings.pupil_radius,
            iris_cy - settings.pupil_radius,
            iris_cx + settings.pupil_radius,
            iris_cy + settings.pupil_radius,
        ]
        draw.ellipse(pupil_bbox, fill=(10, 10, 10, 255))

        highlight_bbox = [
            iris_cx - settings.pupil_radius + 8,
            iris_cy - settings.pupil_radius + 8,
            iris_cx - settings.pupil_radius + 22,
            iris_cy - settings.pupil_radius + 22,
        ]
        draw.ellipse(highlight_bbox, fill=(255, 255, 255, 180))

        if self.blink_started_at is not None:
            t = min(1.0, (time.time() - self.blink_started_at) / self.blink_duration)
            close_t = math.sin(t * math.pi)
            close_y = int(close_t * (settings.eye_radius - 6))
            upper = [
                self.cx - settings.eye_radius,
                self.cy - settings.eye_radius,
                self.cx + settings.eye_radius,
                self.cy - 6 + close_y,
            ]
            lower = [
                self.cx - settings.eye_radius,
                self.cy + 6 - close_y,
                self.cx + settings.eye_radius,
                self.cy + settings.eye_radius,
            ]
            draw.rectangle(upper, fill=(245, 245, 240, 255))
            draw.rectangle(lower, fill=(245, 245, 240, 255))

        return img
