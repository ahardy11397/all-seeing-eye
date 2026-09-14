from __future__ import annotations

import io
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config import settings


class StateStore:
    """Shared state between the render loop and the web dashboard."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._eye_jpeg: bytes | None = None
        self._cam_jpeg: bytes | None = None
        self._info: dict = {}
        self._seq = 0

    def publish(self, eye_jpeg: bytes, cam_jpeg: bytes, info: dict) -> None:
        with self._lock:
            self._eye_jpeg = eye_jpeg
            self._cam_jpeg = cam_jpeg
            self._info = info
            self._seq += 1

    def latest(self) -> tuple[int, bytes | None, bytes | None, dict]:
        with self._lock:
            return self._seq, self._eye_jpeg, self._cam_jpeg, dict(self._info)


store = StateStore()


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - stdlib signature
        pass

    def do_GET(self):  # noqa: N802
        path = self.path.split("?")[0]
        if path in ("/", "/dashboard"):
            self._html()
        elif path == "/api/state":
            self._state()
        elif path == "/api/eye.jpg":
            _, eye, _, _ = store.latest()
            self._jpeg(eye)
        elif path == "/api/cam.jpg":
            _, _, cam, _ = store.latest()
            self._jpeg(cam)
        else:
            self.send_error(404)

    def do_POST(self):  # noqa: N802
        path = self.path.split("?")[0]
        if path != "/api/settings":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            updates = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self.send_error(400)
            return

        int_fields = {"min_box_area", "required_detections", "detection_interval",
                      "eye_smoothing"}
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        applied = {}
        for key, value in updates.items():
            if key in int_fields:
                setattr(settings, key, int(float(value)))
                applied[key] = int(float(value))
            elif key in float_fields:
                setattr(settings, key, float(value))
                applied[key] = float(value)
            elif key in str_fields:
                setattr(settings, key, str(value))
                applied[key] = str(value)
            elif key == "parked_drift_px":
                self.server.detector.parked_drift_px = int(float(value))  # type: ignore[attr-defined]
                applied[key] = int(float(value))

        self.send_response(200)
        body = json.dumps({"ok": True, "applied": applied}).encode()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _jpeg(self, data: bytes | None) -> None:
        if data is None:
            self.send_error(503)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _state(self) -> None:
        _, _, _, info = store.latest()
        payload = {
            "fps": info.get("fps", 0.0),
            "detection": info.get("detection"),
            "parked": info.get("parked", False),
            "iris": info.get("iris", {"x": settings.width // 2, "y": settings.height // 2}),
            "settings": {
                "min_confidence": settings.min_confidence,
                "min_box_area": settings.min_box_area,
                "required_detections": settings.required_detections,
                "detection_interval": settings.detection_interval,
                "parked_cooldown_s": settings.parked_cooldown_s,
                "parked_drift_px": getattr(self.server.detector, "parked_drift_px", 8),  # type: ignore[attr-defined]
                "smoothing": settings.smoothing,
                "eye_type": getattr(settings, "eye_type", "human"),
            },
        }
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _html(self) -> None:
        html = """<!DOCTYPE html>
<html>
<head>
<title>All-Seeing Eye — Dashboard</title>
<style>
  :root { color-scheme: dark; }
  body { margin: 0; background: #0d0f12; color: #e8eaed;
         font: 14px/1.45 system-ui, sans-serif; }
  header { padding: 14px 20px; background: #16191d; display: flex;
           align-items: baseline; gap: 18px; }
  header h1 { font-size: 18px; margin: 0; }
  #status { font-size: 13px; color: #9aa0a6; }
  #status b { color: #81c995; }
  main { display: grid; grid-template-columns: 1fr 1fr 340px; gap: 16px;
         padding: 16px 20px; max-width: 1500px; margin: 0 auto; }
  .card { background: #16191d; border-radius: 10px; padding: 12px; }
  .card h2 { margin: 0 0 8px; font-size: 13px; text-transform: uppercase;
             letter-spacing: .08em; color: #9aa0a6; }
  img { width: 100%; border-radius: 6px; background: #000; display: block; }
  .info { margin-top: 8px; font-size: 12px; color: #bdc1c6; }
  .info span { color: #81c995; font-weight: 600; }
  /* settings */
  .ctl { margin: 10px 0; }
  .ctl label { display: flex; justify-content: space-between; font-size: 12.5px;
               color: #bdc1c6; margin-bottom: 4px; }
  .ctl label output { color: #8ab4f8; font-weight: 600; }
  input[type=range] { width: 100%; accent-color: #8ab4f8; }
  .btn { margin-top: 14px; width: 100%; padding: 8px; border: 0; border-radius: 6px;
         background: #8ab4f8; color: #202124; font-weight: 600; cursor: pointer; }
  .btn:active { filter: brightness(.9); }
  .hint { font-size: 11px; color: #80868b; margin-top: 6px; }
</style>
</head>
<body>
<header>
  <h1>All-Seeing Eye</h1>
  <div id="status">FPS <b id="fps">–</b> ·
    state <b id="state">–</b> ·
    target <b id="target">–</b></div>
</header>
<main>
  <div class="card"><h2>Projected eye</h2><img id="eye" src="/api/eye.jpg"></div>
  <div class="card"><h2>Camera + tracking</h2><img id="cam" src="/api/cam.jpg">
    <div class="info">Detection: <span id="det">–</span> ·
      box: <span id="box">–</span></div></div>
  <div class="card"><h2>Settings</h2>
    <div class="ctl" style="margin-bottom: 12px;"><label>Eye type</label>
      <select id="eye_type" style="width: 100%; padding: 4px; background: #202124; color: #e8eaed; border: 1px solid #5f6368; border-radius: 4px;">
        <option value="human">Human (Default)</option>
        <option value="monster">Monster</option>
      </select>
    </div>
    <div class="ctl"><label>Min confidence <output id="o_min_confidence"></output></label>
      <input type="range" id="min_confidence" min="0.10" max="0.95" step="0.01"></div>
    <div class="ctl"><label>Min object size (px²) <output id="o_min_box_area"></output></label>
      <input type="range" id="min_box_area" min="500" max="40000" step="100"></div>
    <div class="ctl"><label>Frames to confirm <output id="o_required_detections"></output></label>
      <input type="range" id="required_detections" min="1" max="10" step="1"></div>
    <div class="ctl"><label>Detect every N frames <output id="o_detection_interval"></output></label>
      <input type="range" id="detection_interval" min="1" max="10" step="1"></div>
    <div class="ctl"><label>Parked cooldown (s) <output id="o_parked_cooldown_s"></output></label>
      <input type="range" id="parked_cooldown_s" min="5" max="60" step="1"></div>
    <div class="ctl"><label>Parked drift (px) <output id="o_parked_drift_px"></output></label>
      <input type="range" id="parked_drift_px" min="2" max="40" step="1"></div>
    <div class="ctl"><label>Eye smoothing <output id="o_smoothing"></output></label>
      <input type="range" id="smoothing" min="0.05" max="0.6" step="0.01"></div>
    <button class="btn" id="reset">Reset to defaults</button>
    <div class="hint">Changes apply instantly on the next frame.</div>
  </div>
</main>
<script>
const FIELDS = ['min_confidence','min_box_area','required_detections','detection_interval',
                'parked_cooldown_s','parked_drift_px','smoothing'];
const STR_FIELDS = ['eye_type'];

function fmt(v) { return (typeof v === 'number' && v < 10) ? v.toFixed(2) : Math.round(v); }

// -- settings: load once, then push on change -------------------------------
fetch('/api/state').then(r => r.json()).then(s => {
  for (const f of FIELDS) {
    const el = document.getElementById(f);
    el.value = s.settings[f];
    document.getElementById('o_' + f).textContent = fmt(s.settings[f]);
    el.addEventListener('input', () => {
      document.getElementById('o_' + f).textContent = fmt(parseFloat(el.value));
      push({[f]: parseFloat(el.value)});
    });
  }
  for (const f of STR_FIELDS) {
    const el = document.getElementById(f);
    if(s.settings[f]) { el.value = s.settings[f]; }
    el.addEventListener('change', () => {
      push({[f]: el.value});
    });
  }
});

let pushTimer = null;
function push(patch) {
  clearTimeout(pushTimer);
  pushTimer = setTimeout(() =>
    fetch('/api/settings', {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(patch)}), 120);
}

document.getElementById('reset').onclick = () => {
  const defaults = {min_confidence: 0.7, min_box_area: 8000, required_detections: 3,
                    detection_interval: 3, parked_cooldown_s: 20, parked_drift_px: 8,
                    smoothing: 0.18, eye_type: 'human'};
  push(defaults);
  for (const f of FIELDS) {
    document.getElementById(f).value = defaults[f];
    document.getElementById('o_' + f).textContent = fmt(defaults[f]);
  }
  for (const f of STR_FIELDS) {
    document.getElementById(f).value = defaults[f];
  }
};

// -- live status + image refresh ---------------------------------------------
function pollState() {
  fetch('/api/state').then(r => r.json()).then(s => {
    document.getElementById('fps').textContent = s.fps.toFixed(1);
    document.getElementById('state').textContent =
        s.parked ? 'parked-ignored' : (s.detection ? 'tracking' : 'idle');
    document.getElementById('target').textContent =
        s.iris ? Math.round(s.iris.x) + ', ' + Math.round(s.iris.y) : '–';
    const d = s.detection;
    document.getElementById('det').textContent = d ? d.label + ' (' + d.conf.toFixed(2) + ')' : 'none';
    document.getElementById('box').textContent = d ? d.box.join(', ') : '–';
  }).catch(() => {});
  setTimeout(pollState, 500);
}
pollState();

function refreshImage(id, url) {
  const img = document.getElementById(id);
  fetch(url + '?t=' + Date.now()).then(r => r.blob()).then(b => {
    img.src = URL.createObjectURL(b);
  }).catch(() => {}).finally(() => setTimeout(() => refreshImage(id, url), 100));
}
refreshImage('eye', '/api/eye.jpg');
refreshImage('cam', '/api/cam.jpg');
</script>
</body>
</html>"""
        data = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_dashboard_server(store_ref: StateStore, port: int, detector) -> ThreadingHTTPServer:
    """detector is passed so parked_drift_px can be tuned live."""
    global store
    store = store_ref
    handler = type("BoundHandler", (DashboardHandler,), {"detector": detector})
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    server.detector = detector  # type: ignore[attr-defined]
    return server
