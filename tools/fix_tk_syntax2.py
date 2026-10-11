import re
with open("src/dashboard.py", "r") as f:
    tk = f.read()

def cleanup(match):
    # match.group(0) is the entire lambda v: ....
    # We want to extract the key and the casting
    s = match.group(0)
    
    key_match = re.search(r'"([^"]+)"', s)
    if not key_match: return s
    key = key_match.group(1)
    
    if "int(float(v))" in s:
        return f'lambda v: (setattr(settings, "{key}", int(float(v))), settings.save())'
    else:
        return f'lambda v: (setattr(settings, "{key}", float(v)), settings.save())'

tk = re.sub(r'lambda v:[^\n]+', cleanup, tk)

with open("src/dashboard.py", "w") as f:
    f.write(tk)
