import math
import random
import time
from pathlib import Path
import re

# --- Create Skull ---
skull_code = """from __future__ import annotations
import math
import random
import time
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
        # We will build the base skull image (front facing)
        # Then during render we'll shift it and draw the glowing eyes
        base = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(base)
        
        # Skull dimensions
        sw = 260
        sh = 260
        jaw_w = 140
        jaw_h = 100
        
        cx, cy = self.cx, self.cy - 30
        
        # Cranium
        draw.ellipse([cx - sw//2, cy - sh//2, cx + sw//2, cy + sh//2], fill=(220, 220, 210, 255))
        # Jaw
        draw.rectangle([cx - jaw_w//2, cy + sh//3, cx + jaw_w//2, cy + sh//2 + jaw_h], fill=(220, 220, 210, 255), outline=(220, 220, 210, 255))
        
        # Cheekbones curve
        draw.ellipse([cx - sw//2 - 10, cy + 20, cx - sw//2 + 80, cy + 140], fill=(0, 0, 0, 255))
        draw.ellipse([cx + sw//2 - 80, cy + 20, cx + sw//2 + 10, cy + 140], fill=(0, 0, 0, 255))
        
        # Re-fill cheekbones to make them distinct
        draw.ellipse([cx - sw//2 + 10, cy + 40, cx - sw//4 + 20, cy + 100], fill=(220, 220, 210, 255))
        draw.ellipse([cx + sw//4 - 20, cy + 40, cx + sw//2 - 10, cy + 100], fill=(220, 220, 210, 255))

        # Eye sockets
        self.eye_offset_x = 60
        self.eye_offset_y = 10
        self.eye_r = 45
        
        # Left eye socket
        draw.ellipse([cx - self.eye_offset_x - self.eye_r, cy - self.eye_offset_y - self.eye_r, 
                      cx - self.eye_offset_x + self.eye_r, cy - self.eye_offset_y + self.eye_r], fill=(20, 20, 20, 255))
        # Right eye socket
        draw.ellipse([cx + self.eye_offset_x - self.eye_r, cy - self.eye_offset_y - self.eye_r, 
                      cx + self.eye_offset_x + self.eye_r, cy - self.eye_offset_y + self.eye_r], fill=(20, 20, 20, 255))
        
        # Nose cavity (upside down heart/spade)
        draw.polygon([(cx, cy + 40), (cx - 20, cy + 90), (cx + 20, cy + 90)], fill=(20, 20, 20, 255))
        
        # Teeth lines
        jaw_bottom = cy + sh//2 + jaw_h
        jaw_top = cy + sh//3 + 40
        draw.line([cx - jaw_w//2 + 20, (jaw_top+jaw_bottom)//2, cx + jaw_w//2 - 20, (jaw_top+jaw_bottom)//2], fill=(50, 50, 50, 255), width=4)
        for tx in range(cx - jaw_w//2 + 30, cx + jaw_w//2 - 20, 20):
            draw.line([tx, jaw_top + 10, tx, jaw_bottom - 10], fill=(50, 50, 50, 255), width=4)
            
        # Add some grit
        self._skull_base = base.filter(ImageFilter.GaussianBlur(1))

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
        head_shift_x = int(gx * 20)
        head_shift_y = int(gy * 20)
        
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        out.paste(self._skull_base, (head_shift_x, head_shift_y), self._skull_base)
        
        # Draw glowing red eyes in the sockets that move much further
        draw = ImageDraw.Draw(out)
        
        eye_shift_x = int(gx * 35) + head_shift_x
        eye_shift_y = int(gy * 35) + head_shift_y
        
        glow_r = 15
        cy = self.cy - 30
        
        # Left glow
        lx = self.cx - self.eye_offset_x + eye_shift_x
        ly = cy - self.eye_offset_y + eye_shift_y
        draw.ellipse([lx - glow_r, ly - glow_r, lx + glow_r, ly + glow_r], fill=(255, 30, 30))
        draw.ellipse([lx - glow_r//2, ly - glow_r//2, lx + glow_r//2, ly + glow_r//2], fill=(255, 200, 200))
        
        # Right glow
        rx = self.cx + self.eye_offset_x + eye_shift_x
        ry = cy - self.eye_offset_y + eye_shift_y
        draw.ellipse([rx - glow_r, ry - glow_r, rx + glow_r, ry + glow_r], fill=(255, 30, 30))
        draw.ellipse([rx - glow_r//2, ry - glow_r//2, rx + glow_r//2, ry + glow_r//2], fill=(255, 200, 200))
        
        # Soften the glow
        return out.filter(ImageFilter.GaussianBlur(1.5))
"""
Path("src/skull.py").write_text(skull_code)


# --- Create DancingSkeleton ---
dance_code = """from __future__ import annotations
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
"""
Path("src/dancing_skeleton.py").write_text(dance_code)


# --- Patch Dispatchers ---
def patch_file(filepath, var_name, eye_creation_args):
    p = Path(filepath)
    if not p.exists(): return
    content = p.read_text()
    
    if "from skull import Skull" not in content:
        content = content.replace("from joker_eye import JokerEye", 
                                  "from joker_eye import JokerEye\nfrom skull import Skull\nfrom dancing_skeleton import DancingSkeleton")

    pattern = re.compile(
        r'(\s*)elif current_eye_type == "joker": ' + re.escape(var_name) + r' = JokerEye\(' + re.escape(eye_creation_args) + r'\)',
        re.DOTALL
    )
    
    def repl(m):
        ind = m.group(1)
        return f"""{ind}elif current_eye_type == "joker": {var_name} = JokerEye({eye_creation_args})
{ind}elif current_eye_type == "skull": {var_name} = Skull({eye_creation_args})
{ind}elif current_eye_type == "dancing_skeleton": {var_name} = DancingSkeleton({eye_creation_args})"""
    
    content, count = pattern.subn(repl, content)
    if count == 0:
        print(f"Failed to patch {filepath}")
    else:
        print(f"Patched {filepath}")
        
    p.write_text(content)

patch_file("src/main.py", "eye", "width, height")
patch_file("src/dashboard.py", "self.eye", "settings.width, settings.height")
patch_file("run_stream.py", "eye", "settings.width, settings.height")

# dashboard.py dropdown
d = Path("src/dashboard.py").read_text()
if '"skull"' not in d:
    d = d.replace('"joker"', '"joker", "skull", "dancing_skeleton"')
    Path("src/dashboard.py").write_text(d)

# dashboard_server.py HTML dropdown
ds = Path("src/dashboard_server.py").read_text()
if 'value="skull"' not in ds:
    options = """        <option value="joker">Joker (Heath Ledger)</option>
        <option value="skull">Skull</option>
        <option value="dancing_skeleton">Dancing Skeleton</option>"""
    ds = ds.replace('<option value="joker">Joker (Heath Ledger)</option>', options)
    Path("src/dashboard_server.py").write_text(ds)

print("Created Skull and DancingSkeleton and patched dispatches.")

