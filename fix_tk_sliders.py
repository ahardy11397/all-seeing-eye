import re
with open("src/dashboard.py", "r") as f:
    tk = f.read()

# Fix the broken lambdas
tk = tk.replace('float(v, settings.save())', 'float(v)), settings.save()')

# Wait, let's verify what the exact strings are
# lambda v: (setattr(settings, "min_confidence", float(v, settings.save()))))
# Let's just use regex to fix it
tk = re.sub(r'float\(v, settings\.save\(\)\)\)+', r'float(v)), settings.save())', tk)

# For ints: int(float(v, settings.save())))))
tk = re.sub(r'int\(float\(v, settings\.save\(\)\)\)+', r'int(float(v))), settings.save())', tk)

with open("src/dashboard.py", "w") as f:
    f.write(tk)
