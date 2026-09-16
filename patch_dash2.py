with open("src/dashboard_server.py", "r") as f:
    text = f.read()

old_html = """    <div class="ctl" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <label for="blink_enabled" style="margin: 0; display: inline;">Enable random blinking</label>
      <input type="checkbox" id="blink_enabled" style="width: auto;">
    </div>"""

new_html = """    <div class="ctl" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <label for="blink_enabled" style="margin: 0; display: inline;">Enable random blinking</label>
      <input type="checkbox" id="blink_enabled" style="width: auto;">
    </div>
    <div class="ctl" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <label for="tracking_enabled" style="margin: 0; display: inline;">Enable Motion Tracking (YOLO)</label>
      <input type="checkbox" id="tracking_enabled" style="width: auto;">
    </div>"""

text = text.replace(old_html, new_html)

with open("src/dashboard_server.py", "w") as f:
    f.write(text)
