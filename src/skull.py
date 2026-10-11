from __future__ import annotations
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
        self.frames = []
        self.sockets = {}
        gif_path = "skull_human.gif"
        import os
        from PIL import Image
        
        sockets_256 = {
            0: [(79, 86)],
            1: [(64, 86), (143, 88)],
            2: [(85, 86), (171, 86)],
            3: [(113, 88), (192, 86)],
            4: [(177, 86)]
        }
        
        if os.path.exists(gif_path):
            img = Image.open(gif_path)
            
            min_dim = min(self.width, self.height)
            scale = min_dim / 256.0
            offset_x = (self.width - min_dim) // 2
            offset_y = (self.height - min_dim) // 2
            
            for i in range(5):
                try:
                    img.seek(i)
                except EOFError:
                    break
                frame = img.convert("RGB")
                frame = frame.resize((min_dim, min_dim), Image.LANCZOS)
                
                canvas = Image.new("RGB", (self.width, self.height), (0, 0, 0))
                canvas.paste(frame, (offset_x, offset_y))
                self.frames.append(canvas)
                
                scaled_pts = []
                for x, y in sockets_256[i]:
                    sx = offset_x + int(x * scale)
                    sy = offset_y + int(y * scale)
                    scaled_pts.append((sx, sy))
                self.sockets[i] = scaled_pts
                
        else:
            self.frames = [Image.new("RGB", (self.width, self.height), (0, 0, 0))]
            self.sockets = {0: [(self.cx, self.cy)]}

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
        
        # gx is -1 to 1.
        # -1 = Left Profile (frame 0)
        # -0.5 = Slight Left (frame 1)
        # 0 = Straight (frame 2)
        # 0.5 = Slight Right (frame 3)
        # 1 = Right Profile (frame 4)
        
        # Map gx to frame index (0 to 4)
        val = (gx + 1.0) / 2.0  # 0 to 1
        frame_idx = int(round(val * 4))
        frame_idx = max(0, min(4, frame_idx))
        
        if not self.frames:
            return Image.new("RGB", (self.width, self.height), (0, 0, 0))
            
        # Limit frame_idx to available frames
        frame_idx = min(frame_idx, len(self.frames) - 1)
        
        out = self.frames[frame_idx].copy()
        
        # Slight vertical tilt (parallax) using Y translation
        if gy != 0:
            import numpy as np
            import cv2
            arr = np.array(out)
            shift_y = int(gy * min(self.width, self.height) * 0.05)
            M = np.float32([[1, 0, 0], [0, 1, shift_y]])
            arr = cv2.warpAffine(arr, M, (self.width, self.height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
            from PIL import ImageDraw, ImageFilter
            out = Image.fromarray(arr)
        else:
            from PIL import ImageDraw, ImageFilter
            shift_y = 0
            
        # Draw glowing eyes!
        draw = ImageDraw.Draw(out)
        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)
        
        glow_r = min(self.width, self.height) // 25
        
        # The eye moves slightly within the socket based on gaze
        eye_shift_x = int(gx * min(self.width, self.height) * 0.03)
        eye_shift_y = int(gy * min(self.width, self.height) * 0.03)
        
        if frame_idx in self.sockets:
            for sx, sy in self.sockets[frame_idx]:
                px = sx + eye_shift_x
                py = sy + eye_shift_y + shift_y
                
                # Core
                gdraw.ellipse([px - glow_r*2, py - glow_r*2, px + glow_r*2, py + glow_r*2], fill=(255, 10, 10, 100))
                gdraw.ellipse([px - glow_r, py - glow_r, px + glow_r, py + glow_r], fill=(255, 80, 80, 200))
                gdraw.ellipse([px - glow_r//3, py - glow_r//3, px + glow_r//3, py + glow_r//3], fill=(255, 255, 255, 255))
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(5))
        out.paste(glow_layer, (0, 0), glow_layer)
        
        return out