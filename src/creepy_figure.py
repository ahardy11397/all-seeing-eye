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
        
        self.leg_phase = 0.0
        self._build_static_layers()

    def _build_static_layers(self) -> None:
        # Dimly backlit room (window in the background)
        bg = Image.new("RGB", (self.width, self.height), (5, 5, 5))
        draw = ImageDraw.Draw(bg)
        
        # Draw a window
        win_w, win_h = 200, 300
        win_x, win_y = self.cx - win_w//2, self.cy - win_h//2 - 50
        draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(40, 50, 60))
        # Window bars
        draw.rectangle([win_x + win_w//2 - 5, win_y, win_x + win_w//2 + 5, win_y + win_h], fill=(0, 0, 0))
        draw.rectangle([win_x, win_y + win_h//2 - 5, win_x + win_w, win_y + win_h//2 + 5], fill=(0, 0, 0))
        
        # Floor
        draw.polygon([(0, win_y + win_h), (self.width, win_y + win_h), (self.width, self.height), (0, self.height)], fill=(10, 10, 15))
        
        # Vignette / blur for atmosphere
        self._bg = bg.filter(ImageFilter.GaussianBlur(3))

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
                    self.idle_glance_target_x = random.randint(50, self.width - 50)

                if now - self.idle_glance_started_at >= self.idle_glance_duration:
                    self.idle_glance_started_at = None
                    self.idle_mode = "idle"
                    self.idle_next_switch = now + random.uniform(1.0, 3.0)
                    tx = int(self.idle_glance_origin_x)
                else:
                    tx = self.idle_glance_target_x
            else:
                tx = self.cx

        # Very slow smooth movement
        dx = tx - self.iris_x
        self.iris_x += dx * 0.05
        
        # Leg animation phase based on movement speed
        if abs(dx) > 1.0:
            self.leg_phase += abs(dx) * 0.02
        else:
            self.leg_phase = 0.0
            
    def render(self) -> Image.Image:
        canvas = self._bg.copy()
        draw = ImageDraw.Draw(canvas)
        
        # Figure position
        fx = int(self.iris_x)
        fy = self.cy + 50
        
        # Draw creepy figure (tall thin silhouette)
        # Head
        draw.ellipse([fx - 15, fy - 180, fx + 15, fy - 140], fill=(0, 0, 0))
        # Body
        draw.line([fx, fy - 140, fx, fy - 40], fill=(0, 0, 0), width=20)
        # Arms
        arm_swing = math.sin(self.leg_phase) * 20
        draw.line([fx, fy - 130, fx - 20 - arm_swing, fy - 60], fill=(0, 0, 0), width=6)
        draw.line([fx, fy - 130, fx + 20 + arm_swing, fy - 60], fill=(0, 0, 0), width=6)
        # Legs
        leg_swing = math.sin(self.leg_phase) * 30
        draw.line([fx, fy - 40, fx - leg_swing, fy + 40], fill=(0, 0, 0), width=8)
        draw.line([fx, fy - 40, fx + leg_swing, fy + 40], fill=(0, 0, 0), width=8)
        
        # Dim glow from eyes maybe?
        draw.ellipse([fx - 6, fy - 165, fx - 2, fy - 160], fill=(150, 0, 0))
        draw.ellipse([fx + 2, fy - 165, fx + 6, fy - 160], fill=(150, 0, 0))

        # Add some noise/film grain effect by blending a slightly randomized dark layer
        return canvas
