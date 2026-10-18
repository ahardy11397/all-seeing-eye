from __future__ import annotations
import math
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from config import settings

class CreepyFigure:
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
        self.idle_glance_origin_x = self.cx
        self.idle_glance_started_at = None
        self.idle_glance_duration = 0.0
        
        self._build_static_layers()

    def _build_static_layers(self) -> None:
        # Glowing gradient background
        bg = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        
        yy, xx = np.mgrid[0:self.height, 0:self.width]
        # Radial gradient from center bottom
        center_x = self.cx
        center_y = self.height + 50
        dist = np.sqrt((xx - center_x)**2 + (yy - center_y)**2) / max(self.width, self.height)
        
        # Intense glowing red/orange fading into dark black
        glow = np.clip(1.0 - dist*1.2, 0, 1) ** 1.5
        
        r = (glow * 255).astype(np.uint8)
        g = (glow * 100).astype(np.uint8)
        b = (glow * 30).astype(np.uint8)
        
        arr = np.dstack([r, g, b])
        self._bg = Image.fromarray(arr, "RGB")
        
        # Create a large shapeless blurry shadow template
        self.shadow_w, self.shadow_h = 600, 800
        shadow = Image.new("RGBA", (self.shadow_w, self.shadow_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        
        # Draw a very organic, blobby shape in the center
        draw.ellipse([150, 150, 450, 650], fill=(0, 0, 0, 240))
        draw.ellipse([100, 250, 400, 550], fill=(0, 0, 0, 200))
        draw.ellipse([200, 100, 500, 500], fill=(0, 0, 0, 200))
        draw.ellipse([180, 300, 480, 700], fill=(0, 0, 0, 220))
        
        # Heavy blur to make it completely shapeless with no hard edges
        self._shadow = shadow.filter(ImageFilter.GaussianBlur(80))

    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        if target_x is not None:
            tx = max(0, min(self.width, target_x))
            self.idle_mode = "idle"
            self.idle_glance_started_at = None
            self.idle_next_switch = now + random.uniform(2.0, 5.0)
        else:
            if now >= self.idle_next_switch:
                modes = ["idle", "walk"]
                modes.remove(self.idle_mode) if self.idle_mode in modes else None
                self.idle_mode = random.choice(modes)
                self.idle_next_switch = now + random.uniform(2.0, 5.0)

            if self.idle_mode == "walk":
                if self.idle_glance_started_at is None:
                    self.idle_glance_started_at = now
                    self.idle_glance_duration = random.uniform(3.0, 6.0)
                    self.idle_glance_origin_x = self.iris_x
                    self.idle_glance_target_x = random.randint(-100, self.width + 100)

                if now - self.idle_glance_started_at >= self.idle_glance_duration:
                    self.idle_glance_started_at = None
                    self.idle_mode = "idle"
                    self.idle_next_switch = now + random.uniform(1.0, 3.0)
                    tx = int(self.idle_glance_origin_x)
                else:
                    tx = self.idle_glance_target_x
            else:
                tx = self.cx

        # Extremely slow smooth movement for a creeping shadow
        dx = tx - self.iris_x
        step = dx * 0.01
        max_speed = 1.0
        if abs(step) > max_speed:
            step = math.copysign(max_speed, step)
        self.iris_x += step
            
    def render(self) -> Image.Image:
        canvas = self._bg.copy()
        
        # Shadow position
        fx = int(self.iris_x) - self.shadow_w // 2
        # Slight organic vertical bobbing
        fy = (self.height - self.shadow_h + 80) + int(math.sin(time.time() * 2) * 15)
        
        # Paste the blurry shadow over the glowing background
        canvas.paste(self._shadow, (fx, fy), self._shadow)
        
        return canvas
