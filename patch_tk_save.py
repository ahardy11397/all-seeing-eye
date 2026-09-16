import re
with open("src/dashboard.py", "r") as f:
    tk = f.read()

# Replace detector.parked_drift_px with settings.parked_drift_px
tk = tk.replace('getattr(self.detector, "parked_drift_px", 8)', 'getattr(settings, "parked_drift_px", 25)')
tk = tk.replace('setattr(self.detector, "parked_drift_px", int(float(v)))', 'setattr(settings, "parked_drift_px", int(float(v)))')
tk = tk.replace('self.detector.parked_drift_px = 8', 'settings.parked_drift_px = 25')

# Add settings.save() to all the lambda callbacks in SettingsPanel
def repl_lambda(m):
    # m.group(1) is the lambda body
    body = m.group(1)
    if "settings.save" not in body:
         return f'lambda v: ({body}, settings.save())'
    return m.group(0)

tk = re.sub(r'lambda v:\s*([^\)]+)', repl_lambda, tk)

with open("src/dashboard.py", "w") as f:
    f.write(tk)
