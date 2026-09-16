import re

with open("src/dashboard_server.py", "r") as f:
    content = f.read()

# 1. Add POST handling for /api/camera
post_logic_new = """
        if path == "/api/camera":
            length = int(self.headers.get("Content-Length", 0))
            try:
                import json
                cmd = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_error(400)
                return
            
            base_url = settings.camera_url.rsplit("/", 1)[0]
            action = cmd.get("action")
            
            try:
                import requests
                if action == "focus":
                    requests.get(f"{base_url}/focus", timeout=2)
                elif action == "torch":
                    state = cmd.get("value")
                    requests.get(f"{base_url}/enabletorch" if state else f"{base_url}/disabletorch", timeout=2)
                elif action == "zoom":
                    val = cmd.get("value")
                    requests.get(f"{base_url}/ptz?zoom={val}", timeout=2)
            except Exception as e:
                print("Camera API error:", e)
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")
            return

        if path != "/api/settings":
"""
content = content.replace('        if path != "/api/settings":', post_logic_new.strip("\n"))


# 2. Add HTML for camera controls
html_old = """    <button class="btn" id="reset">Reset to defaults</button>
    <div class="hint">Changes apply instantly on the next frame.</div>
  </div>
</main>"""

html_new = """    <button class="btn" id="reset">Reset to defaults</button>
    <div class="hint">Changes apply instantly on the next frame.</div>
  </div>
  <div class="card"><h2>Camera Controls</h2>
    <div class="ctl" style="display: flex; gap: 8px;">
      <button class="btn" id="cam_focus" style="margin-top: 0; background: #5f6368; color: #fff;">Autofocus</button>
      <button class="btn" id="cam_torch" style="margin-top: 0; background: #5f6368; color: #fff;">Toggle Flash</button>
    </div>
    <div class="ctl"><label>Zoom <output id="o_cam_zoom">0</output></label>
      <input type="range" id="cam_zoom" min="0" max="100" step="1" value="0">
    </div>
  </div>
</main>"""
content = content.replace(html_old, html_new)

# 3. Add JS for camera controls
js_old = """// -- live status + image refresh ---------------------------------------------"""

js_new = """// -- camera controls ---------------------------------------------------------
let torchState = false;
function camCmd(action, value=null) {
  fetch('/api/camera', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action, value})
  });
}
document.getElementById('cam_focus').onclick = () => camCmd('focus');
document.getElementById('cam_torch').onclick = () => {
  torchState = !torchState;
  camCmd('torch', torchState);
};
document.getElementById('cam_zoom').addEventListener('input', (e) => {
  document.getElementById('o_cam_zoom').textContent = e.target.value;
});
document.getElementById('cam_zoom').addEventListener('change', (e) => {
  camCmd('zoom', e.target.value);
});

// -- live status + image refresh ---------------------------------------------"""

content = content.replace(js_old, js_new)

with open("src/dashboard_server.py", "w") as f:
    f.write(content)
