import re

# 1. Update dashboard_server.py
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Replace HTML sliders to be all 0 to 100
html_old = """
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
"""
html_new = """
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
"""
ds = ds.replace(html_old.strip("\n"), html_new.strip("\n"))

# Replace JS IDs if needed
js_old = """
const CAM_SLIDERS = [
  {id: 'cam_zoom', action: 'zoom'},
  {id: 'cam_focus_distance', action: 'focus_distance'},
  {id: 'cam_exposure', action: 'exposure_compensation'},
  {id: 'cam_gain', action: 'gain'},
  {id: 'cam_night_vision_exposure', action: 'night_vision_exposure'},
  {id: 'cam_night_vision_gain', action: 'night_vision_gain'}
];
"""
js_new = """
const CAM_SLIDERS = [
  {id: 'cam_zoom', action: 'zoom'},
  {id: 'cam_focus_distance', action: 'focus_distance'},
  {id: 'cam_exposure', action: 'exposure_ns'},
  {id: 'cam_gain', action: 'iso'},
  {id: 'cam_night_vision_exposure', action: 'night_vision_average'},
  {id: 'cam_night_vision_gain', action: 'night_vision_gain'}
];
"""
ds = ds.replace(js_old.strip("\n"), js_new.strip("\n"))

# Replace POST handler
post_old = """
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

post_new = """
            try:
                import requests
                val = cmd.get("value")
                
                # Fetch available values if needed for mapping
                if not hasattr(self.__class__, "_camera_avail"):
                    try:
                        resp = requests.get(f"{base_url}/status.json?show_avail=1", timeout=2)
                        self.__class__._camera_avail = resp.json().get("avail", {})
                    except:
                        self.__class__._camera_avail = {}

                def map_slider(act, val_0_100):
                    v = int(float(val_0_100))
                    arr = self.__class__._camera_avail.get(act)
                    if arr:
                        idx = int(v * (len(arr) - 1) / 100.0)
                        return arr[idx]
                    return val_0_100
                
                # Prerequisites
                if action in ["exposure_ns", "iso"]:
                    requests.get(f"{base_url}/settings/manual_sensor?set=on", timeout=1)
                elif action == "focus_distance":
                    requests.get(f"{base_url}/settings/focusmode?set=off", timeout=1)
                elif action in ["night_vision_gain", "night_vision_average"]:
                    requests.get(f"{base_url}/settings/night_vision?set=on", timeout=1)

                if action == "focus":
                    requests.get(f"{base_url}/focus", timeout=2)
                elif action == "torch":
                    requests.get(f"{base_url}/settings/torch?set=on" if val else f"{base_url}/settings/torch?set=off", timeout=2)
                elif action == "zoom":
                    requests.get(f"{base_url}/ptz?zoom={val}", timeout=2)
                elif action in ["exposure_ns", "iso", "focus_distance", "night_vision_gain"]:
                    requests.get(f"{base_url}/settings/{action}?set={map_slider(action, val)}", timeout=2)
                elif action == "night_vision_average":
                    # map 0-100 to 1-10
                    v = max(1, int(float(val) / 10.0))
                    requests.get(f"{base_url}/settings/{action}?set={v}", timeout=2)
                else:
                    requests.get(f"{base_url}/settings/{action}?set={val}", timeout=2)
            except Exception as e:
"""
ds = ds.replace(post_old.strip("\n"), post_new.strip("\n"))

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
