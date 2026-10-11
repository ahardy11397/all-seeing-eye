from __future__ import annotations
import math
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from config import settings

class SpiderEye:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2
        
        # We will use iris_x, iris_y to represent the "gaze" of the spider
        self.iris_x = self.cx
        self.iris_y = self.cy
        
        self.idle_mode = "idle"
        self.idle_scan_angle = 0.0
        self.idle_scan_speed = random.uniform(0.4, 0.9)
        self.idle_next_switch = time.time() + random.uniform(2.0, 5.0)
        self.idle_glance_target_x = self.cx
        self.idle_glance_target_y = self.cy
        self.idle_glance_origin_x = self.cx
        self.idle_glance_origin_y = self.cy
        self.idle_glance_started_at = None
        self.idle_glance_duration = 0.0
        
        self._build_static_layers()

    def _build_static_layers(self) -> None:
        # Background: dark hairy texture
        bg = Image.new("RGB", (self.width, self.height), (35, 30, 30))
        draw = ImageDraw.Draw(bg)
        rng = np.random.default_rng(42)
        for _ in range(1500):
            x1 = rng.uniform(0, self.width)
            y1 = rng.uniform(0, self.height)
            length = rng.uniform(5, 25)
            angle = rng.uniform(0, math.pi * 2)
            x2 = x1 + math.cos(angle) * length
            y2 = y1 + math.sin(angle) * length
            color = rng.choice([(45, 40, 40), (60, 50, 50), (25, 20, 20)])
            draw.line([x1, y1, x2, y2], fill=tuple(color), width=1)
        self._bg = bg
        
        # Eyes configuration: (offset_x, offset_y, radius)
        # Jumping spiders have 2 huge anterior median eyes, 2 smaller anterior lateral, 4 small others.
        self.eyes_config = [
            # Two main eyes
            (-60, 0, 45), (60, 0, 45),
            # Two lateral eyes
            (-150, -20, 25), (150, -20, 25),
            # Four smaller eyes on top
            (-80, -80, 15), (80, -80, 15),
            (-130, -70, 12), (130, -70, 12)
        ]
        
        # Specular highlight sprite
        hl_size = 40
        hl = Image.new("RGBA", (hl_size, hl_size), (0, 0, 0, 0))
        hdraw = ImageDraw.Draw(hl)
        hdraw.ellipse([5, 5, 25, 20], fill=(255, 255, 255, 220))
        hdraw.ellipse([20, 15, 28, 23], fill=(255, 255, 255, 160))
        self._hl = hl.filter(ImageFilter.GaussianBlur(1))

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
                    reach = random.uniform(25, settings.max_pupil_offset)
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
        gx = (self.iris_x - self.cx) / max(1, settings.max_pupil_offset)
        gy = (self.iris_y - self.cy) / max(1, settings.max_pupil_offset)
        return max(-1.0, min(1.0, gx)), max(-1.0, min(1.0, gy))

    def render(self) -> Image.Image:
        canvas = self._bg.copy()
        draw = ImageDraw.Draw(canvas)
        
        gx, gy = self.gaze()
        
        # When spiders look around, they turn their whole head.
        # We can simulate this by shifting all eyes slightly.
        head_shift_x = int(gx * 30)
        head_shift_y = int(gy * 30)
        
        for ox, oy, r in self.eyes_config:
            ex = self.cx + ox + head_shift_x
            ey = self.cy + oy + head_shift_y
            
            # Base black eye
            draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(30, 10, 10))
            
            # Soft inner glow to make it look like a lens
            draw.ellipse([ex - r*0.8, ey - r*0.8, ex + r*0.8, ey + r*0.8], fill=(80, 20, 20))
            draw.ellipse([ex - r*0.5, ey - r*0.5, ex + r*0.5, ey + r*0.5], fill=(140, 30, 30))
            
            # Specular highlight shifts with gaze
            hl_shift_x = int(gx * r * 0.4)
            hl_shift_y = int(gy * r * 0.4)
            
            # Scale highlight relative to eye size
            scale = r / 45.0
            hl_w = int(40 * scale)
            hl_h = int(40 * scale)
            
            if hl_w > 0 and hl_h > 0:
                hl_resized = self._hl.resize((hl_w, hl_h), Image.Resampling.BILINEAR)
                hl_x = int(ex - hl_w/2 - r*0.2 + hl_shift_x)
                hl_y = int(ey - hl_h/2 - r*0.2 + hl_shift_y)
                canvas.paste(hl_resized, (hl_x, hl_y), hl_resized)
                
        return canvas
