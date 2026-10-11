import re
from pathlib import Path

p = Path("src/uga_logo.py")
code = p.read_text()

render_new = """    def render(self) -> Image.Image:
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        
        # Center the logo on the output frame
        paste_x = (self.width - self.logo.width) // 2
        paste_y = (self.height - self.logo.height) // 2
        
        out.paste(self.logo, (paste_x, paste_y), self.logo)
        
        return out"""

code = re.sub(r"    def render\(self\) -> Image\.Image:.*", render_new, code, flags=re.DOTALL)
p.write_text(code)
print("Made UgaLogo static")
