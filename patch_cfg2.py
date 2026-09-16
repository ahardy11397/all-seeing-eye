import re
with open("src/config.py", "r") as f:
    cfg = f.read()

# Add parked_drift_px if it doesn't exist
if "parked_drift_px" not in cfg:
    cfg = re.sub(r'(parked_cooldown_s: float = 20\.0)', r'\1\n    parked_drift_px: int = 25', cfg)

with open("src/config.py", "w") as f:
    f.write(cfg)
