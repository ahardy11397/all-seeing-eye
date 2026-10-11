with open("src/dashboard.py", "r") as f:
    tk = f.read()

tk = tk.replace('settings.parked_drift_px = 25\n        self.destroy()', 'settings.parked_drift_px = 25\n        settings.save()\n        self.destroy()')

with open("src/dashboard.py", "w") as f:
    f.write(tk)
