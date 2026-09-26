from pathlib import Path

p = Path("src/joker_eye.py")
content = p.read_text()

# Extract the block that was wrongly injected
block = """
        # --- Pre-render Joker face makeup ---
        face = Image.new("RGBA", (self.width, self.height), (230, 230, 230, 255))
        
        makeup_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        mdraw = ImageDraw.Draw(makeup_layer)
        
        rng_makeup = np.random.default_rng(42)
        # Draw base solid black around the eye socket
        R = settings.eye_radius
        mdraw.ellipse([self.cx - R*1.4, self.cy - R*1.2, self.cx + R*1.4, self.cy + R*1.3], fill=(15, 15, 15, 255))
        
        # Draw messy jagged edges and drips
        for _ in range(80):
            ang = rng_makeup.uniform(0, math.pi * 2)
            dist = rng_makeup.uniform(R * 1.0, R * 2.0)
            if rng_makeup.uniform() < 0.4:
                ang = rng_makeup.uniform(0, math.pi) # biased downward
                dist = rng_makeup.uniform(R * 1.2, R * 2.5) # longer drips
                
            sx = self.cx + math.cos(ang) * dist
            sy = self.cy + math.sin(ang) * dist
            
            w = rng_makeup.uniform(20, 60)
            h = rng_makeup.uniform(20, 60)
            mdraw.ellipse([sx - w/2, sy - h/2, sx + w/2, sy + h/2], fill=(15, 15, 15, int(rng_makeup.uniform(100, 255))))
            
            if sy > self.cy and rng_makeup.uniform() < 0.3:
                drip_len = rng_makeup.uniform(50, 150)
                mdraw.line([sx, sy, sx + rng_makeup.uniform(-20, 20), sy + drip_len], fill=(15, 15, 15, int(rng_makeup.uniform(150, 255))), width=int(rng_makeup.uniform(10, 25)))

        # heavily blur the makeup to make it look smeared greasepaint
        makeup_layer = makeup_layer.filter(ImageFilter.GaussianBlur(18))
        
        # composite makeup onto pale face
        self._joker_face = Image.alpha_composite(face, makeup_layer).convert("RGB")
"""

# The code in the file actually has `# heavily blur the makeup to make it look like smeared greasepaint`
# Wait, let's just use string replace.
import re

# Remove from after _idle_target
content = re.sub(r"        # --- Pre-render Joker face makeup ---.*?        self\._joker_face = Image\.alpha_composite\(face, makeup_layer\)\.convert\(\"RGB\"\)\n+", "", content, flags=re.DOTALL)

# Insert at the end of _build_static_layers
insert_pos = content.find("        # --- wet lower-lid reflection line sprite (drawn dynamically, no sprite needed)")
if insert_pos == -1:
    print("Could not find insert pos!")
else:
    content = content[:insert_pos] + block + "\n" + content[insert_pos:]
    p.write_text(content)
    print("Fixed joker_eye.py")

