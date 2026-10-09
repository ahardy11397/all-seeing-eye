import re
from pathlib import Path

# 1. Snake Eye (based on Dragon Eye)
dragon_code = Path("src/dragon_eye.py").read_text()
snake_code = dragon_code.replace("class DragonEye:", "class SnakeEye:")
snake_code = snake_code.replace("np.array([255, 215, 0], dtype=float)", "np.array([220, 255, 0], dtype=float)") # inner yellow-green
snake_code = snake_code.replace("np.array([0, 100, 50], dtype=float)", "np.array([0, 40, 10], dtype=float)") # outer dark green
snake_code = snake_code.replace("vessel_r = 255.0", "vessel_r = 150.0")
snake_code = snake_code.replace("vessel_g = 215.0", "vessel_g = 180.0")
snake_code = snake_code.replace("vessel_b = 0.0", "vessel_b = 0.0")
Path("src/snake_eye.py").write_text(snake_code)
print("Created snake_eye.py")
