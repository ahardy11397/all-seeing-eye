import re

with open("src/monster_eye.py", "r") as f:
    content = f.read()

content = content.replace("class Eye:", "class MonsterEye:")

content = content.replace(
    "r = np.clip(base - 3 * t + 2 * t, 0, 255)",
    "r = np.clip(base * 0.7 + 20, 0, 255)"
)
content = content.replace(
    "g = np.clip(base - 1 * t - 4 * t, 0, 255)",
    "g = np.clip(base * 0.1, 0, 255)"
)
content = content.replace(
    "b = np.clip(base + 2, 0, 255)",
    "b = np.clip(base * 0.1, 0, 255)"
)

content = content.replace(
    "vessel_r = 168.0\n        vessel_g = 22.0\n        vessel_b = 30.0",
    "vessel_r = 255.0\n        vessel_g = 180.0\n        vessel_b = 20.0"
)

content = content.replace(
    "inner = np.array([118, 172, 232], dtype=float)",
    "inner = np.array([255, 230, 50], dtype=float)"
)
content = content.replace(
    "outer = np.array([16, 52, 112], dtype=float)",
    "outer = np.array([180, 20, 0], dtype=float)"
)

content = content.replace(
    "pdraw.ellipse([psize / 2 - ps, psize / 2 - ps, psize / 2 + ps, psize / 2 + ps], fill=255)",
    "pdraw.ellipse([psize / 2 - ps * 0.25, psize / 2 - ps * 1.5, psize / 2 + ps * 0.25, psize / 2 + ps * 1.5], fill=255)"
)

with open("src/monster_eye.py", "w") as f:
    f.write(content)

print("Patched monster_eye.py")
