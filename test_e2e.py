import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))

import threading
import time
import requests
from config import settings
import dashboard_server as ds
import detector as det

detector = det.Detector()
server = ds.make_dashboard_server(None, 8099, detector)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()
time.sleep(1)

# Mock store.latest()
class MockStore:
    def latest(self):
        return (None, None, None, {"fps": 30, "detection": None, "parked": False, "iris": {"x": 0, "y": 0}})
ds.store = MockStore()

print("Initial min_confidence:", requests.get("http://127.0.0.1:8099/api/state").json()["settings"]["min_confidence"])
requests.post("http://127.0.0.1:8099/api/settings", json={"min_confidence": 0.88})
print("After update min_confidence:", requests.get("http://127.0.0.1:8099/api/state").json()["settings"]["min_confidence"])

print("Initial cam_zoom:", requests.get("http://127.0.0.1:8099/api/state").json()["settings"]["cam_zoom"])
requests.post("http://127.0.0.1:8099/api/camera", json={"action": "zoom", "value": 75})
print("After update cam_zoom:", requests.get("http://127.0.0.1:8099/api/state").json()["settings"]["cam_zoom"])

server.shutdown()
