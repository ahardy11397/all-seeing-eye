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

        self.idle_mode = "idle"  # idle | glance | scan
        self.idle_scan_angle = 0.0
        self.idle_scan_speed = random.uniform(0.4, 0.9)
        self.idle_next_switch = time.time() + random.uniform(2.0, 5.0)
        self.idle_glance_target_x = self.cx
        self.idle_glance_target_y = self.cy
        self.idle_glance_origin_x = self.cx
        self.idle_glance_origin_y = self.cy
        self.idle_glance_started_at: float | None = None
        self.idle_glance_duration: float = 0.0

    def _next_blink_time(self) -> float:
        return time.time() + random.uniform(*settings.blink_interval_s)

    def _switch_idle_mode(self, now: float) -> None:
        modes = ["idle", "glance", "scan"]
        modes.remove(self.idle_mode)
        self.idle_mode = random.choice(modes)
        if self.idle_mode == "scan":
            self.idle_scan_speed = random.uniform(0.4, 0.9)
        self.idle_next_switch = now + random.uniform(2.0, 5.0)

    def _idle_target(self, now: float) -> tuple[int, int]:
        if now >= self.idle_next_switch:
            self._switch_idle_mode(now)

        if self.idle_mode == "scan":
            self.idle_scan_angle += self.idle_scan_speed * 0.05
            if self.idle_scan_angle > math.pi * 2:
                self.idle_scan_angle -= math.pi * 2
            reach = random.uniform(settings.max_pupil_offset * 0.7, settings.max_pupil_offset)
            tx = int(self.cx + math.cos(self.idle_scan_angle) * reach)
            ty = int(self.cy + math.sin(self.idle_scan_angle * 0.7) * reach * 0.6)
            return tx, ty

        if self.idle_mode == "glance":
            if self.idle_glance_started_at is None:
                self.idle_glance_started_at = now
                self.idle_glance_duration = random.uniform(*settings.idle_glance_duration_s)
                self.idle_glance_origin_x = self.iris_x
                self.idle_glance_origin_y = self.iris_y
                angle = random.uniform(0, math.pi * 2)
                reach = random.uniform(25, settings.max_pupil_offset)
                self.idle_glance_target_x = int(self.cx + math.cos(angle) * reach)
                self.idle_glance_target_y = int(self.cy + math.sin(angle) * reach)

            if now - self.idle_glance_started_at >= self.idle_glance_duration:
                self.idle_glance_started_at = None
                self.idle_mode = "idle"
                self.idle_next_switch = now + random.uniform(1.0, 3.0)
                return int(self.idle_glance_origin_x), int(self.idle_glance_origin_y)

            return self.idle_glance_target_x, self.idle_glance_target_y

        return self.cx, self.cy

    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        if target_x is not None and target_y is not None:
            tx = max(0, min(self.width, target_x))
            ty = max(0, min(self.height, target_y))
            self.idle_mode = "idle"
            self.idle_glance_started_at = None
            self.idle_next_switch = now + random.uniform(2.0, 5.0)
        else:
            tx, ty = self._idle_target(now)

        self.iris_x += (tx - self.iris_x) * settings.smoothing
        self.iris_y += (ty - self.iris_y) * settings.smoothing

        blink_interval = settings.blink_interval_s
        if self.idle_mode != "idle":
            blink_interval = (blink_interval[0] * 0.6, blink_interval[1] * 0.7)

        if self.blink_started_at is None and now >= self.next_blink_at:
            self.blink_started_at = now
            self.blink_duration = random.uniform(*settings.blink_duration_s)

        if self.blink_started_at is not None:
            if now - self.blink_started_at >= self.blink_duration:
                self.blink_started_at = None
                self.next_blink_at = now + random.uniform(*blink_interval)

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
