import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Fix int_fields shadowing and parked_drift_px
old_lines = """        int_fields = {"min_box_area", "required_detections", "detection_interval",
                      "eye_smoothing"}
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        bool_fields = {"blink_enabled", "cam_night"}
        int_fields = {"cam_zoom", "cam_focus_distance", "cam_exposure", "cam_gain", "cam_night_vision_exposure", "cam_night_vision_gain"}"""

new_lines = """        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        bool_fields = {"blink_enabled", "cam_night"}
        int_fields = {"cam_zoom", "cam_focus_distance", "cam_exposure", "cam_gain", "cam_night_vision_exposure", "cam_night_vision_gain", "min_box_area", "required_detections", "detection_interval", "parked_drift_px"}"""

ds = ds.replace(old_lines, new_lines)

# Remove the explicit parked_drift_px checking since it's now in int_fields!
ds = re.sub(
    r'elif key == "parked_drift_px":[\s\S]*?applied\[key\] = int\(float\(value\)\)',
    '',
    ds
)

# And in state payload:
ds = ds.replace(
    '"parked_drift_px": self.server.detector.parked_drift_px,',
    '"parked_drift_px": settings.parked_drift_px,'
)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
