with open("src/dashboard.py", "r") as f:
    tk = f.read()

import re
tk = re.sub(r'lambda v: \(setattr\(settings, "([^"]+)", (int\(float\(v\)\)|float\(v\))\), settings\.save\(\)\)',
            r'lambda v: (setattr(settings, "\1", \2), settings.save()))', tk)

with open("src/dashboard.py", "w") as f:
    f.write(tk)
