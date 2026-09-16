import sys
sys.path.insert(0, "src")
from eye import Eye
from monster_eye import MonsterEye

eye1 = Eye(100, 100)
print(type(eye1).__name__)

eye2 = MonsterEye(100, 100)
print(type(eye2).__name__)
