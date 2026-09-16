from pathlib import Path
import re

# --- Update snake_eye.py ---
# Let's make the snake eye more distinct: 
# 1. Very bright toxic green iris
# 2. Narrower slit pupil
# 3. Yellow/green sclera instead of white with blood vessels
snake_path = Path("src/snake_eye.py")
snake_code = snake_path.read_text()

# Change the pupil slit to be even narrower
snake_code = snake_code.replace("psize / 2 - ps * 0.15", "psize / 2 - ps * 0.08")
snake_code = snake_code.replace("psize / 2 + ps * 0.15", "psize / 2 + ps * 0.08")

# Change the base sclera color to a sickly yellow/green, removing the white
snake_code = re.sub(
    r"base = 252\.0 - 30\.0 \* t \*\* 1\.8", 
    "base = 180.0 - 50.0 * t ** 1.8", 
    snake_code
)
snake_code = re.sub(
    r"r = np\.clip\(base \* 0\.1, 0, 255\)",
    "r = np.clip(base * 0.6 + 40, 0, 255)",
    snake_code
)
snake_code = re.sub(
    r"g = np\.clip\(base \* 0\.2, 0, 255\)",
    "g = np.clip(base * 0.9 + 20, 0, 255)",
    snake_code
)
snake_code = re.sub(
    r"b = np\.clip\(base \* 0\.1, 0, 255\)",
    "b = np.clip(base * 0.2, 0, 255)",
    snake_code
)

# Darken the vessels slightly and make them more yellow-green
snake_code = snake_code.replace("vessel_r = 150.0", "vessel_r = 80.0")
snake_code = snake_code.replace("vessel_g = 180.0", "vessel_g = 120.0")
snake_code = snake_code.replace("vessel_b = 0.0", "vessel_b = 20.0")

# Change Iris color to vivid neon green / yellow
snake_code = snake_code.replace("np.array([220, 255, 0], dtype=float)", "np.array([120, 255, 30], dtype=float)")
snake_code = snake_code.replace("np.array([0, 40, 10], dtype=float)", "np.array([10, 80, 20], dtype=float)")

snake_path.write_text(snake_code)


# --- Update spider_eye.py ---
spider_path = Path("src/spider_eye.py")
spider_code = spider_path.read_text()

# Brighter background, dark greyish brown instead of pitch black
spider_code = spider_code.replace("Image.new(\"RGB\", (self.width, self.height), (15, 10, 10))", "Image.new(\"RGB\", (self.width, self.height), (35, 30, 30))")
spider_code = spider_code.replace("rng.choice([(25, 20, 20), (35, 30, 30), (10, 5, 5)])", "rng.choice([(45, 40, 40), (60, 50, 50), (25, 20, 20)])")

# Brighter, more distinct eyes (deep red glowing lenses)
spider_code = spider_code.replace("fill=(10, 5, 5)", "fill=(30, 10, 10)")
spider_code = spider_code.replace("fill=(20, 10, 15)", "fill=(80, 20, 20)")
spider_code = spider_code.replace("fill=(30, 15, 20)", "fill=(140, 30, 30)")
# Specular highlight stronger
spider_code = spider_code.replace("fill=(255, 255, 255, 180)", "fill=(255, 255, 255, 220)")
spider_code = spider_code.replace("fill=(255, 255, 255, 100)", "fill=(255, 255, 255, 160)")

spider_path.write_text(spider_code)


# --- Update creepy_figure.py ---
creepy_path = Path("src/creepy_figure.py")
creepy_code = """from __future__ import annotations
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
        self.shadow_w, self.shadow_h = 350, 500
        shadow = Image.new("RGBA", (self.shadow_w, self.shadow_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        
        # Draw a very organic, blobby shape
        draw.ellipse([50, 50, 300, 450], fill=(0, 0, 0, 240))
        draw.ellipse([0, 100, 250, 350], fill=(0, 0, 0, 200))
        draw.ellipse([100, 0, 350, 300], fill=(0, 0, 0, 200))
        draw.ellipse([80, 200, 320, 500], fill=(0, 0, 0, 220))
        
        # Heavy blur to make it completely shapeless
        self._shadow = shadow.filter(ImageFilter.GaussianBlur(35))

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
        self.iris_x += dx * 0.03
            
    def render(self) -> Image.Image:
        canvas = self._bg.copy()
        
        # Shadow position
        fx = int(self.iris_x) - self.shadow_w // 2
        # Slight organic vertical bobbing
        fy = (self.height - self.shadow_h + 80) + int(math.sin(time.time() * 2) * 15)
        
        # Paste the blurry shadow over the glowing background
        canvas.paste(self._shadow, (fx, fy), self._shadow)
        
        return canvas
"""
creepy_path.write_text(creepy_code)

print("Updated eyes!")
