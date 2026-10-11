import re

with open("src/dashboard_server.py", "r") as f:
    content = f.read()

# I need to restore the JS to be fully correct.
correct_js = """
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

let pushTimer = null;
function push(patch) {
  clearTimeout(pushTimer);
  pushTimer = setTimeout(() =>
    fetch('/api/settings', {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(patch)}), 120);
}

document.getElementById('reset').onclick = () => {
  const defaults = {min_confidence: 0.7, min_box_area: 8000, required_detections: 3,
                    detection_interval: 3, parked_cooldown_s: 20, parked_drift_px: 8,
                    smoothing: 0.18, eye_type: 'human'};
  push(defaults);
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
    r'// -- settings: load once, then push on change -------------------------------.*?// -- live status \+ image refresh ---------------------------------------------',
    correct_js.strip() + '\n\n// -- live status + image refresh ---------------------------------------------',
    content,
    flags=re.DOTALL
)

with open("src/dashboard_server.py", "w") as f:
    f.write(content)

print("Fixed JS in dashboard_server.py")
