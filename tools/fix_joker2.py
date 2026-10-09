from pathlib import Path
import re

p = Path("src/joker_eye.py")
code = p.read_text()

# Remove the incorrectly placed code
code = re.sub(r"        # inner makeup overlay to hide the hard edge.*?\n    def update", "    def update", code, flags=re.DOTALL)

# Inject correctly after _joker_face
inject_correct = """        self._joker_face = Image.alpha_composite(face, makeup_layer).convert("RGB")
        
        # inner makeup overlay to hide the hard edge
        self._inner_makeup = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(self._inner_makeup)
        idraw.ellipse([self.cx - R - 15, self.cy - R - 15, self.cx + R + 15, self.cy + R + 15], outline=(15, 15, 15, 255), width=30)
        self._inner_makeup = self._inner_makeup.filter(ImageFilter.GaussianBlur(25))"""

code = code.replace("        self._joker_face = Image.alpha_composite(face, makeup_layer).convert(\"RGB\")", inject_correct)

# Wait, `out` in render is a string replacement I did earlier.
# `out.alpha_composite(self._inner_makeup)` requires `out` to be RGBA!
# But wait, `out` is RGB! `out.alpha_composite` only works if `out` is RGBA.
# Wait, `Image.alpha_composite` requires RGBA. Since `out` is RGB, `out.paste(self._inner_makeup, (0, 0), self._inner_makeup)` is the correct way to blend an RGBA image over an RGB image!
code = code.replace("out.alpha_composite(self._inner_makeup)", "out.paste(self._inner_makeup, (0, 0), self._inner_makeup)")

p.write_text(code)
print("Fixed joker_eye.py again")
