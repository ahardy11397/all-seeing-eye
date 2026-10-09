with open("src/main.py", "r") as f:
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
                eye = MonsterEye(width, height)
            elif current_eye_type == "zombie":
                eye = ZombieEye(width, height)
            elif current_eye_type == "dragon":
                eye = DragonEye(width, height)
            else:
                eye = Eye(width, height)
"""

import re
content = re.sub(
    r'        if \(current_eye_type == "human".*?eye = Eye\(width, height\)',
    loop_updates.strip("\n"),
    content,
    flags=re.DOTALL
)

with open("src/main.py", "w") as f:
    f.write(content)
