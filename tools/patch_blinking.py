import os
import re

files = ["src/eye.py", "src/monster_eye.py", "src/zombie_eye.py", "src/dragon_eye.py"]

for filepath in files:
    with open(filepath, "r") as f:
        content = f.read()

    # Add blink_factor initialization
    content = content.replace(
        "self.blink_duration: float = 0.0",
        "self.blink_duration: float = 0.0\n        self.blink_factor: float = 0.0"
    )

    # Replace `# blinking disabled` with actual logic
    blink_logic = """
        if getattr(settings, "blink_enabled", False):
            if self.blink_started_at is None:
                if now >= self.next_blink_at:
                    self.blink_started_at = now
                    self.blink_duration = random.uniform(0.15, 0.35)
            
            if self.blink_started_at is not None:
                elapsed = now - self.blink_started_at
                if elapsed >= self.blink_duration:
                    self.blink_started_at = None
                    self.next_blink_at = self._next_blink_time()
                    self.blink_factor = 0.0
                else:
                    progress = elapsed / self.blink_duration
                    # power curve to make it stay closed a tiny bit longer
                    self.blink_factor = math.sin(progress * math.pi) ** 0.8
        else:
            self.blink_factor = 0.0
"""
    content = content.replace("# blinking disabled", blink_logic.strip("\n"))

    # Add mask rendering logic
    mask_logic_old = """
        mask = Image.new("1", (self.width, self.height), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse([self.cx - R, self.cy - R, self.cx + R, self.cy + R], fill=1)
"""
    mask_logic_new = """
        mask = Image.new("1", (self.width, self.height), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse([self.cx - R, self.cy - R, self.cx + R, self.cy + R], fill=1)
        
        if self.blink_factor > 0.0:
            # Curved eyelids using black ellipses
            # As blink_factor goes from 0 to 1, the ellipses move towards the center
            lid_r = R * 1.5
            
            # Top lid
            top_y_center = self.cy - R - lid_r + (R * 1.1) * self.blink_factor
            mdraw.ellipse([self.cx - lid_r, top_y_center - lid_r, self.cx + lid_r, top_y_center + lid_r], fill=0)
            
            # Bottom lid (moves up slightly less than top lid moves down)
            bot_y_center = self.cy + R + lid_r - (R * 0.9) * self.blink_factor
            mdraw.ellipse([self.cx - lid_r, bot_y_center - lid_r, self.cx + lid_r, bot_y_center + lid_r], fill=0)
"""
    content = content.replace(mask_logic_old.strip("\n"), mask_logic_new.strip("\n"))

    with open(filepath, "w") as f:
        f.write(content)

