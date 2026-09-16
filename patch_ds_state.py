import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Add int_fields parsing
post_fields_old = """
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        bool_fields = {"blink_enabled"}
"""
post_fields_new = """
        float_fields = {"min_confidence", "parked_cooldown_s", "smoothing"}
        str_fields = {"eye_type"}
        bool_fields = {"blink_enabled", "cam_night"}
        int_fields = {"cam_zoom", "cam_focus_distance", "cam_exposure", "cam_gain", "cam_night_vision_exposure", "cam_night_vision_gain"}
"""
ds = ds.replace(post_fields_old.strip("\n"), post_fields_new.strip("\n"))

parse_old = """
            elif key in bool_fields:
                setattr(settings, key, bool(value))
                applied[key] = bool(value)
"""
parse_new = """
            elif key in bool_fields:
                setattr(settings, key, bool(value))
                applied[key] = bool(value)
            elif key in int_fields:
                setattr(settings, key, int(value))
                applied[key] = int(value)
"""
ds = ds.replace(parse_old.strip("\n"), parse_new.strip("\n"))

# Add to state payload
state_old = """
                "blink_enabled": getattr(settings, "blink_enabled", False),
"""
state_new = """
                "blink_enabled": getattr(settings, "blink_enabled", False),
                "cam_night": getattr(settings, "cam_night", False),
                "cam_zoom": getattr(settings, "cam_zoom", 0),
                "cam_focus_distance": getattr(settings, "cam_focus_distance", 0),
                "cam_exposure": getattr(settings, "cam_exposure", 50),
                "cam_gain": getattr(settings, "cam_gain", 50),
                "cam_night_vision_exposure": getattr(settings, "cam_night_vision_exposure", 50),
                "cam_night_vision_gain": getattr(settings, "cam_night_vision_gain", 50),
"""
ds = ds.replace(state_old.strip("\n"), state_new.strip("\n"))

# Fix the exponential mapping in the /api/camera POST
# and ALSO save the value to settings so it persists even if they don't click Save!
cam_api_old = """
                def map_slider(act, val_0_100):
                    v = int(float(val_0_100))
                    arr = self.__class__._camera_avail.get(act)
                    if arr:
                        idx = int(v * (len(arr) - 1) / 100.0)
                        return arr[idx]
                    return val_0_100
                
                # Prerequisites
                if action in ["exposure_ns", "iso"]:
                    requests.get(f"{base_url}/settings/manual_sensor?set=on", timeout=1)
                elif action == "focus_distance":
                    requests.get(f"{base_url}/settings/focusmode?set=off", timeout=1)
                elif action in ["night_vision_gain", "night_vision_average"]:
                    requests.get(f"{base_url}/settings/night_vision?set=on", timeout=1)

                if action == "focus":
                    requests.get(f"{base_url}/focus", timeout=2)
                elif action == "torch":
                    requests.get(f"{base_url}/settings/torch?set=on" if val else f"{base_url}/settings/torch?set=off", timeout=2)
                elif action == "zoom":
                    requests.get(f"{base_url}/ptz?zoom={val}", timeout=2)
                elif action in ["exposure_ns", "iso", "focus_distance", "night_vision_gain"]:
                    requests.get(f"{base_url}/settings/{action}?set={map_slider(action, val)}", timeout=2)
                elif action == "night_vision_average":
                    # map 0-100 to 1-10
                    v = max(1, int(float(val) / 10.0))
                    requests.get(f"{base_url}/settings/{action}?set={v}", timeout=2)
                else:
                    requests.get(f"{base_url}/settings/{action}?set={val}", timeout=2)
"""

cam_api_new = """
                import math
                v = int(float(val)) if val is not None else 0
                
                # Update persistent settings so UI doesn't reset on refresh
                if action == "zoom": setattr(settings, "cam_zoom", v)
                elif action == "focus_distance": setattr(settings, "cam_focus_distance", v)
                elif action == "exposure_ns": setattr(settings, "cam_exposure", v)
                elif action == "iso": setattr(settings, "cam_gain", v)
                elif action == "night_vision_average": setattr(settings, "cam_night_vision_exposure", v)
                elif action == "night_vision_gain": setattr(settings, "cam_night_vision_gain", v)
                elif action == "night_vision": setattr(settings, "cam_night", bool(val))
                
                # Prerequisites
                if action in ["exposure_ns", "iso"]:
                    requests.get(f"{base_url}/settings/manual_sensor?set=on", timeout=1)
                elif action == "focus_distance":
                    requests.get(f"{base_url}/settings/focusmode?set=off", timeout=1)

                if action == "focus":
                    requests.get(f"{base_url}/focus", timeout=2)
                elif action == "torch":
                    requests.get(f"{base_url}/settings/torch?set=on" if val else f"{base_url}/settings/torch?set=off", timeout=2)
                elif action == "zoom":
                    # IP Webcam zoom is 100 to 1000
                    z = int(100 + v * 9.0)
                    requests.get(f"{base_url}/ptz?zoom={z}", timeout=2)
                elif action == "exposure_ns":
                    # Exponential mapping: 78432 to 9540712800
                    min_exp, max_exp = math.log(78432), math.log(9540712800)
                    exp_val = int(math.exp(min_exp + (v / 100.0) * (max_exp - min_exp)))
                    requests.get(f"{base_url}/settings/exposure_ns?set={exp_val}", timeout=2)
                elif action == "iso":
                    # Exponential mapping: 50 to 800
                    min_iso, max_iso = math.log(50), math.log(800)
                    iso_val = int(math.exp(min_iso + (v / 100.0) * (max_iso - min_iso)))
                    requests.get(f"{base_url}/settings/iso?set={iso_val}", timeout=2)
                elif action == "focus_distance":
                    # Linear 0.0 to 10.0
                    requests.get(f"{base_url}/settings/focus_distance?set={v / 10.0}", timeout=2)
                elif action == "night_vision_gain":
                    # Linear 0.5 to 10.0
                    gain = 0.5 + (v / 100.0) * 9.5
                    requests.get(f"{base_url}/settings/night_vision_gain?set={gain}", timeout=2)
                elif action == "night_vision_average":
                    # Map 0-100 to 1-10
                    requests.get(f"{base_url}/settings/night_vision_average?set={max(1, int(v / 10.0))}", timeout=2)
                elif action == "night_vision":
                    requests.get(f"{base_url}/settings/night_vision?set=on" if val else f"{base_url}/settings/night_vision?set=off", timeout=2)
                else:
                    requests.get(f"{base_url}/settings/{action}?set={val}", timeout=2)
"""
ds = ds.replace(cam_api_old.strip("\n"), cam_api_new.strip("\n"))

# Remove the old _camera_avail fetching since we are using explicit math now
avail_fetch = """
                # Fetch available values if needed for mapping
                if not hasattr(self.__class__, "_camera_avail"):
                    try:
                        resp = requests.get(f"{base_url}/status.json?show_avail=1", timeout=2)
                        self.__class__._camera_avail = resp.json().get("avail", {})
                    except:
                        self.__class__._camera_avail = {}
"""
ds = ds.replace(avail_fetch.strip("\n"), "")

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
