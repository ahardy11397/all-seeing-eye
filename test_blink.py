import sys
sys.path.insert(0, "src")
from eye import Eye
from PIL import ImageDraw

eye = Eye(400, 400)
# Mock a blink factor
for blink_factor in [0.0, 0.5, 1.0]:
    frame = eye.render()
    
    mask = frame.copy().convert("RGBA")
    draw = ImageDraw.Draw(mask)
    R = 190
    cy = 200
    
    # Curved eyelids:
    # A circle offset upwards/downwards
    
    top_y = cy - R + (R * 2) * blink_factor / 2
    bot_y = cy + R - (R * 2) * blink_factor / 2
    
    draw.rectangle([0, 0, 400, top_y], fill=(0,0,0,255))
    draw.rectangle([0, bot_y, 400, 400], fill=(0,0,0,255))
    
    mask.save(f"blink_{blink_factor}.png")
