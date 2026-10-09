import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Extract CAM_SLIDERS and nightState definitions
cam_sliders_def = """const CAM_SLIDERS = [
  {id: 'cam_zoom', action: 'zoom'},
  {id: 'cam_focus_distance', action: 'focus_distance'},
  {id: 'cam_exposure', action: 'exposure_ns'},
  {id: 'cam_gain', action: 'iso'},
  {id: 'cam_night_vision_exposure', action: 'night_vision_average'},
  {id: 'cam_night_vision_gain', action: 'night_vision_gain'}
];"""

night_state_def = """let nightState = false;"""
torch_state_def = """let torchState = false;"""

# Remove them from their original locations
ds = ds.replace(cam_sliders_def, "")
ds = ds.replace(night_state_def, "")
ds = ds.replace(torch_state_def, "")

# Insert them at the top of the <script> block
script_top = """<script>
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
"""
ds = ds.replace("<script>", script_top)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
