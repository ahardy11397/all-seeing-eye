import re

with open("src/dashboard.py", "r") as f:
    content = f.read()

# Add a dropdown for eye_type in SettingsPanel
dropdown_ui = """
        tk.Label(outer, text="Eye style", fg="#fff", bg="#181818",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))

        self.eye_type_var = tk.StringVar(value=getattr(settings, "eye_type", "human"))
        
        def on_eye_type_change(*args):
            setattr(settings, "eye_type", self.eye_type_var.get())
            
        self.eye_type_var.trace_add("write", on_eye_type_change)
        
        dropdown = tk.OptionMenu(outer, self.eye_type_var, "human", "monster")
        dropdown.config(bg="#181818", fg="#ccc", highlightthickness=0)
        dropdown["menu"].config(bg="#181818", fg="#ccc")
        dropdown.pack(anchor="w", pady=3)

        tk.Label(outer, text="Eye animation", fg="#fff", bg="#181818",
"""

content = content.replace(
    '        tk.Label(outer, text="Eye animation", fg="#fff", bg="#181818",\n                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))',
    dropdown_ui.strip("\n")
)

# Update _reset
reset_func = """
    def _reset(self) -> None:
        defaults = type(settings)()
        for field in ("min_confidence", "min_box_area", "required_detections",
                      "detection_interval", "parked_cooldown_s", "smoothing"):
            setattr(settings, field, getattr(defaults, field))
        setattr(settings, "eye_type", "human")
        self.detector.parked_drift_px = 8
        self.destroy()
        SettingsPanel(self.master, self.detector)
"""

content = re.sub(
    r'    def _reset\(self\) -> None:.*?SettingsPanel\(self\.master, self\.detector\)',
    reset_func.strip(),
    content,
    flags=re.DOTALL
)

with open("src/dashboard.py", "w") as f:
    f.write(content)

print("Patched dashboard.py")
