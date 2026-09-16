with open("src/dashboard_server.py", "r") as f:
    text = f.read()

# 1. bool_fields
text = text.replace('bool_fields = {"blink_enabled", "cam_night"}', 'bool_fields = {"blink_enabled", "cam_night", "tracking_enabled"}')

# 2. state
text = text.replace('"blink_enabled": getattr(settings, "blink_enabled", False),', '"blink_enabled": getattr(settings, "blink_enabled", False),\n                "tracking_enabled": getattr(settings, "tracking_enabled", True),')

# 3. HTML
html_old = """    <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 20px;">
      <label for="blink_enabled" style="margin: 0; display: inline;">Enable random blinking</label>
      <input type="checkbox" id="blink_enabled" style="width: auto;">
    </div>"""

html_new = """    <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 20px;">
      <label for="blink_enabled" style="margin: 0; display: inline;">Enable random blinking</label>
      <input type="checkbox" id="blink_enabled" style="width: auto;">
      <div style="width: 20px;"></div>
      <label for="tracking_enabled" style="margin: 0; display: inline;">Enable Motion Tracking (YOLO)</label>
      <input type="checkbox" id="tracking_enabled" style="width: auto;">
    </div>"""
text = text.replace(html_old, html_new)

# 4. BOOL_FIELDS
text = text.replace("const BOOL_FIELDS = ['blink_enabled'];", "const BOOL_FIELDS = ['blink_enabled', 'tracking_enabled'];")

# 5. default settings
text = text.replace("smoothing: 0.18, eye_type: 'human', blink_enabled: false", "smoothing: 0.18, eye_type: 'human', blink_enabled: false, tracking_enabled: true")

with open("src/dashboard_server.py", "w") as f:
    f.write(text)
