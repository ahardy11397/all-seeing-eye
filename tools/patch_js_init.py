import re

with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

js_old = """
CAM_SLIDERS.forEach(s => {
  const el = document.getElementById(s.id);
  const out = document.getElementById('o_' + s.id);
  el.addEventListener('input', (e) => { out.textContent = e.target.value; });
  el.addEventListener('change', (e) => { camCmd(s.action, e.target.value); });
});
"""

js_new = """
CAM_SLIDERS.forEach(s => {
  const el = document.getElementById(s.id);
  const out = document.getElementById('o_' + s.id);
  
  // Try to load initial value from state
  fetch('/api/state').then(r => r.json()).then(state => {
     if (state.settings[s.id] !== undefined) {
         el.value = state.settings[s.id];
         out.textContent = el.value;
     }
  }).catch(() => {});

  el.addEventListener('input', (e) => { out.textContent = e.target.value; });
  el.addEventListener('change', (e) => { camCmd(s.action, e.target.value); });
});

let nightState = false;
fetch('/api/state').then(r => r.json()).then(state => {
    if (state.settings.cam_night !== undefined) {
        nightState = state.settings.cam_night;
    }
}).catch(() => {});
"""

# Wait, we already have a fetch('/api/state') loop in the JS!
# I can just append my initialization inside that loop!
