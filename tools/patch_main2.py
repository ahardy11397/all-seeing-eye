import re

with open("src/main.py", "r") as f:
    content = f.read()

content = content.replace(
    '        if (current_eye_type == "human" and not isinstance(eye, Eye)) or \\\n           (current_eye_type == "monster" and not isinstance(eye, MonsterEye)):',
    '        if (current_eye_type == "human" and type(eye).__name__ != "Eye") or \\\n           (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye"):'
)

with open("src/main.py", "w") as f:
    f.write(content)
