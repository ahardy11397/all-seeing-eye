with open("src/config.py", "r") as f:
    content = f.read()

content = content.replace("smoothing: float = 0.18", "smoothing: float = 0.18\n    blink_enabled: bool = False\n    blink_interval_s: tuple[float, float] = (2.0, 8.0)")

with open("src/config.py", "w") as f:
    f.write(content)
