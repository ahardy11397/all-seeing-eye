from pathlib import Path
import re

# 1. Fix DancingSkeleton
skel_path = Path("src/dancing_skeleton.py")
skel_code = skel_path.read_text()

gaze_method = """    def gaze(self) -> tuple[float, float]:
        gx = (self.iris_x - self.cx) / (self.width / 2.0)
        return max(-1.0, min(1.0, gx)), 0.0

    def render"""

if "def gaze" not in skel_code:
    skel_code = skel_code.replace("    def render", gaze_method)
    skel_path.write_text(skel_code)
    print("Fixed DancingSkeleton gaze method.")

# 2. Rewrite Skull to use 3D image
skull_code = """from __future__ import annotations
import math
import random
import time
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from config import settings

class Skull:
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
        img_path = "skull.jpg"
        if os.path.exists(img_path):
            img = Image.open(img_path).convert("RGB")
            
            # Resize image to fit screen while maintaining aspect ratio
            # Let's crop it to be a square matching the smaller dimension
            min_dim = min(self.width, self.height)
            img = img.resize((min_dim, min_dim), Image.LANCZOS)
            
            # create black background and paste the centered skull
            self._skull_base = Image.new("RGB", (self.width, self.height), (0, 0, 0))
            offset_x = (self.width - min_dim) // 2
            offset_y = (self.height - min_dim) // 2
            self._skull_base.paste(img, (offset_x, offset_y))
            
            # Sockets are at roughly 35% and 65% width, 45% height of the image
            self.lx = offset_x + int(min_dim * 0.35)
            self.rx = offset_x + int(min_dim * 0.65)
            self.ly = offset_y + int(min_dim * 0.45)
            self.ry = offset_y + int(min_dim * 0.45)
        else:
            self._skull_base = Image.new("RGB", (self.width, self.height), (0, 0, 0))
            self.lx, self.ly = self.cx - 50, self.cy - 30
            self.rx, self.ry = self.cx + 50, self.cy - 30

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
        
        # shift the skull base slightly to simulate head turning
        head_shift_x = int(gx * 8)
        head_shift_y = int(gy * 8)
        
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        out.paste(self._skull_base, (head_shift_x, head_shift_y))
        
        # Draw glowing red eyes in the sockets that move much further
        draw = ImageDraw.Draw(out)
        
        eye_shift_x = int(gx * 25) + head_shift_x
        eye_shift_y = int(gy * 25) + head_shift_y
        
        glow_r = min(self.width, self.height) // 25
        
        # Left glow
        lx = self.lx + eye_shift_x
        ly = self.ly + eye_shift_y
        draw.ellipse([lx - glow_r, ly - glow_r, lx + glow_r, ly + glow_r], fill=(255, 30, 30))
        draw.ellipse([lx - glow_r//2, ly - glow_r//2, lx + glow_r//2, ly + glow_r//2], fill=(255, 200, 200))
        
        # Right glow
        rx = self.rx + eye_shift_x
        ry = self.ry + eye_shift_y
        draw.ellipse([rx - glow_r, ry - glow_r, rx + glow_r, ry + glow_r], fill=(255, 30, 30))
        draw.ellipse([rx - glow_r//2, ry - glow_r//2, rx + glow_r//2, ry + glow_r//2], fill=(255, 200, 200))
        
        # Soften the glow slightly (blur 2px) but we don't want to blur the high quality skull!
        # Instead of blurring the whole image, we'll draw the glow on a separate layer, blur it, and paste it.
        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)
        
        gdraw.ellipse([lx - glow_r*2, ly - glow_r*2, lx + glow_r*2, ly + glow_r*2], fill=(255, 10, 10, 100))
        gdraw.ellipse([lx - glow_r, ly - glow_r, lx + glow_r, ly + glow_r], fill=(255, 80, 80, 200))
        gdraw.ellipse([lx - glow_r//3, ly - glow_r//3, lx + glow_r//3, ly + glow_r//3], fill=(255, 255, 255, 255))
        
        gdraw.ellipse([rx - glow_r*2, ry - glow_r*2, rx + glow_r*2, ry + glow_r*2], fill=(255, 10, 10, 100))
        gdraw.ellipse([rx - glow_r, ry - glow_r, rx + glow_r, ry + glow_r], fill=(255, 80, 80, 200))
        gdraw.ellipse([rx - glow_r//3, ry - glow_r//3, rx + glow_r//3, ry + glow_r//3], fill=(255, 255, 255, 255))
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(5))
        
        # We need to re-paste the unblurred skull and composite the blurred glow
        out2 = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        out2.paste(self._skull_base, (head_shift_x, head_shift_y))
        out2.paste(glow_layer, (0, 0), glow_layer)
        
        return out2
"""
Path("src/skull.py").write_text(skull_code)
print("Rewrote Skull to use 3D image.")
