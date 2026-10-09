with open("src/dashboard.py", "r") as f:
    content = f.read()

imports = """
from eye import Eye
from monster_eye import MonsterEye
from zombie_eye import ZombieEye
from dragon_eye import DragonEye
"""
content = content.replace("from eye import Eye\nfrom monster_eye import MonsterEye", imports.strip())

loop_updates = """
            if (current_eye_type == "human" and type(self.eye).__name__ != "Eye") or \\
               (current_eye_type == "monster" and type(self.eye).__name__ != "MonsterEye") or \\
               (current_eye_type == "zombie" and type(self.eye).__name__ != "ZombieEye") or \\
               (current_eye_type == "dragon" and type(self.eye).__name__ != "DragonEye"):
                if current_eye_type == "monster":
                    self.eye = MonsterEye(settings.width, settings.height)
                elif current_eye_type == "zombie":
                    self.eye = ZombieEye(settings.width, settings.height)
                elif current_eye_type == "dragon":
                    self.eye = DragonEye(settings.width, settings.height)
                else:
                    self.eye = Eye(settings.width, settings.height)
"""

# Replace existing check
import re
content = re.sub(
    r'            if \(current_eye_type == "human".*?self\.eye = Eye\(settings\.width, settings\.height\)',
    loop_updates.strip("\n"),
    content,
    flags=re.DOTALL
)

with open("src/dashboard.py", "w") as f:
    f.write(content)
