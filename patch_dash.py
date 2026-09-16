with open("src/dashboard_server.py", "r") as f:
    content = f.read()

# Add bool_fields to POST handler
post_logic_old = """
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        applied = {}
"""
post_logic_new = """
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        bool_fields = {"blink_enabled"}
        applied = {}
"""
content = content.replace(post_logic_old.strip("\n"), post_logic_new.strip("\n"))

bool_logic_old = """
            elif key in str_fields:
                setattr(settings, key, str(value))
                applied[key] = str(value)
"""
bool_logic_new = """
            elif key in str_fields:
                setattr(settings, key, str(value))
                applied[key] = str(value)
            elif key in bool_fields:
                setattr(settings, key, bool(value))
                applied[key] = bool(value)
"""
content = content.replace(bool_logic_old.strip("\n"), bool_logic_new.strip("\n"))

# Add to state payload
state_old = """
                "eye_type": getattr(settings, "eye_type", "human"),
"""
state_new = """
                "eye_type": getattr(settings, "eye_type", "human"),
                "blink_enabled": getattr(settings, "blink_enabled", False),
"""
content = content.replace(state_old.strip("\n"), state_new.strip("\n"))

# Add HTML toggle
html_old = """
    <div class="ctl"><label>Eye smoothing <output id="o_smoothing"></output></label>
      <input type="range" id="smoothing" min="0.05" max="0.6" step="0.01"></div>
"""
html_new = """
    <div class="ctl"><label>Eye smoothing <output id="o_smoothing"></output></label>
      <input type="range" id="smoothing" min="0.05" max="0.6" step="0.01"></div>
    <div class="ctl" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <label for="blink_enabled" style="margin: 0; display: inline;">Enable random blinking</label>
      <input type="checkbox" id="blink_enabled" style="width: auto;">
    </div>
"""
content = content.replace(html_old.strip("\n"), html_new.strip("\n"))

# Add JS logic
js_old = """
const STR_FIELDS = ['eye_type'];
"""
js_new = """
const STR_FIELDS = ['eye_type'];
const BOOL_FIELDS = ['blink_enabled'];
"""
content = content.replace(js_old.strip("\n"), js_new.strip("\n"))

js_loop_old = """
  for (const f of STR_FIELDS) {
    const el = document.getElementById(f);
    if(s.settings[f]) { el.value = s.settings[f]; }
    el.addEventListener('change', () => {
      push({[f]: el.value});
    });
  }
"""
js_loop_new = """
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
"""
content = content.replace(js_loop_old.strip("\n"), js_loop_new.strip("\n"))

# defaults
reset_old = """
                    smoothing: 0.18, eye_type: 'human'};
"""
reset_new = """
                    smoothing: 0.18, eye_type: 'human', blink_enabled: false};
"""
content = content.replace(reset_old.strip("\n"), reset_new.strip("\n"))

reset_bool_old = """
  for (const f of STR_FIELDS) {
    document.getElementById(f).value = defaults[f];
  }
"""
reset_bool_new = """
  for (const f of STR_FIELDS) {
    document.getElementById(f).value = defaults[f];
  }
  for (const f of BOOL_FIELDS) {
    document.getElementById(f).checked = defaults[f];
  }
"""
content = content.replace(reset_bool_old.strip("\n"), reset_bool_new.strip("\n"))

with open("src/dashboard_server.py", "w") as f:
    f.write(content)

