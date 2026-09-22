from __future__ import annotations

import io
import json
import math
import requests
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
        if path == "/api/camera":
            length = int(self.headers.get("Content-Length", 0))
            try:
                cmd = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_error(400)
                return
            
            base_url = settings.camera_url.rsplit("/", 1)[0]
            action = cmd.get("action")
            
            try:
                val = cmd.get("value")
                


                v = int(float(val)) if val is not None else 0
                
                # Update persistent settings so UI doesn't reset on refresh
                if action == "zoom": setattr(settings, "cam_zoom", v)
                elif action == "focus_distance": setattr(settings, "cam_focus_distance", v)
                elif action == "exposure_ns": setattr(settings, "cam_exposure", v)
                elif action == "iso": setattr(settings, "cam_gain", v)
                elif action == "night_vision_average": setattr(settings, "cam_night_vision_exposure", v)
                elif action == "night_vision_gain": setattr(settings, "cam_night_vision_gain", v)
                elif action == "night_vision": setattr(settings, "cam_night", val is True or val == "on")
                
                
                settings.save()
                settings.save()
                
                # Prerequisites
                if action in ["exposure_ns", "iso"]:
                    requests.get(f"{base_url}/settings/manual_sensor?set=on", timeout=1)
                elif action == "focus_distance":
                    requests.get(f"{base_url}/settings/focusmode?set=off", timeout=1)

                if action == "focus":
                    requests.get(f"{base_url}/focus", timeout=2)
                elif action == "torch":
                    requests.get(f"{base_url}/enabletorch" if val else f"{base_url}/disabletorch", timeout=2)
                elif action == "zoom":
                    # IP Webcam zoom is 100 to 1000
                    z = int(100 + v * 9.0)
                    requests.get(f"{base_url}/ptz?zoom={z}", timeout=2)
                elif action == "exposure_ns":
                    # Exponential mapping: 78432 to 9540712800
                    min_exp, max_exp = math.log(78432), math.log(9540712800)
                    exp_val = int(math.exp(min_exp + (v / 100.0) * (max_exp - min_exp)))
                    requests.get(f"{base_url}/settings/exposure_ns?set={exp_val}", timeout=2)
                elif action == "iso":
                    # Exponential mapping: 50 to 800
                    min_iso, max_iso = math.log(50), math.log(800)
                    iso_val = int(math.exp(min_iso + (v / 100.0) * (max_iso - min_iso)))
                    requests.get(f"{base_url}/settings/iso?set={iso_val}", timeout=2)
                elif action == "focus_distance":
                    # Linear 0.0 to 10.0
                    requests.get(f"{base_url}/settings/focus_distance?set={v / 10.0}", timeout=2)
                elif action == "night_vision_gain":
                    # Linear 0.5 to 10.0
                    gain = 0.5 + (v / 100.0) * 9.5
                    requests.get(f"{base_url}/settings/night_vision_gain?set={gain}", timeout=2)
                elif action == "night_vision_average":
                    # Map 0-100 to 1-10
                    requests.get(f"{base_url}/settings/night_vision_average?set={max(1, int(v / 10.0))}", timeout=2)
                elif action == "night_vision":
                    is_on = (val is True or val == "on")
                    requests.get(f"{base_url}/settings/night_vision?set=on" if is_on else f"{base_url}/settings/night_vision?set=off", timeout=2)
                else:
                    requests.get(f"{base_url}/settings/{action}?set={val}", timeout=2)
            except Exception as e:
                print("Camera API error:", e)
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")
            return

        if path != "/api/settings":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            updates = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self.send_error(400)
            return

        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        bool_fields = {"blink_enabled", "cam_night", "tracking_enabled"}
        int_fields = {"cam_zoom", "cam_focus_distance", "cam_exposure", "cam_gain", "cam_night_vision_exposure", "cam_night_vision_gain", "min_box_area", "required_detections", "detection_interval", "parked_drift_px"}
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
            elif key in bool_fields:
                setattr(settings, key, bool(value))
                applied[key] = bool(value)
            
            

        
        settings.save()
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
                "parked_drift_px": settings.parked_drift_px,  # type: ignore[attr-defined]
                "smoothing": settings.smoothing,
                "eye_type": getattr(settings, "eye_type", "human"),
                "blink_enabled": getattr(settings, "blink_enabled", False),
                "tracking_enabled": getattr(settings, "tracking_enabled", True),
                "cam_night": getattr(settings, "cam_night", False),
                "cam_zoom": getattr(settings, "cam_zoom", 0),
                "cam_focus_distance": getattr(settings, "cam_focus_distance", 0),
                "cam_exposure": getattr(settings, "cam_exposure", 50),
                "cam_gain": getattr(settings, "cam_gain", 50),
                "cam_night_vision_exposure": getattr(settings, "cam_night_vision_exposure", 50),
                "cam_night_vision_gain": getattr(settings, "cam_night_vision_gain", 50),
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All-Seeing Eye — Dashboard</title>
<style>
  :root { color-scheme: dark; }
  body { margin: 0; background: #0d0f12; color: #e8eaed;
         font: 14px/1.45 system-ui, sans-serif; }
  header { padding: 14px 20px; background: #16191d; display: flex;
           align-items: baseline; gap: 18px; flex-wrap: wrap; }
  header h1 { font-size: 18px; margin: 0; }
  #status { font-size: 13px; color: #9aa0a6; }
  #status b { color: #81c995; }
  
  main { display: grid; gap: 16px; padding: 16px; max-width: 1500px; margin: 0 auto; 
         grid-template-columns: 1fr; }
  @media (min-width: 768px) {
      main { grid-template-columns: 1fr 1fr; }
  }
  @media (min-width: 1200px) {
      main { grid-template-columns: 1fr 1fr 340px; }
      .card-eye { grid-column: 1; grid-row: 1 / span 2; }
      .card-cam { grid-column: 2; grid-row: 1 / span 2; }
      .card-settings { grid-column: 3; grid-row: 1; }
      .card-controls { grid-column: 3; grid-row: 2; }
  }

  .card { background: #16191d; border-radius: 10px; padding: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
  .card h2 { margin: 0 0 12px; font-size: 13px; text-transform: uppercase;
             letter-spacing: .08em; color: #9aa0a6; border-bottom: 1px solid #2c313a; padding-bottom: 8px; }
  img { width: 100%; border-radius: 6px; background: #000; display: block; object-fit: contain; }
  .info { margin-top: 10px; font-size: 12px; color: #bdc1c6; background: #202124; padding: 8px; border-radius: 6px; }
  .info span { color: #81c995; font-weight: 600; }
  /* settings */
  .ctl { margin: 12px 0; }
  .ctl label { display: flex; justify-content: space-between; font-size: 13px;
               color: #e8eaed; margin-bottom: 6px; font-weight: 500; }
  .ctl label output { color: #8ab4f8; font-weight: 600; }
  input[type=range] { width: 100%; accent-color: #8ab4f8; margin: 4px 0; }
  .btn { margin-top: 14px; width: 100%; padding: 10px; border: 0; border-radius: 6px;
         background: #8ab4f8; color: #202124; font-weight: 600; cursor: pointer; transition: background 0.2s; }
  .btn:hover { background: #aecbfa; }
  .btn:active { filter: brightness(.9); }
  .hint { font-size: 11px; color: #80868b; margin-top: 8px; text-align: center; }
  
  /* Select and Checkbox styling */
  select { width: 100%; padding: 8px; background: #202124; color: #e8eaed; border: 1px solid #5f6368; border-radius: 6px; font-size: 14px; }
  input[type=checkbox] { width: 18px; height: 18px; accent-color: #8ab4f8; cursor: pointer; }
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
  <div class="card card-eye"><h2>Projected eye</h2><img id="eye" src="/api/eye.jpg"></div>
  <div class="card card-cam"><h2>Camera + tracking</h2><img id="cam" src="/api/cam.jpg">
    <div class="info">Detection: <span id="det">–</span> ·
      box: <span id="box">–</span></div></div>
  <div class="card card-settings"><h2>Settings</h2>
    <div class="ctl" style="margin-bottom: 12px;"><label>Eye type</label>
      <select id="eye_type" style="width: 100%; padding: 4px; background: #202124; color: #e8eaed; border: 1px solid #5f6368; border-radius: 4px;">
                <option value="human">Human (Default)</option>
        <option value="monster">Monster</option>
        <option value="zombie">Zombie</option>
        <option value="dragon">Dragon</option>
        <option value="snake">Snake</option>
        <option value="spider">Spider</option>
        <option value="bug">Bug</option>
        <option value="creepy_figure">Creepy Figure</option>
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
    <div class="ctl" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <label for="blink_enabled" style="margin: 0; display: inline;">Enable random blinking</label>
      <input type="checkbox" id="blink_enabled" style="width: auto;">
    </div>
    <div class="ctl" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <label for="tracking_enabled" style="margin: 0; display: inline;">Enable Motion Tracking (YOLO)</label>
      <input type="checkbox" id="tracking_enabled" style="width: auto;">
    </div>
    <button class="btn" id="reset">Reset to defaults</button>
    <div class="hint">Changes apply instantly on the next frame.</div>
  </div>
  <div class="card card-controls"><h2>Camera Controls</h2>
    <div class="ctl" style="display: flex; flex-wrap: wrap; gap: 8px;">
      <button class="btn" id="cam_focus" style="margin-top: 0; flex: 1; background: #5f6368; color: #fff;">Autofocus</button>
      <button class="btn" id="cam_torch" style="margin-top: 0; flex: 1; background: #5f6368; color: #fff;">Toggle Flash</button>
      <button class="btn" id="cam_night" style="margin-top: 0; flex: 1; background: #5f6368; color: #fff;">Toggle Night Mode</button>
    </div>
    <div class="ctl"><label>Zoom <output id="o_cam_zoom">0</output></label>
      <input type="range" id="cam_zoom" min="0" max="100" step="1" value="0">
    </div>
    <div class="ctl"><label>Manual Focus <output id="o_cam_focus_distance">0</output></label>
      <input type="range" id="cam_focus_distance" min="0" max="100" step="1" value="0">
    </div>
    <div class="ctl"><label>Exposure <output id="o_cam_exposure">50</output></label>
      <input type="range" id="cam_exposure" min="0" max="100" step="1" value="50">
    </div>
    <div class="ctl"><label>Gain <output id="o_cam_gain">50</output></label>
      <input type="range" id="cam_gain" min="0" max="100" step="1" value="50">
    </div>
    <div class="ctl"><label>Night Mode Exposure <output id="o_cam_night_vision_exposure">50</output></label>
      <input type="range" id="cam_night_vision_exposure" min="0" max="100" step="1" value="50">
    </div>
    <div class="ctl"><label>Night Mode Gain <output id="o_cam_night_vision_gain">50</output></label>
      <input type="range" id="cam_night_vision_gain" min="0" max="100" step="1" value="50">
    </div>
  </div>
</main>
<script>
let torchState = false;
let nightState = false;
const CAM_SLIDERS = [
  {id: 'cam_zoom', action: 'zoom'},
  {id: 'cam_focus_distance', action: 'focus_distance'},
  {id: 'cam_exposure', action: 'exposure_ns'},
  {id: 'cam_gain', action: 'iso'},
  {id: 'cam_night_vision_exposure', action: 'night_vision_average'},
  {id: 'cam_night_vision_gain', action: 'night_vision_gain'}
];

const FIELDS = ['min_confidence','min_box_area','required_detections','detection_interval',
                'parked_cooldown_s','parked_drift_px','smoothing'];
const STR_FIELDS = ['eye_type'];
const BOOL_FIELDS = ['blink_enabled', 'tracking_enabled'];

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
  for (const f of BOOL_FIELDS) {
    const el = document.getElementById(f);
    el.checked = s.settings[f];
    el.addEventListener('change', () => {
      push({[f]: el.checked});
    });
  }
  
  CAM_SLIDERS.forEach(s_cam => {
      const el = document.getElementById(s_cam.id);
      const out = document.getElementById('o_' + s_cam.id);
      if (s.settings[s_cam.id] !== undefined) {
          el.value = s.settings[s_cam.id];
          out.textContent = el.value;
      }
  });
  
  if (s.settings.cam_night !== undefined) {
      nightState = s.settings.cam_night;
      updateNightBtn();
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
  const defaults = {min_confidence: 0.5, min_box_area: 1500, required_detections: 3,
                    detection_interval: 3, parked_cooldown_s: 20, parked_drift_px: 25,
                    smoothing: 0.18, eye_type: 'human', blink_enabled: false, tracking_enabled: true};
  push(defaults);
  for (const f of FIELDS) {
    document.getElementById(f).value = defaults[f];
    document.getElementById('o_' + f).textContent = fmt(defaults[f]);
  }
  for (const f of STR_FIELDS) {
    document.getElementById(f).value = defaults[f];
  }
  for (const f of BOOL_FIELDS) {
    document.getElementById(f).checked = defaults[f];
  }
};

// -- camera controls ---------------------------------------------------------

function camCmd(action, value=null) {
  fetch('/api/camera', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action, value})
  });
}
document.getElementById('cam_focus').onclick = () => camCmd('focus');
const btnTorch = document.getElementById('cam_torch');
function updateTorchBtn() {
  btnTorch.textContent = torchState ? 'Flash: ON' : 'Flash: OFF';
  btnTorch.style.background = torchState ? '#8ab4f8' : '#5f6368';
  btnTorch.style.color = torchState ? '#000' : '#fff';
}
btnTorch.onclick = () => {
  torchState = !torchState;
  updateTorchBtn();
  camCmd('torch', torchState ? 'on' : 'off');
};

const btnNight = document.getElementById('cam_night');
function updateNightBtn() {
  btnNight.textContent = nightState ? 'Night Mode: ON' : 'Night Mode: OFF';
  btnNight.style.background = nightState ? '#8ab4f8' : '#5f6368';
  btnNight.style.color = nightState ? '#000' : '#fff';
}
btnNight.onclick = () => {
  nightState = !nightState;
  updateNightBtn();
  camCmd('night_vision', nightState ? 'on' : 'off');
};



CAM_SLIDERS.forEach(s => {
  const el = document.getElementById(s.id);
  const out = document.getElementById('o_' + s.id);
  el.addEventListener('input', (e) => { out.textContent = e.target.value; });
  el.addEventListener('change', (e) => { camCmd(s.action, e.target.value); });
});

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
        self.send_header("Cache-Control", "no-store")
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
