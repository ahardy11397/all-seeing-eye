with open("src/dashboard.py", "r") as f:
    content = f.read()

# Add to tk UI
tk_old = """
        self.eye_type_var = tk.StringVar(value=getattr(settings, "eye_type", "human"))
        
        def on_eye_type_change(*args):
            setattr(settings, "eye_type", self.eye_type_var.get())
            
        self.eye_type_var.trace_add("write", on_eye_type_change)
        
        dropdown = tk.OptionMenu(outer, self.eye_type_var, "human", "monster", "zombie", "dragon")
        dropdown.config(bg="#202124", fg="#e8eaed", activebackground="#303134", activeforeground="#fff", highlightthickness=0, borderwidth=1)
        dropdown["menu"].config(bg="#202124", fg="#e8eaed")
        dropdown.pack(fill="x", padx=4, pady=4)
"""
tk_new = tk_old + """
        self.blink_var = tk.BooleanVar(value=getattr(settings, "blink_enabled", False))
        def on_blink_change(*args):
            setattr(settings, "blink_enabled", self.blink_var.get())
        self.blink_var.trace_add("write", on_blink_change)
        
        tk.Checkbutton(outer, text="Enable random blinking", variable=self.blink_var, 
                       bg="#181818", fg="#bdc1c6", selectcolor="#202124", 
                       activebackground="#181818", activeforeground="#fff").pack(anchor="w", padx=4, pady=4)
"""

content = content.replace(tk_old.strip("\n"), tk_new.strip("\n"))

with open("src/dashboard.py", "w") as f:
    f.write(content)
