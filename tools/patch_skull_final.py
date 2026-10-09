import re
from pathlib import Path

p = Path("src/skull.py")
code = p.read_text()

build_static_new = """    def _build_static_layers(self) -> None:
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
            self.sockets = {0: [(self.cx, self.cy)]}"""

code = re.sub(r"    def _build_static_layers\(self\) -> None:.*?(?=    def update)", build_static_new + "\n\n", code, flags=re.DOTALL)

render_new = """    def render(self) -> Image.Image:
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
        
        return out"""

code = re.sub(r"    def render\(self\) -> Image\.Image:.*", render_new, code, flags=re.DOTALL)

p.write_text(code)
print("Patched skull.py with human skull spritesheet + glowing eyes")
