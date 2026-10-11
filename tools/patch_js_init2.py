import re

with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Fix the bool array to include cam_night
js_bool_old = "const BOOL_FIELDS = ['blink_enabled'];"
js_bool_new = "const BOOL_FIELDS = ['blink_enabled'];" # I'll manually set cam_night since it's a toggle button, not a checkbox

js_fetch_old = """
  for (const f of BOOL_FIELDS) {
    const el = document.getElementById(f);
    el.checked = s.settings[f];
    el.addEventListener('change', () => {
      push({[f]: el.checked});
    });
  }
});
"""

js_fetch_new = """
  for (const f of BOOL_FIELDS) {
    const el = document.getElementById(f);
    el.checked = s.settings[f];
    el.addEventListener('change', () => {
      push({[f]: el.checked});
    });
  }
  
  CAM_SLIDERS.forEach(s_cam => {
      const el = document.getElementById(s_cam.id);
      const out = document.getElementById('o_' + s_cam.id);
      if (s.settings[s_cam.id] !== undefined) {
          el.value = s.settings[s_cam.id];
          out.textContent = el.value;
      }
  });
  
  if (s.settings.cam_night !== undefined) {
      nightState = s.settings.cam_night;
  }
});
"""

ds = ds.replace(js_fetch_old.strip("\n"), js_fetch_new.strip("\n"))

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
