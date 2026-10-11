from __future__ import annotations
import math
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from config import settings

class BugEye:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2
        
        self.iris_x = self.cx
        self.iris_y = self.cy
        
        self.idle_mode = "idle"
        self.idle_next_switch = time.time() + random.uniform(2.0, 5.0)
        self.idle_glance_target_x = self.cx
        self.idle_glance_target_y = self.cy
        self.idle_glance_origin_x = self.cx
        self.idle_glance_origin_y = self.cy
        self.idle_glance_started_at = None
        self.idle_glance_duration = 0.0
        
        self._build_static_layers()

    def _build_static_layers(self) -> None:
        # We will create a base hex grid
        w, h = self.width, self.height
        hex_size = 20
        hex_w = math.sqrt(3) * hex_size
        hex_h = 2 * hex_size
        
        # Pre-render a tiling compound pattern
        pattern = Image.new("RGBA", (w * 2, h * 2), (10, 30, 10, 255))
        draw = ImageDraw.Draw(pattern)
        
        for row in range(-10, int(h * 2 / (hex_h * 0.75)) + 10):
            for col in range(-10, int(w * 2 / hex_w) + 10):
                x = col * hex_w
                y = row * hex_h * 0.75
                if row % 2 == 1:
                    x += hex_w / 2
                
                # Draw a single ommatidium (lens)
                # Outer hexagon
                points = []
                for i in range(6):
                    angle = i * math.pi / 3 - math.pi / 6
                    px = x + hex_size * math.cos(angle)
                    py = y + hex_size * math.sin(angle)
                    points.append((px, py))
                
                color_val = random.randint(40, 70)
                draw.polygon(points, fill=(20, color_val, 20, 255), outline=(0, 0, 0, 255))
                
                # Inner highlight
                draw.ellipse([x - hex_size*0.4, y - hex_size*0.4, x + hex_size*0.4, y + hex_size*0.4], fill=(50, 120, 50, 255))
                # Specular dot
                draw.ellipse([x - hex_size*0.2, y - hex_size*0.3, x, y - hex_size*0.1], fill=(150, 220, 150, 255))

        # We blur the pattern slightly
        self._pattern = pattern.filter(ImageFilter.GaussianBlur(0.5))

    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        if target_x is not None and target_y is not None:
            tx = max(0, min(self.width, target_x))
            ty = max(0, min(self.height, target_y))
            self.idle_mode = "idle"
            self.idle_glance_started_at = None
            self.idle_next_switch = now + random.uniform(2.0, 5.0)
        else:
            if now >= self.idle_next_switch:
                modes = ["idle", "glance"]
                modes.remove(self.idle_mode) if self.idle_mode in modes else None
                self.idle_mode = random.choice(modes)
                self.idle_next_switch = now + random.uniform(2.0, 5.0)

            if self.idle_mode == "glance":
                if self.idle_glance_started_at is None:
                    self.idle_glance_started_at = now
                    self.idle_glance_duration = random.uniform(1.2, 2.8)
                    self.idle_glance_origin_x = self.iris_x
                    self.idle_glance_origin_y = self.iris_y
                    angle = random.uniform(0, math.pi * 2)
                    reach = random.uniform(25, settings.max_pupil_offset * 2)
                    self.idle_glance_target_x = int(self.cx + math.cos(angle) * reach)
                    self.idle_glance_target_y = int(self.cy + math.sin(angle) * reach)

                if now - self.idle_glance_started_at >= self.idle_glance_duration:
                    self.idle_glance_started_at = None
                    self.idle_mode = "idle"
                    self.idle_next_switch = now + random.uniform(1.0, 3.0)
                    tx, ty = int(self.idle_glance_origin_x), int(self.idle_glance_origin_y)
                else:
                    tx, ty = self.idle_glance_target_x, self.idle_glance_target_y
            else:
                tx, ty = self.cx, self.cy

        self.iris_x += (tx - self.iris_x) * settings.smoothing
        self.iris_y += (ty - self.iris_y) * settings.smoothing

    def gaze(self) -> tuple[float, float]:
        gx = (self.iris_x - self.cx) / max(1, settings.max_pupil_offset * 2)
        gy = (self.iris_y - self.cy) / max(1, settings.max_pupil_offset * 2)
        return max(-1.0, min(1.0, gx)), max(-1.0, min(1.0, gy))

    def render(self) -> Image.Image:
        gx, gy = self.gaze()
        
        # Shift the pattern based on gaze
        shift_x = int(gx * 50) + self.width // 2
        shift_y = int(gy * 50) + self.height // 2
        
        # Crop the relevant part of the pre-rendered pattern
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        crop = self._pattern.crop((shift_x, shift_y, shift_x + self.width, shift_y + self.height))
        
        # Apply a spherical shading to make it look like a globe
        arr = np.asarray(crop).astype(float)
        yy, xx = np.mgrid[0:self.height, 0:self.width]
        R = min(self.width, self.height) * 0.8
        dx = xx - self.cx
        dy = yy - self.cy
        d = np.sqrt(dx*dx + dy*dy) / R
        
        # Shading
        shade = np.clip(1.0 - d**2, 0, 1)
        arr = arr * shade[..., None]
        
        return Image.fromarray(arr.astype(np.uint8))
