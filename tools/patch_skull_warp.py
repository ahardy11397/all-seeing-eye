import re
from pathlib import Path

p = Path("src/skull.py")
code = p.read_text()

render_new = """    def render(self) -> Image.Image:
        gx, gy = self.gaze()
        
        import cv2
        import numpy as np
        
        arr = np.array(self._skull_base)
        h, w = arr.shape[:2]
        
        # perspective vertical squish (pitch/yaw)
        # If gx > 0 (looking right): right edge shrinks vertically
        shrink_r = max(0, gx * h * 0.12)
        shrink_l = max(0, -gx * h * 0.12)
        
        # If gy > 0 (looking down): bottom edge shrinks horizontally
        shrink_b = max(0, gy * w * 0.12)
        shrink_t = max(0, -gy * w * 0.12)
        
        # horizontal and vertical translation
        tx = gx * w * 0.15
        ty = gy * h * 0.15

        tl = [0 + tx + shrink_t, 0 + ty + shrink_l]
        tr = [w + tx - shrink_t, 0 + ty + shrink_r]
        br = [w + tx - shrink_b, h + ty - shrink_r]
        bl = [0 + tx + shrink_b, h + ty - shrink_l]

        src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        dst_pts = np.float32([tl, tr, br, bl])

        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(arr, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
        
        sockets = np.float32([[[self.lx, self.ly], [self.rx, self.ry]]])
        warped_sockets = cv2.perspectiveTransform(sockets, M)[0]
        
        wl_x, wl_y = warped_sockets[0]
        wr_x, wr_y = warped_sockets[1]
        
        out2 = Image.fromarray(warped)
        
        # Draw glowing red eyes in the sockets that move much further
        draw = ImageDraw.Draw(out2)
        
        eye_shift_x = int(gx * min(w, h) * 0.05)
        eye_shift_y = int(gy * min(w, h) * 0.05)
        
        glow_r = min(self.width, self.height) // 25
        
        # Left glow
        lx = wl_x + eye_shift_x
        ly = wl_y + eye_shift_y
        
        # Right glow
        rx = wr_x + eye_shift_x
        ry = wr_y + eye_shift_y
        
        # Draw glows on a separate layer so we can blur them without blurring the high-res skull
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
