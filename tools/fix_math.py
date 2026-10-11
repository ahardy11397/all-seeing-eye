with open("src/dashboard_server.py", "r") as f:
    ds = f.read()

ds = ds.replace("                import math\n", "")
ds = ds.replace("import json\n", "import json\nimport math\n", 1)

with open("src/dashboard_server.py", "w") as f:
    f.write(ds)
