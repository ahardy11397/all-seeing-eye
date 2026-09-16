import re
from pathlib import Path

def patch_file(filepath, var_name, eye_creation_args):
    p = Path(filepath)
    if not p.exists(): return
    content = p.read_text()
    
    if "from snake_eye import SnakeEye" not in content:
        content = content.replace("from dragon_eye import DragonEye", 
                                  "from dragon_eye import DragonEye\nfrom snake_eye import SnakeEye\nfrom spider_eye import SpiderEye\nfrom bug_eye import BugEye\nfrom creepy_figure import CreepyFigure")

    old_if = f"""            if (current_eye_type == "human" and type({var_name}).__name__ != "Eye") or \\
               (current_eye_type == "monster" and type({var_name}).__name__ != "MonsterEye") or \\
               (current_eye_type == "zombie" and type({var_name}).__name__ != "ZombieEye") or \\
               (current_eye_type == "dragon" and type({var_name}).__name__ != "DragonEye"):
                if current_eye_type == "monster":
                    {var_name} = MonsterEye({eye_creation_args})
                elif current_eye_type == "zombie":
                    {var_name} = ZombieEye({eye_creation_args})
                elif current_eye_type == "dragon":
                    {var_name} = DragonEye({eye_creation_args})
                else:
                    {var_name} = Eye({eye_creation_args})"""

    # For run_stream.py the formatting might be slightly different:
    old_if_rs = f"""            if (current_eye_type == "human" and type({var_name}).__name__ != "Eye") or \\
               (current_eye_type == "monster" and type({var_name}).__name__ != "MonsterEye") or \\
               (current_eye_type == "zombie" and type({var_name}).__name__ != "ZombieEye") or \\
               (current_eye_type == "dragon" and type({var_name}).__name__ != "DragonEye"):"""
               
    # Wait, in run_stream.py it was using `\` but somehow it got joined in my `view_file` output as `or                (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye") or                (current_eye_type == "zombie" and type(eye).__name__ != "ZombieEye") or                (current_eye_type == "dragon" and type(eye).__name__ != "DragonEye"):`
    # Better to use regex to find the block.
    
    # regex for the if block
    pattern = re.compile(
        r'(\s*)if \(current_eye_type == "human".*?else:\s+' + re.escape(var_name) + r' = Eye\(' + re.escape(eye_creation_args) + r'\)',
        re.DOTALL
    )
    
    def repl(m):
        ind = m.group(1)
        return f"""{ind}if type({var_name}).__name__.lower().replace("eye", "").replace("creepyfigure", "creepy_figure") != current_eye_type and not (current_eye_type == "human" and type({var_name}).__name__ == "Eye"):
{ind}    if current_eye_type == "monster": {var_name} = MonsterEye({eye_creation_args})
{ind}    elif current_eye_type == "zombie": {var_name} = ZombieEye({eye_creation_args})
{ind}    elif current_eye_type == "dragon": {var_name} = DragonEye({eye_creation_args})
{ind}    elif current_eye_type == "snake": {var_name} = SnakeEye({eye_creation_args})
{ind}    elif current_eye_type == "spider": {var_name} = SpiderEye({eye_creation_args})
{ind}    elif current_eye_type == "bug": {var_name} = BugEye({eye_creation_args})
{ind}    elif current_eye_type == "creepy_figure": {var_name} = CreepyFigure({eye_creation_args})
{ind}    else: {var_name} = Eye({eye_creation_args})"""
    
    content, count = pattern.subn(repl, content)
    if count == 0:
        print(f"Failed to patch {filepath}")
    else:
        print(f"Patched {filepath}")
        
    p.write_text(content)

patch_file("src/main.py", "eye", "width, height")
patch_file("src/dashboard.py", "self.eye", "settings.width, settings.height")
patch_file("run_stream.py", "eye", "settings.width, settings.height")

# Also dashboard.py dropdown
d = Path("src/dashboard.py").read_text()
d = d.replace('"human", "monster", "zombie", "dragon"', '"human", "monster", "zombie", "dragon", "snake", "spider", "bug", "creepy_figure"')
Path("src/dashboard.py").write_text(d)

# dashboard_server.py HTML dropdown
ds = Path("src/dashboard_server.py").read_text()
options = """        <option value="human">Human (Default)</option>
        <option value="monster">Monster</option>
        <option value="zombie">Zombie</option>
        <option value="dragon">Dragon</option>
        <option value="snake">Snake</option>
        <option value="spider">Spider</option>
        <option value="bug">Bug</option>
        <option value="creepy_figure">Creepy Figure</option>"""
ds = re.sub(r'<option value="human">Human \(Default\)</option>.*?<option value="dragon">Dragon</option>', options, ds, flags=re.DOTALL)
Path("src/dashboard_server.py").write_text(ds)
print("Patched dashboard dropdowns")

