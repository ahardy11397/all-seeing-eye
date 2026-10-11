import re

with open("src/dashboard_server.py", "r") as f:
    content = f.read()

# 1. Handle string updates
post_updates = """
        int_fields = {"min_box_area", "required_detections", "detection_interval",
                      "eye_smoothing"}
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
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
            elif key == "parked_drift_px":
"""
content = re.sub(
    r'        int_fields = \{"min_box_area",.*?elif key == "parked_drift_px":',
    post_updates.strip(),
    content,
    flags=re.DOTALL
)

# 2. Expose eye_type in state
state_payload = """
                "parked_drift_px": getattr(self.server.detector, "parked_drift_px", 8),  # type: ignore[attr-defined]
                "smoothing": settings.smoothing,
                "eye_type": getattr(settings, "eye_type", "human"),
"""
content = re.sub(
    r'                "parked_drift_px": getattr\(self\.server\.detector, "parked_drift_px", 8\),.*?type: ignore\[attr-defined\].*?"smoothing": settings\.smoothing,',
    state_payload.strip(),
    content,
    flags=re.DOTALL
)

# 3. Add to UI
ui_controls = """
    <div class="card"><h2>Settings</h2>
    <div class="ctl" style="margin-bottom: 12px;"><label>Eye type</label>
      <select id="eye_type" style="width: 100%; padding: 4px; background: #202124; color: #e8eaed; border: 1px solid #5f6368; border-radius: 4px;">
        <option value="human">Human (Default)</option>
        <option value="monster">Monster</option>
      </select>
    </div>
"""
content = content.replace('<div class="card"><h2>Settings</h2>', ui_controls.strip())

# 4. Add fields to js FIELDS
js_fields = """
const FIELDS = ['min_confidence','min_box_area','required_detections','detection_interval',
                'parked_cooldown_s','parked_drift_px','smoothing'];
const STR_FIELDS = ['eye_type'];
"""
content = content.replace(
    "const FIELDS = ['min_confidence','min_box_area','required_detections','detection_interval',\n                'parked_cooldown_s','parked_drift_px','smoothing'];",
    js_fields.strip()
)

# 5. Populate and listen to string fields
js_populate = """
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
});
"""
content = re.sub(
    r'// -- settings: load once, then push on change -------------------------------.*?\}\);',
    js_populate.strip(),
    content,
    flags=re.DOTALL
)

# 6. Default resets
reset_defaults = """
document.getElementById('reset').onclick = () => {
  const defaults = {min_confidence: 0.7, min_box_area: 8000, required_detections: 3,
                    detection_interval: 3, parked_cooldown_s: 20, parked_drift_px: 8,
                    smoothing: 0.18, eye_type: "human"};
"""
content = re.sub(
    r"document\.getElementById\('reset'\)\.onclick = \(\) => \{.*?smoothing: 0\.18\};",
    reset_defaults.strip(),
    content,
    flags=re.DOTALL
)

reset_apply = """
  for (const f of FIELDS) {
    document.getElementById(f).value = defaults[f];
    document.getElementById('o_' + f).textContent = fmt(defaults[f]);
  }
  for (const f of STR_FIELDS) {
    document.getElementById(f).value = defaults[f];
  }
};
"""
content = re.sub(
    r"  for \(const f of FIELDS\) \{.*?\}\n\};",
    reset_apply.strip(),
    content,
    flags=re.DOTALL
)


with open("src/dashboard_server.py", "w") as f:
    f.write(content)

print("Patched dashboard_server.py")
