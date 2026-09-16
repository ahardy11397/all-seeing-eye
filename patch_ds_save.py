import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

# Fix /api/settings save
settings_api_old = """
        for key, value in updates.items():
            if key in str_fields:
                setattr(settings, key, str(value))
                applied[key] = str(value)
            elif key in bool_fields:
                setattr(settings, key, bool(value))
                applied[key] = bool(value)
            elif key in int_fields:
                setattr(settings, key, int(value))
                applied[key] = int(value)
            elif key == "parked_drift_px":
                self.server.detector.parked_drift_px = int(float(value))  # type: ignore[attr-defined]
                applied[key] = int(float(value))

        self.send_response(200)
"""
settings_api_new = """
        for key, value in updates.items():
            if key in str_fields:
                setattr(settings, key, str(value))
                applied[key] = str(value)
            elif key in bool_fields:
                setattr(settings, key, bool(value))
                applied[key] = bool(value)
            elif key in int_fields:
                setattr(settings, key, int(value))
                applied[key] = int(value)
            elif key in float_fields:
                setattr(settings, key, float(value))
                applied[key] = float(value)
            elif key == "parked_drift_px":
                self.server.detector.parked_drift_px = int(float(value))  # type: ignore[attr-defined]
                applied[key] = int(float(value))
        
        settings.save()
        self.send_response(200)
"""
ds = ds.replace(settings_api_old.strip("\n"), settings_api_new.strip("\n"))


# Fix /api/camera save
cam_api_old = """
                elif action == "night_vision_gain": setattr(settings, "cam_night_vision_gain", v)
                elif action == "night_vision": setattr(settings, "cam_night", val is True or val == "on")
"""
cam_api_new = """
                elif action == "night_vision_gain": setattr(settings, "cam_night_vision_gain", v)
                elif action == "night_vision": setattr(settings, "cam_night", val is True or val == "on")
                
                settings.save()
"""
ds = ds.replace(cam_api_old.strip("\n"), cam_api_new.strip("\n"))

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
