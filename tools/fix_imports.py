import re
with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

ds = ds.replace("                import json\n", "")
ds = ds.replace("                import requests\n", "")
ds = ds.replace("import json\n", "import json\nimport requests\n", 1)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
