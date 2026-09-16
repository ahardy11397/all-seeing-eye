const FIELDS = ['min_confidence','min_box_area','required_detections','detection_interval',
                'parked_cooldown_s','parked_drift_px','smoothing'];
const STR_FIELDS = ['eye_type'];

function fmt(v) { return (typeof v === 'number' && v < 10) ? v.toFixed(2) : Math.round(v); }

// mock document and fetch
const document = {
  getElementById: (id) => ({
    value: '',
    textContent: '',
    addEventListener: () => {},
    onclick: () => {}
  })
};
const fetch = () => Promise.resolve({json: () => Promise.resolve({settings: {}})});

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

// -- live status + image refresh ---------------------------------------------
function pollState() {
  fetch('/api/state').then(r => r.json()).then(s => {
    document.getElementById('fps').textContent = s.fps.toFixed(1);
    document.getElementById('state').textContent =
        s.parked ? 'parked-ignored' : (s.detection ? 'tracking' : 'idle');
    document.getElementById('target').textContent =
        s.iris ? Math.round(s.iris.x) + ', ' + Math.round(s.iris.y) : '–';
    const d = s.detection;
    document.getElementById('det').textContent = d ? d.label + ' (' + d.conf.toFixed(2) + ')' : 'none';
    document.getElementById('box').textContent = d ? d.box.join(', ') : '–';
  }).catch(() => {});
  setTimeout(pollState, 500);
}
pollState();
