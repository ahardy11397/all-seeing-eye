import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Add parked_drift_px to int_fields, and remove the explicit checking!
ds = re.sub(
    r'int_fields = \{"cam_zoom", "cam_focus_distance", "cam_exposure", "cam_gain", "cam_night_vision_exposure", "cam_night_vision_gain"\}',
    'int_fields = {"cam_zoom", "cam_focus_distance", "cam_exposure", "cam_gain", "cam_night_vision_exposure", "cam_night_vision_gain", "min_box_area", "required_detections", "detection_interval", "parked_drift_px"}',
    ds
)

ds = re.sub(
    r'elif key == "parked_drift_px":[\s\S]*?applied\[key\] = int\(float\(value\)\)',
    '',
    ds
)

# Wait! My regex earlier accidentally DELETED `elif key in int_fields` and `elif key in float_fields` completely from /api/settings !!!
# Let's completely rewrite the for key, value in updates.items(): block to be safe.
