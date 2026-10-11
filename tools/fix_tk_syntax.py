import re
with open("src/dashboard.py", "r") as f:
    tk = f.read()

# Fix floats
tk = re.sub(r'lambda v:\s*\(\s*setattr\(settings,\s*"([^"]+)",\s*float\(v\)\),\s*settings\.save\(\)\)\)+', 
            r'lambda v: (setattr(settings, "\1", float(v)), settings.save())', tk)

# Fix ints
tk = re.sub(r'lambda v:\s*\(\s*setattr\(settings,\s*"([^"]+)",\s*int\(float\(v\)\)\),\s*settings\.save\(\)\)\)+', 
            r'lambda v: (setattr(settings, "\1", int(float(v))), settings.save())', tk)

# Fix smoothing
tk = re.sub(r'lambda v:\s*\(\s*setattr\(settings,\s*"smoothing",\s*float\(v\)\),\s*settings\.save\(\)\)\)+',
            r'lambda v: (setattr(settings, "smoothing", float(v)), settings.save())', tk)

with open("src/dashboard.py", "w") as f:
    f.write(tk)
