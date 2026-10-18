import re

with open("src/main.py", "r") as f:
    content = f.read()

# Add MonsterEye import
imports = """
from eye import Eye
from monster_eye import MonsterEye
"""
content = content.replace("from eye import Eye", imports.strip())

# Loop updates
loop_updates = """
    def tick() -> None:
        nonlocal eye, projector
        current_eye_type = getattr(settings, "eye_type", "human")
        if (current_eye_type == "human" and not isinstance(eye, Eye)) or \
           (current_eye_type == "monster" and not isinstance(eye, MonsterEye)):
            if current_eye_type == "monster":
                eye = MonsterEye(width, height)
            else:
                eye = Eye(width, height)
            projector = Projector(eye)

        t0 = time.perf_counter()
"""

content = content.replace(
    '    def tick() -> None:\n        t0 = time.perf_counter()',
    loop_updates.strip("\n")
)

with open("src/main.py", "w") as f:
    f.write(content)

print("Patched main.py")
