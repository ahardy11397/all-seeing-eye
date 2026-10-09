with open("src/zombie_eye.py", "r") as f:
    content = f.read()

content = content.replace("class Eye:", "class ZombieEye:")

# Make sclera milky/yellowish-grey
content = content.replace(
    "r = np.clip(base - 3 * t + 2 * t, 0, 255)",
    "r = np.clip(base * 0.8 + 30, 0, 255)"
)
content = content.replace(
    "g = np.clip(base - 1 * t - 4 * t, 0, 255)",
    "g = np.clip(base * 0.8 + 30, 0, 255)"
)
content = content.replace(
    "b = np.clip(base + 2, 0, 255)",
    "b = np.clip(base * 0.7 + 20, 0, 255)"
)

# Dead/dark vessels
content = content.replace(
    "vessel_r = 168.0\n        vessel_g = 22.0\n        vessel_b = 30.0",
    "vessel_r = 60.0\n        vessel_g = 40.0\n        vessel_b = 40.0"
)

# Pale, cloudy icy/grey iris
content = content.replace(
    "inner = np.array([118, 172, 232], dtype=float)",
    "inner = np.array([180, 190, 200], dtype=float)"
)
content = content.replace(
    "outer = np.array([16, 52, 112], dtype=float)",
    "outer = np.array([100, 110, 110], dtype=float)"
)

# Pupil a bit cloudy (instead of pure black)
content = content.replace(
    "black = Image.new(\"RGBA\", (psize, psize), (6, 6, 10, 255))",
    "black = Image.new(\"RGBA\", (psize, psize), (60, 70, 70, 255))"
)

with open("src/zombie_eye.py", "w") as f:
    f.write(content)
