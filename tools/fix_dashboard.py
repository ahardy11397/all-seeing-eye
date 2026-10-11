with open("src/dashboard.py", "r") as f:
    content = f.read()

content = content.replace(
    '        tk.Label(outer, text="Eye animation", fg="#fff", bg="#181818",\n\n        self._slider(',
    '        tk.Label(outer, text="Eye animation", fg="#fff", bg="#181818", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))\n\n        self._slider('
)

with open("src/dashboard.py", "w") as f:
    f.write(content)
