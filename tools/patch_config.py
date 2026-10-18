with open("src/config.py", "r") as f:
    text = f.read()

import re
if "tracking_enabled" not in text:
    text = text.replace("    blink_duration_s: tuple[float, float] = (0.12, 0.25)\n", "    blink_duration_s: tuple[float, float] = (0.12, 0.25)\n    tracking_enabled: bool = True\n")
    with open("src/config.py", "w") as f:
        f.write(text)
