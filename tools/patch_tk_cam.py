with open("src/dashboard.py", "r") as f:
    content = f.read()

tk_old = """
        tk.Checkbutton(outer, text="Enable random blinking", variable=self.blink_var, 
                       bg="#181818", fg="#bdc1c6", selectcolor="#202124", 
                       activebackground="#181818", activeforeground="#fff").pack(anchor="w", padx=4, pady=4)
"""
tk_new = tk_old + """
        # Camera controls
        tk.Label(outer, text="Camera Controls", fg="#fff", bg="#181818",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 4))
        
        btn_frame = tk.Frame(outer, bg="#181818")
        btn_frame.pack(fill="x", padx=4, pady=4)
        
        import threading
        import requests
        self.torch_state = False
        
        def cam_req(path):
            base_url = settings.camera_url.rsplit("/", 1)[0]
            def do_req():
                try:
                    requests.get(f"{base_url}{path}", timeout=2)
                except:
                    pass
            threading.Thread(target=do_req, daemon=True).start()
            
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

content = content.replace(tk_old.strip("\n"), tk_new.strip("\n"))

with open("src/dashboard.py", "w") as f:
    f.write(content)

