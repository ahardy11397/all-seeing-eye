with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Update night button logic
old_night = """document.getElementById('cam_night').onclick = () => {
  nightState = !nightState;
  camCmd('night_vision', nightState ? 'on' : 'off');
};"""

new_night = """const btnNight = document.getElementById('cam_night');
function updateNightBtn() {
  btnNight.textContent = nightState ? 'Night Mode: ON' : 'Night Mode: OFF';
  btnNight.style.background = nightState ? '#8ab4f8' : '#5f6368';
  btnNight.style.color = nightState ? '#000' : '#fff';
}
btnNight.onclick = () => {
  nightState = !nightState;
  updateNightBtn();
  camCmd('night_vision', nightState ? 'on' : 'off');
};"""
ds = ds.replace(old_night, new_night)

# Update torch button logic
old_torch = """document.getElementById('cam_flash').onclick = () => {
  torchState = !torchState;
  camCmd('torch', torchState ? 'on' : 'off');
};"""

new_torch = """const btnTorch = document.getElementById('cam_flash');
function updateTorchBtn() {
  btnTorch.textContent = torchState ? 'Flash: ON' : 'Flash: OFF';
  btnTorch.style.background = torchState ? '#8ab4f8' : '#5f6368';
  btnTorch.style.color = torchState ? '#000' : '#fff';
}
btnTorch.onclick = () => {
  torchState = !torchState;
  updateTorchBtn();
  camCmd('torch', torchState ? 'on' : 'off');
};"""
ds = ds.replace(old_torch, new_torch)

# We also need to call updateNightBtn() inside the fetch block where nightState is initialized!
old_fetch = """  if (s.settings.cam_night !== undefined) {
      nightState = s.settings.cam_night;
  }
});"""

new_fetch = """  if (s.settings.cam_night !== undefined) {
      nightState = s.settings.cam_night;
      updateNightBtn();
  }
});"""
ds = ds.replace(old_fetch, new_fetch)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
