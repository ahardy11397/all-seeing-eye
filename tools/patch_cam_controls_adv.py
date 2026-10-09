import re

with open("src/dashboard_server.py", "r") as f:
    content = f.read()

post_logic_old = """
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
"""

post_logic_new = """
            try:
                import requests
                val = cmd.get("value")
                if action == "focus":
                    requests.get(f"{base_url}/focus", timeout=2)
                elif action == "torch":
                    requests.get(f"{base_url}/enabletorch" if val else f"{base_url}/disabletorch", timeout=2)
                elif action == "zoom":
                    requests.get(f"{base_url}/ptz?zoom={val}", timeout=2)
                else:
                    requests.get(f"{base_url}/settings/{action}?set={val}", timeout=2)
            except Exception as e:
"""
content = content.replace(post_logic_old.strip("\n"), post_logic_new.strip("\n"))

html_old = """
    <div class="ctl" style="display: flex; gap: 8px;">
      <button class="btn" id="cam_focus" style="margin-top: 0; background: #5f6368; color: #fff;">Autofocus</button>
      <button class="btn" id="cam_torch" style="margin-top: 0; background: #5f6368; color: #fff;">Toggle Flash</button>
    </div>
    <div class="ctl"><label>Zoom <output id="o_cam_zoom">0</output></label>
      <input type="range" id="cam_zoom" min="0" max="100" step="1" value="0">
    </div>
  </div>
"""

html_new = """
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
    <div class="ctl"><label>Exposure <output id="o_cam_exposure">0</output></label>
      <input type="range" id="cam_exposure" min="-12" max="12" step="1" value="0">
    </div>
    <div class="ctl"><label>Gain <output id="o_cam_gain">0</output></label>
      <input type="range" id="cam_gain" min="0" max="100" step="1" value="0">
    </div>
    <div class="ctl"><label>Night Mode Exposure <output id="o_cam_night_vision_exposure">0</output></label>
      <input type="range" id="cam_night_vision_exposure" min="-12" max="12" step="1" value="0">
    </div>
    <div class="ctl"><label>Night Mode Gain <output id="o_cam_night_vision_gain">0</output></label>
      <input type="range" id="cam_night_vision_gain" min="0" max="100" step="1" value="0">
    </div>
  </div>
"""
content = content.replace(html_old.strip("\n"), html_new.strip("\n"))

js_old = """
document.getElementById('cam_zoom').addEventListener('input', (e) => {
  document.getElementById('o_cam_zoom').textContent = e.target.value;
});
document.getElementById('cam_zoom').addEventListener('change', (e) => {
  camCmd('zoom', e.target.value);
});
"""

js_new = """
let nightState = false;
document.getElementById('cam_night').onclick = () => {
  nightState = !nightState;
  camCmd('night_vision', nightState ? 'on' : 'off');
};

const CAM_SLIDERS = [
  {id: 'cam_zoom', action: 'zoom'},
  {id: 'cam_focus_distance', action: 'focus_distance'},
  {id: 'cam_exposure', action: 'exposure_compensation'},
  {id: 'cam_gain', action: 'gain'},
  {id: 'cam_night_vision_exposure', action: 'night_vision_exposure'},
  {id: 'cam_night_vision_gain', action: 'night_vision_gain'}
];

CAM_SLIDERS.forEach(s => {
  const el = document.getElementById(s.id);
  const out = document.getElementById('o_' + s.id);
  el.addEventListener('input', (e) => { out.textContent = e.target.value; });
  el.addEventListener('change', (e) => { camCmd(s.action, e.target.value); });
});
"""
content = content.replace(js_old.strip("\n"), js_new.strip("\n"))

with open("src/dashboard_server.py", "w") as f:
    f.write(content)
