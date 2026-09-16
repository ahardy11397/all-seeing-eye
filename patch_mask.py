import os

files = ["src/eye.py", "src/monster_eye.py", "src/zombie_eye.py", "src/dragon_eye.py"]

for filepath in files:
    with open(filepath, "r") as f:
        content = f.read()

    new_logic = """
        out.paste(canvas, (0, 0), canvas)
        
        if self.blink_factor > 0.0:
            odraw = ImageDraw.Draw(out)
            lid_r = R * 1.5
            top_y_center = self.cy - R - lid_r + (R * 1.1) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, top_y_center - lid_r, self.cx + lid_r, top_y_center + lid_r], fill=(0, 0, 0))
            
            bot_y_center = self.cy + R + lid_r - (R * 0.9) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, bot_y_center - lid_r, self.cx + lid_r, bot_y_center + lid_r], fill=(0, 0, 0))

        return out
"""
    content = content.replace("        out.paste(canvas, (0, 0), canvas)\n        return out", new_logic.strip("\n"))

    with open(filepath, "w") as f:
        f.write(content)
