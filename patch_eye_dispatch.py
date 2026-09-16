import re
from pathlib import Path

# Common replacement for main.py, dashboard.py, run_stream.py
def patch_file(filepath):
    p = Path(filepath)
    if not p.exists(): return
    content = p.read_text()
    
    # Add imports
    imports_to_add = """from dragon_eye import DragonEye
from snake_eye import SnakeEye
from spider_eye import SpiderEye
from bug_eye import BugEye
from creepy_figure import CreepyFigure
"""
    if "from snake_eye import SnakeEye" not in content:
        content = content.replace("from dragon_eye import DragonEye", imports_to_add)

    # Add to if/else block
    dispatch_old = """            if (current_eye_type == "human" and type(eye).__name__ != "Eye") or \
               (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye") or \
               (current_eye_type == "zombie" and type(eye).__name__ != "ZombieEye") or \
               (current_eye_type == "dragon" and type(eye).__name__ != "DragonEye"):
                if current_eye_type == "monster":
                    eye = MonsterEye(width, height)
                elif current_eye_type == "zombie":
                    eye = ZombieEye(width, height)
                elif current_eye_type == "dragon":
                    eye = DragonEye(width, height)
                else:
                    eye = Eye(width, height)"""
    
    # regex for run_stream.py, dashboard.py, main.py
    # They have slightly different variable names for eye creation (width/height vs settings.width)
    import re
    # We can just match the block dynamically
    
    block_pattern = re.compile(
        r'if \(current_eye_type == "human".*?else:\s+self\.eye = Eye\([^)]+\)',
        re.DOTALL
    )
    # wait, in run_stream it's `eye = Eye(...)` not `self.eye`
    
