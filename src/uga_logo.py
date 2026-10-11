import math
import time
import os
from PIL import Image
from config import settings

class UgaLogo:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.iris_x = width // 2
        self.iris_y = height // 2
        
        # Load and resize the logo
        logo_path = "uga_logo.png"
        if os.path.exists(logo_path):
            self.logo = Image.open(logo_path).convert("RGBA")
            # Scale it to fit nicely within the screen
            size = int(min(width, height) * 0.8)
            self.logo = self.logo.resize((size, size), Image.LANCZOS)
        else:
            # Fallback
            self.logo = Image.new("RGBA", (200, 200), (255, 0, 0, 255))
            
    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        # We ignore tracking entirely per "just spins back and forth"
        pass
        
    def gaze(self) -> tuple[float, float]:
        # Dummy gaze
        return 0.0, 0.0
        
    def render(self) -> Image.Image:
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        
        # Center the logo on the output frame
        paste_x = (self.width - self.logo.width) // 2
        paste_y = (self.height - self.logo.height) // 2
        
        out.paste(self.logo, (paste_x, paste_y), self.logo)
        
        return out