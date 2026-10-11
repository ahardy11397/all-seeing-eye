import re
from pathlib import Path

p = Path("src/skull.py")
code = p.read_text()

build_static_new = """    def _build_static_layers(self) -> None:
        self.frames = []
        gif_path = "skull.gif"
        import os
        from PIL import Image
        
        if os.path.exists(gif_path):
            img = Image.open(gif_path)
            for i in range(img.n_frames):
                img.seek(i)
                frame = img.convert("RGB")
                
                min_dim = min(self.width, self.height)
                frame = frame.resize((min_dim, min_dim), Image.LANCZOS)
                
                canvas = Image.new("RGB", (self.width, self.height), (0, 0, 0))
                offset_x = (self.width - min_dim) // 2
                offset_y = (self.height - min_dim) // 2
                canvas.paste(frame, (offset_x, offset_y))
                
                self.frames.append(canvas)
                
            # Symmetry analysis found front facing at frame 9 or 57
            self.front_frame = 9
            self.max_turn_frames = 20
        else:
            # Fallback
            self.frames = [Image.new("RGB", (self.width, self.height), (0, 0, 0))]
            self.front_frame = 0
            self.max_turn_frames = 0"""

code = re.sub(r"    def _build_static_layers\(self\) -> None:.*?(?=    def update)", build_static_new + "\n\n", code, flags=re.DOTALL)

render_new = """    def render(self) -> Image.Image:
        gx, gy = self.gaze()
        
        # Calculate which frame to show based on horizontal gaze
        # gx goes from -1 to 1.
        # If gx is positive, target is to our right, so the skull turns to its right (our left).
        # We might need to invert the sign depending on the GIF's spin direction.
        # Let's just use int(gx * self.max_turn_frames)
        
        frame_offset = int(gx * self.max_turn_frames)
        
        # Assume the GIF spins clockwise or counter-clockwise.
        # We can just add the offset.
        frame_idx = (self.front_frame - frame_offset) % max(1, len(self.frames))
        
        # Get the base frame
        out = self.frames[frame_idx].copy()
        
        # Vertical tilt (gy) is harder to fake with a horizontal spinning gif.
        # We can use a very slight vertical parallax shift on the image to simulate looking up/down!
        if gy != 0:
            import numpy as np
            import cv2
            arr = np.array(out)
            shift_y = int(gy * min(self.width, self.height) * 0.05)
            
            # Create a simple translation matrix for Y
            M = np.float32([[1, 0, 0], [0, 1, shift_y]])
            arr = cv2.warpAffine(arr, M, (self.width, self.height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
            out = Image.fromarray(arr)
            
        return out"""

code = re.sub(r"    def render\(self\) -> Image\.Image:.*", render_new, code, flags=re.DOTALL)

p.write_text(code)
print("Patched skull.py with GIF")
