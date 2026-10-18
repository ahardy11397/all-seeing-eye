with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

ds = ds.replace(
    '"parked_drift_px": getattr(self.server.detector, "parked_drift_px", 8),',
    '"parked_drift_px": settings.parked_drift_px,'
)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
