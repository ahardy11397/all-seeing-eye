import re

with open("src/dashboard.py", "r") as f:
    content = f.read()

imports = """
from eye import Eye
from monster_eye import MonsterEye
"""
content = content.replace("from eye import Eye", imports.strip())

loop_updates = """
        def tick() -> None:
            current_eye_type = getattr(settings, "eye_type", "human")
            if (current_eye_type == "human" and type(self.eye).__name__ != "Eye") or \
               (current_eye_type == "monster" and type(self.eye).__name__ != "MonsterEye"):
                if current_eye_type == "monster":
                    self.eye = MonsterEye(settings.width, settings.height)
                else:
                    self.eye = Eye(settings.width, settings.height)

            t0 = time.perf_counter()
"""

content = content.replace(
    '        def tick() -> None:\n            t0 = time.perf_counter()',
    loop_updates.strip("\n")
)

with open("src/dashboard.py", "w") as f:
    f.write(content)

print("Patched dashboard logic")
