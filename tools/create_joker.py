from pathlib import Path
import re

# 1. Create joker_eye.py
joker_code = Path("src/eye.py").read_text()
joker_code = joker_code.replace("class Eye:", "class JokerEye:")

# Change iris color to hazel/greenish brown
# In eye.py:
# inner = np.array([118, 172, 232], dtype=float)
# outer = np.array([16, 52, 112], dtype=float)
joker_code = joker_code.replace(
    "inner = np.array([118, 172, 232], dtype=float)", 
    "inner = np.array([130, 110, 50], dtype=float)" # Hazel/Brown
)
joker_code = joker_code.replace(
    "outer = np.array([16, 52, 112], dtype=float)", 
    "outer = np.array([50, 60, 20], dtype=float)" # Olive/Green
)

# Sclera base can be slightly bloodshot, but eye.py's default is good. 

# Modify the render function to add the messy makeup and white skin
# We need to replace the section from `out = Image.new("RGB", (self.width, self.height), (0, 0, 0))`
# down to the end of the blink logic.

render_old = """        # solid black background outside the eyeball (so projectors/WebView
        # never show transparent as white), and clip vessels that extend
        # beyond the eyeball circle
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        out.paste(canvas, (0, 0), canvas)
        
        if self.blink_factor > 0.0:
            odraw = ImageDraw.Draw(out)
            lid_r = R * 1.5
            top_y_center = self.cy - R - lid_r + (R * 1.1) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, top_y_center - lid_r, self.cx + lid_r, top_y_center + lid_r], fill=(0, 0, 0))
            
            bot_y_center = self.cy + R + lid_r - (R * 0.9) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, bot_y_center - lid_r, self.cx + lid_r, bot_y_center + lid_r], fill=(0, 0, 0))

        return out"""

render_new = """        # Background: White face paint with some unevenness
        out = Image.new("RGB", (self.width, self.height), (230, 230, 230))
        
        # Add some smudgy grey/white texture to background
        import random
        # We can just leave it solid pale for performance, but let's add a quick vignette
        
        # Paste the eyeball
        out.paste(canvas, (0, 0), canvas)
        
        odraw = ImageDraw.Draw(out)
        
        # Joker black smudgy makeup around the eye
        # We'll draw several messy overlapping ellipses and polygons around the eye border
        import numpy as np
        rng_makeup = np.random.default_rng(42) # fixed seed for static-looking makeup strokes
        
        for _ in range(40):
            # random smudges around the eye
            ang = rng_makeup.uniform(0, math.pi * 2)
            dist = rng_makeup.uniform(R * 0.8, R * 1.5)
            # biased towards bottom and corners (like weeping makeup)
            if rng_makeup.uniform() < 0.6:
                if rng_makeup.uniform() < 0.5:
                    ang = rng_makeup.uniform(0, math.pi) # bottom half
                else:
                    ang = rng_makeup.choice([rng_makeup.uniform(-0.5, 0.5), rng_makeup.uniform(math.pi-0.5, math.pi+0.5)]) # corners
            
            sx = self.cx + math.cos(ang) * dist
            sy = self.cy + math.sin(ang) * dist
            
            # Draw random messy strokes
            w = rng_makeup.uniform(10, 40)
            h = rng_makeup.uniform(10, 40)
            alpha = int(rng_makeup.uniform(100, 255))
            
            # Since ImageDraw doesn't support RGBA directly on RGB without a mask layer, 
            # we'll draw solid black or dark grey with varied shapes to look smudgy.
            grey_val = int(rng_makeup.uniform(0, 30))
            odraw.ellipse([sx - w/2, sy - h/2, sx + w/2, sy + h/2], fill=(grey_val, grey_val, grey_val))
            
            # Occasional drips downwards
            if rng_makeup.uniform() < 0.15 and sy > self.cy:
                drip_len = rng_makeup.uniform(20, 80)
                odraw.line([sx, sy, sx + rng_makeup.uniform(-10, 10), sy + drip_len], fill=(10, 10, 10), width=int(rng_makeup.uniform(3, 10)))

        # Blinking: Eyelids should be painted black (or white with black smudges)
        if self.blink_factor > 0.0:
            lid_r = R * 1.5
            
            # Top lid
            top_y_center = self.cy - R - lid_r + (R * 1.1) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, top_y_center - lid_r, self.cx + lid_r, top_y_center + lid_r], fill=(20, 20, 20))
            
            # Bottom lid
            bot_y_center = self.cy + R + lid_r - (R * 0.9) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, bot_y_center - lid_r, self.cx + lid_r, bot_y_center + lid_r], fill=(20, 20, 20))
            
            # Draw some creases/smudges on the closed lid
            if self.blink_factor > 0.8:
                odraw.line([self.cx - R*0.8, self.cy, self.cx + R*0.8, self.cy], fill=(0,0,0), width=6)

        # Let's apply a slight blur to the whole thing to make the makeup look smeared, 
        # but keep the eye sharp? Doing it to the whole output is easy.
        # Actually, let's keep it sharp for performance, the overlapping ellipses already look like greasepaint.

        return out"""

joker_code = joker_code.replace(render_old, render_new)
Path("src/joker_eye.py").write_text(joker_code)

# 2. Patch dispatchers
def patch_file(filepath, var_name, eye_creation_args):
    p = Path(filepath)
    if not p.exists(): return
    content = p.read_text()
    
    if "from joker_eye import JokerEye" not in content:
        content = content.replace("from creepy_figure import CreepyFigure", 
                                  "from creepy_figure import CreepyFigure\nfrom joker_eye import JokerEye")

    pattern = re.compile(
        r'(\s*)elif current_eye_type == "creepy_figure": ' + re.escape(var_name) + r' = CreepyFigure\(' + re.escape(eye_creation_args) + r'\)',
        re.DOTALL
    )
    
    def repl(m):
        ind = m.group(1)
        return f"""{ind}elif current_eye_type == "creepy_figure": {var_name} = CreepyFigure({eye_creation_args})
{ind}    elif current_eye_type == "joker": {var_name} = JokerEye({eye_creation_args})"""
    
    content, count = pattern.subn(repl, content)
    if count == 0:
        print(f"Failed to patch {filepath}")
    else:
        print(f"Patched {filepath}")
        
    p.write_text(content)

patch_file("src/main.py", "eye", "width, height")
patch_file("src/dashboard.py", "self.eye", "settings.width, settings.height")
patch_file("run_stream.py", "eye", "settings.width, settings.height")

# dashboard.py dropdown
d = Path("src/dashboard.py").read_text()
if '"joker"' not in d:
    d = d.replace('"creepy_figure"', '"creepy_figure", "joker"')
    Path("src/dashboard.py").write_text(d)

# dashboard_server.py HTML dropdown
ds = Path("src/dashboard_server.py").read_text()
if 'value="joker"' not in ds:
    options = """        <option value="creepy_figure">Creepy Figure</option>
        <option value="joker">Joker (Heath Ledger)</option>"""
    ds = ds.replace('<option value="creepy_figure">Creepy Figure</option>', options)
    Path("src/dashboard_server.py").write_text(ds)

print("Created JokerEye and patched dispatches.")

