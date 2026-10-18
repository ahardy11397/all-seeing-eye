from pathlib import Path
import re

p = Path("src/joker_eye.py")
code = p.read_text()

# 1. Add inner makeup overlay to _build_static_layers
inject_static = """
        # inner makeup overlay to hide the hard edge
        self._inner_makeup = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(self._inner_makeup)
        # Draw a thick black ring around the border of the eye
        idraw.ellipse([self.cx - R - 15, self.cy - R - 15, self.cx + R + 15, self.cy + R + 15], outline=(15, 15, 15, 255), width=30)
        # Blur it heavily so it fades inward over the sclera and outward over the face
        self._inner_makeup = self._inner_makeup.filter(ImageFilter.GaussianBlur(25))

    def update"""

code = code.replace("    def update", inject_static)

# 2. Remove the hard outline from render
code = re.sub(r"        # soften the eyeball outline.*?\n        draw\.ellipse.*?width=4\)\n", "", code, flags=re.DOTALL)

# 3. Add alpha composite of _inner_makeup in render
inject_render = """        # Paste the eyeball over the face
        out.paste(canvas, (0, 0), canvas)
        
        # Paste the inner makeup overlay to soften the transition!
        out.alpha_composite(self._inner_makeup)"""

code = code.replace("        # Paste the eyeball over the face\n        out.paste(canvas, (0, 0), canvas)", inject_render)

p.write_text(code)
print("Patched joker_eye.py edge")
