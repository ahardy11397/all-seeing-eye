import re

with open("run_stream.py", "r") as f:
    content = f.read()

imports = """
from eye import Eye
from monster_eye import MonsterEye
"""
content = content.replace("from eye import Eye", imports.strip())

loop_updates = """
        while True:
            current_eye_type = getattr(settings, "eye_type", "human")
            if (current_eye_type == "human" and type(eye).__name__ != "Eye") or \
               (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye"):
                if current_eye_type == "monster":
                    eye = MonsterEye(settings.width, settings.height)
                else:
                    eye = Eye(settings.width, settings.height)

            t0 = time.perf_counter()
"""

content = content.replace(
    '        while True:\n            t0 = time.perf_counter()',
    loop_updates.strip("\n")
)

with open("run_stream.py", "w") as f:
    f.write(content)

print("Patched run_stream.py")
