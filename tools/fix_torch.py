import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

old_torch = """document.getElementById('cam_torch').onclick = () => {
  torchState = !torchState;
  camCmd('torch', torchState);
};"""

new_torch = """const btnTorch = document.getElementById('cam_torch');
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

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
