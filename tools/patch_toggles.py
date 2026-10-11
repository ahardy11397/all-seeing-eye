import re

with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Fix torch endpoint, and fix val check for strings
# For torch:
ds = ds.replace(
    'requests.get(f"{base_url}/settings/torch?set=on" if val else f"{base_url}/settings/torch?set=off", timeout=2)',
    'requests.get(f"{base_url}/enabletorch" if val else f"{base_url}/disabletorch", timeout=2)'
)

# For night_vision:
# val could be boolean or 'on'/'off'
ds = ds.replace(
    'elif action == "night_vision": setattr(settings, "cam_night", bool(val))',
    'elif action == "night_vision": setattr(settings, "cam_night", val is True or val == "on")'
)

ds = ds.replace(
    'requests.get(f"{base_url}/settings/night_vision?set=on" if val else f"{base_url}/settings/night_vision?set=off", timeout=2)',
    'is_on = (val is True or val == "on")\n                    requests.get(f"{base_url}/settings/night_vision?set=on" if is_on else f"{base_url}/settings/night_vision?set=off", timeout=2)'
)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
