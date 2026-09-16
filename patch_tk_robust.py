import re

with open("src/dashboard.py", "r") as f:
    content = f.read()

tk_old = """
        sliders = [
            ("Zoom", 0, 100, "/ptz?zoom="),
            ("Manual Focus", 0, 100, "/settings/focus_distance?set="),
            ("Exposure", -12, 12, "/settings/exposure_compensation?set="),
            ("Gain", 0, 100, "/settings/gain?set="),
            ("Night Mode Exposure", -12, 12, "/settings/night_vision_exposure?set="),
            ("Night Mode Gain", 0, 100, "/settings/night_vision_gain?set=")
        ]
        
        for label_text, min_val, max_val, path_prefix in sliders:
            tk.Label(outer, text=label_text, fg="#bdc1c6", bg="#181818", font=("Arial", 10)).pack(anchor="w", padx=4, pady=(8, 0))
            scale = tk.Scale(outer, from_=min_val, to=max_val, orient="horizontal", bg="#181818", fg="#8ab4f8", highlightthickness=0, borderwidth=0)
            scale.pack(fill="x", padx=4)
            # Use default arguments to capture the current path_prefix and scale inside the lambda
            scale.bind("<ButtonRelease-1>", lambda e, p=path_prefix, s=scale: cam_req(f"{p}{s.get()}"))
"""

tk_new = """
        # We fetch avail on first request in a real app, but for simplicity we send via dashboard_server if we can,
        # or we just rely on the user using the web dashboard.
        # But we'll just proxy the commands through a local function that calls the web dashboard API!
        # No, dashboard_server might not be running if they only ran dashboard.py.
        # We will just map it locally.
        
        sliders = [
            ("Zoom", 0, 100, "zoom"),
            ("Manual Focus", 0, 100, "focus_distance"),
            ("Exposure", 0, 100, "exposure_ns"),
            ("Gain", 0, 100, "iso"),
            ("Night Mode Exposure", 0, 100, "night_vision_average"),
            ("Night Mode Gain", 0, 100, "night_vision_gain")
        ]
        
        self._cam_avail = {}
        def do_cam_cmd(action, val):
            import requests
            base_url = settings.camera_url.rsplit("/", 1)[0]
            if not self._cam_avail:
                try:
                    self._cam_avail = requests.get(f"{base_url}/status.json?show_avail=1", timeout=2).json().get("avail", {})
                except:
                    pass
            
            def map_slider(act, v_0_100):
                arr = self._cam_avail.get(act)
                if arr:
                    idx = int(float(v_0_100) * (len(arr) - 1) / 100.0)
                    return arr[idx]
                return v_0_100
                
            try:
                if action in ["exposure_ns", "iso"]:
                    requests.get(f"{base_url}/settings/manual_sensor?set=on", timeout=1)
                elif action == "focus_distance":
                    requests.get(f"{base_url}/settings/focusmode?set=off", timeout=1)
                    
                if action == "zoom":
                    requests.get(f"{base_url}/ptz?zoom={val}", timeout=2)
                elif action in ["exposure_ns", "iso", "focus_distance", "night_vision_gain"]:
                    requests.get(f"{base_url}/settings/{action}?set={map_slider(action, val)}", timeout=2)
                elif action == "night_vision_average":
                    requests.get(f"{base_url}/settings/{action}?set={max(1, int(float(val)/10))}", timeout=2)
            except:
                pass
                
        for label_text, min_val, max_val, action in sliders:
            tk.Label(outer, text=label_text, fg="#bdc1c6", bg="#181818", font=("Arial", 10)).pack(anchor="w", padx=4, pady=(8, 0))
            scale = tk.Scale(outer, from_=min_val, to=max_val, orient="horizontal", bg="#181818", fg="#8ab4f8", highlightthickness=0, borderwidth=0)
            scale.pack(fill="x", padx=4)
            scale.bind("<ButtonRelease-1>", lambda e, a=action, s=scale: threading.Thread(target=do_cam_cmd, args=(a, s.get()), daemon=True).start())
"""
content = content.replace(tk_old.strip("\n"), tk_new.strip("\n"))

with open("src/dashboard.py", "w") as f:
    f.write(content)
