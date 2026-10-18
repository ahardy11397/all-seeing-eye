from pathlib import Path
import re

p = Path("src/joker_eye.py")
code = p.read_text()

# Inject into _build_static_layers
inject_code = """
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

        # heavily blur the makeup to make it look like smeared greasepaint
        makeup_layer = makeup_layer.filter(ImageFilter.GaussianBlur(18))
        
        # composite makeup onto pale face
        self._joker_face = Image.alpha_composite(face, makeup_layer).convert("RGB")

    def update"""

code = code.replace("    def update", inject_code)

# Replace the end of render
render_pattern = re.compile(r"        # Background: White face paint with some unevenness.*return out", re.DOTALL)

render_replacement = """        # Background: White face paint with makeup
        out = self._joker_face.copy()
        
        # Paste the eyeball over the face
        out.paste(canvas, (0, 0), canvas)
        
        # Blinking: Eyelids should be painted black
        if self.blink_factor > 0.0:
            odraw = ImageDraw.Draw(out)
            lid_r = R * 1.5
            
            # Top lid
            top_y_center = self.cy - R - lid_r + (R * 1.1) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, top_y_center - lid_r, self.cx + lid_r, top_y_center + lid_r], fill=(15, 15, 15))
            
            # Bottom lid
            bot_y_center = self.cy + R + lid_r - (R * 0.9) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, bot_y_center - lid_r, self.cx + lid_r, bot_y_center + lid_r], fill=(15, 15, 15))

        return out"""

code = render_pattern.sub(render_replacement, code)

p.write_text(code)
print("Patched joker_eye.py")
