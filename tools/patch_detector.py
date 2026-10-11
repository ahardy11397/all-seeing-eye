import re
with open("src/detector.py", "r") as f:
    content = f.read()

# Replace self.parked_drift_px with settings.parked_drift_px
content = re.sub(r'self\.parked_drift_px: int = 25', '', content)
content = re.sub(r'self\.parked_drift_px', 'settings.parked_drift_px', content)

with open("src/detector.py", "w") as f:
    f.write(content)
