from __future__ import annotations
import math
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from config import settings

class DancingSkeleton:
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
                    self.idle_glance_target_x = random.randint(100, self.width - 100)

                if now - self.idle_glance_started_at >= self.idle_glance_duration:
                    self.idle_glance_started_at = None
                    self.idle_mode = "idle"
                    self.idle_next_switch = now + random.uniform(1.0, 3.0)
                    tx = int(self.idle_glance_origin_x)
                else:
                    tx = self.idle_glance_target_x
            else:
                tx = self.cx

        # Move horizontally towards target
        dx = tx - self.iris_x
        self.iris_x += dx * 0.05
            
    def gaze(self) -> tuple[float, float]:
        gx = (self.iris_x - self.cx) / (self.width / 2.0)
        return max(-1.0, min(1.0, gx)), 0.0

    def render(self) -> Image.Image:
        out = Image.new("RGB", (self.width, self.height), (15, 10, 25)) # dark purple/disco background
        draw = ImageDraw.Draw(out)
        
        # Disco floor lines
        for y in range(self.cy + 100, self.height, 40):
            draw.line([0, y, self.width, y], fill=(40, 20, 60), width=2)
            
        # Draw Skeleton
        fx = int(self.iris_x)
        fy = self.cy + 50
        
        t = time.time()
        
        # Bobbing
        bob = math.sin(t * 12) * 10
        fy += int(bob)
        
        # Dance phase for arms and legs
        dance1 = math.sin(t * 8)
        dance2 = math.cos(t * 8)
        
        # Head (Skull)
        draw.ellipse([fx - 30, fy - 180, fx + 30, fy - 120], fill=(220, 220, 220))
        # Eyes
        draw.ellipse([fx - 15, fy - 160, fx - 5, fy - 150], fill=(0, 0, 0))
        draw.ellipse([fx + 5, fy - 160, fx + 15, fy - 150], fill=(0, 0, 0))
        # Jaw / Teeth
        draw.rectangle([fx - 15, fy - 130, fx + 15, fy - 110], fill=(220, 220, 220))
        draw.line([fx - 10, fy - 120, fx + 10, fy - 120], fill=(0, 0, 0), width=2)
        
        # Spine
        draw.line([fx, fy - 110, fx, fy - 40], fill=(220, 220, 220), width=8)
        # Ribs
        for ry in range(fy - 100, fy - 50, 15):
            rib_w = 25 - abs(fy - 75 - ry) * 0.5
            draw.line([fx - rib_w, ry, fx + rib_w, ry], fill=(220, 220, 220), width=5)
            
        # Arms
        # Shoulders
        draw.line([fx - 35, fy - 100, fx + 35, fy - 100], fill=(220, 220, 220), width=6)
        
        # Left Arm (waving)
        elbow_lx = fx - 45 - dance1 * 20
        elbow_ly = fy - 80 + dance2 * 20
        draw.line([fx - 35, fy - 100, elbow_lx, elbow_ly], fill=(220, 220, 220), width=6)
        draw.line([elbow_lx, elbow_ly, elbow_lx - 20 - dance2 * 30, elbow_ly - 30 - dance1 * 30], fill=(220, 220, 220), width=6)

        # Right Arm (waving opposite)
        elbow_rx = fx + 45 + dance2 * 20
        elbow_ry = fy - 80 - dance1 * 20
        draw.line([fx + 35, fy - 100, elbow_rx, elbow_ry], fill=(220, 220, 220), width=6)
        draw.line([elbow_rx, elbow_ry, elbow_rx + 20 - dance1 * 30, elbow_ry - 30 + dance2 * 30], fill=(220, 220, 220), width=6)

        # Hips
        draw.line([fx - 20, fy - 40, fx + 20, fy - 40], fill=(220, 220, 220), width=8)

        # Legs (dancing jig)
        knee_lx = fx - 25 - dance2 * 15
        knee_ly = fy + 10 + dance1 * 15
        draw.line([fx - 15, fy - 40, knee_lx, knee_ly], fill=(220, 220, 220), width=7)
        draw.line([knee_lx, knee_ly, knee_lx - 10, knee_ly + 50 - dance1 * 20], fill=(220, 220, 220), width=7)

        knee_rx = fx + 25 + dance1 * 15
        knee_ry = fy + 10 - dance2 * 15
        draw.line([fx + 15, fy - 40, knee_rx, knee_ry], fill=(220, 220, 220), width=7)
        draw.line([knee_rx, knee_ry, knee_rx + 10, knee_ry + 50 + dance2 * 20], fill=(220, 220, 220), width=7)

        return out
