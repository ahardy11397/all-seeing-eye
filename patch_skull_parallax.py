import re
from pathlib import Path

p = Path("src/skull.py")
code = p.read_text()

build_static_new = """    def _build_static_layers(self) -> None:
        img_path = "skull.jpg"
        import os
        from PIL import Image
        import numpy as np
        if os.path.exists(img_path):
            img = Image.open(img_path).convert("RGB")
            
            min_dim = min(self.width, self.height)
            img = img.resize((min_dim, min_dim), Image.LANCZOS)
            
            self._skull_base = Image.new("RGB", (self.width, self.height), (0, 0, 0))
            offset_x = (self.width - min_dim) // 2
            offset_y = (self.height - min_dim) // 2
            self._skull_base.paste(img, (offset_x, offset_y))
            
            self.lx = offset_x + int(min_dim * 0.35)
            self.rx = offset_x + int(min_dim * 0.65)
            self.ly = offset_y + int(min_dim * 0.45)
            self.ry = offset_y + int(min_dim * 0.45)
            
            import cv2
            h, w = self.height, self.width
            yy, xx = np.mgrid[0:h, 0:w]
            
            nx, ny = self.cx, self.cy + min_dim * 0.05
            nose_dist = np.sqrt((xx-nx)**2 + (yy-ny)**2)
            depth = np.clip(1.0 - nose_dist/(min_dim*0.3), 0, 1)

            cx, cy = self.cx, self.cy - min_dim * 0.05
            cranium_dist = np.sqrt((xx-cx)**2 + (yy-cy)**2)
            depth_cranium = np.clip(0.7 - cranium_dist/(min_dim*0.45), 0, 1)
            depth = np.maximum(depth, depth_cranium)

            l_dist = np.sqrt((xx-self.lx)**2*0.6 + (yy-self.ly)**2)
            r_dist = np.sqrt((xx-self.rx)**2*0.6 + (yy-self.ry)**2)
            eye_depth = np.clip(1.0 - np.minimum(l_dist, r_dist)/(min_dim*0.2), 0, 1)

            depth = depth - eye_depth * 0.5
            depth = np.clip(depth, 0, 1)
            
            self._depth = cv2.GaussianBlur(depth, (31, 31), 0).astype(np.float32)
            self._yy, self._xx = yy.astype(np.float32), xx.astype(np.float32)
        else:
            self._skull_base = Image.new("RGB", (self.width, self.height), (0, 0, 0))
            self.lx, self.ly = self.cx - 50, self.cy - 30
            self.rx, self.ry = self.cx + 50, self.cy - 30
            self._depth = np.zeros((self.height, self.width), dtype=np.float32)
            self._yy, self._xx = np.mgrid[0:self.height, 0:self.width].astype(np.float32)"""

code = re.sub(r"    def _build_static_layers\(self\) -> None:.*?(?=    def update)", build_static_new + "\n\n", code, flags=re.DOTALL)

render_new = """    def render(self) -> Image.Image:
        gx, gy = self.gaze()
        
        import cv2
        import numpy as np
        
        arr = np.array(self._skull_base)
        
        shift_x = min(self.width, self.height) * 0.15
        shift_y = min(self.width, self.height) * 0.15
        
        dx = self._depth * (gx * shift_x)
        dy = self._depth * (gy * shift_y)
        
        map_x = self._xx - dx
        map_y = self._yy - dy
        
        warped = cv2.remap(arr, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
        out2 = Image.fromarray(warped)
        
        dlx = dx[self.ly, self.lx]
        dly = dy[self.ly, self.lx]
        drx = dx[self.ry, self.rx]
        dry = dy[self.ry, self.rx]
        
        wl_x = int(self.lx + dlx)
        wl_y = int(self.ly + dly)
        wr_x = int(self.rx + drx)
        wr_y = int(self.ry + dry)
        
        draw = ImageDraw.Draw(out2)
        
        eye_shift_x = int(gx * min(self.width, self.height) * 0.05)
        eye_shift_y = int(gy * min(self.width, self.height) * 0.05)
        
        glow_r = min(self.width, self.height) // 25
        
        lx = wl_x + eye_shift_x
        ly = wl_y + eye_shift_y
        rx = wr_x + eye_shift_x
        ry = wr_y + eye_shift_y
        
        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)
        
        gdraw.ellipse([lx - glow_r*2, ly - glow_r*2, lx + glow_r*2, ly + glow_r*2], fill=(255, 10, 10, 100))
        gdraw.ellipse([lx - glow_r, ly - glow_r, lx + glow_r, ly + glow_r], fill=(255, 80, 80, 200))
        gdraw.ellipse([lx - glow_r//3, ly - glow_r//3, lx + glow_r//3, ly + glow_r//3], fill=(255, 255, 255, 255))
        
        gdraw.ellipse([rx - glow_r*2, ry - glow_r*2, rx + glow_r*2, ry + glow_r*2], fill=(255, 10, 10, 100))
        gdraw.ellipse([rx - glow_r, ry - glow_r, rx + glow_r, ry + glow_r], fill=(255, 80, 80, 200))
        gdraw.ellipse([rx - glow_r//3, ry - glow_r//3, rx + glow_r//3, ry + glow_r//3], fill=(255, 255, 255, 255))
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(5))
        out2.paste(glow_layer, (0, 0), glow_layer)
        
        return out2"""

code = re.sub(r"    def render\(self\) -> Image\.Image:.*", render_new, code, flags=re.DOTALL)

p.write_text(code)
print("Patched skull.py with parallax mapping")
