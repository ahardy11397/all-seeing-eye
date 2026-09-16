import re
with open("src/dashboard.py", "r") as f:
    content = f.read()

tk_old = """
        def on_focus(): cam_req("/focus")
        def on_torch():
            self.torch_state = not self.torch_state
            cam_req("/enabletorch" if self.torch_state else "/disabletorch")
            
        tk.Button(btn_frame, text="Autofocus", command=on_focus, bg="#5f6368", fg="#fff", borderwidth=0, padx=8, pady=4).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Toggle Flash", command=on_torch, bg="#5f6368", fg="#fff", borderwidth=0, padx=8, pady=4).pack(side="left")
        
        tk.Label(outer, text="Zoom", fg="#bdc1c6", bg="#181818", font=("Arial", 10)).pack(anchor="w", padx=4, pady=(8, 0))
        zoom_scale = tk.Scale(outer, from_=0, to=100, orient="horizontal", bg="#181818", fg="#8ab4f8", highlightthickness=0, borderwidth=0)
        zoom_scale.pack(fill="x", padx=4)
        
        def on_zoom(val):
            cam_req(f"/ptz?zoom={val}")
        zoom_scale.bind("<ButtonRelease-1>", lambda e: on_zoom(zoom_scale.get()))
"""

tk_new = """
        def on_focus(): cam_req("/focus")
        def on_torch():
            self.torch_state = not getattr(self, "torch_state", False)
            cam_req("/enabletorch" if self.torch_state else "/disabletorch")
        def on_night():
            self.night_state = not getattr(self, "night_state", False)
            cam_req("/settings/night_vision?set=" + ("on" if self.night_state else "off"))
            
        tk.Button(btn_frame, text="Autofocus", command=on_focus, bg="#5f6368", fg="#fff", borderwidth=0, padx=6, pady=4).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Toggle Flash", command=on_torch, bg="#5f6368", fg="#fff", borderwidth=0, padx=6, pady=4).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Toggle Night Mode", command=on_night, bg="#5f6368", fg="#fff", borderwidth=0, padx=6, pady=4).pack(side="left")
        
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
content = content.replace(tk_old.strip("\n"), tk_new.strip("\n"))

with open("src/dashboard.py", "w") as f:
    f.write(content)

