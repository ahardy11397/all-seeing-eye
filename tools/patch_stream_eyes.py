with open("run_stream.py", "r") as f:
    content = f.read()

imports = """
from eye import Eye
from monster_eye import MonsterEye
from zombie_eye import ZombieEye
from dragon_eye import DragonEye
"""
content = content.replace("from eye import Eye\nfrom monster_eye import MonsterEye", imports.strip())

loop_updates = """
            if (current_eye_type == "human" and type(eye).__name__ != "Eye") or \\
               (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye") or \\
               (current_eye_type == "zombie" and type(eye).__name__ != "ZombieEye") or \\
               (current_eye_type == "dragon" and type(eye).__name__ != "DragonEye"):
                if current_eye_type == "monster":
                    eye = MonsterEye(settings.width, settings.height)
                elif current_eye_type == "zombie":
                    eye = ZombieEye(settings.width, settings.height)
                elif current_eye_type == "dragon":
                    eye = DragonEye(settings.width, settings.height)
                else:
                    eye = Eye(settings.width, settings.height)
"""

import re
content = re.sub(
    r'            if \(current_eye_type == "human".*?eye = Eye\(settings\.width, settings\.height\)',
    loop_updates.strip("\n"),
    content,
    flags=re.DOTALL
)

with open("run_stream.py", "w") as f:
    f.write(content)
