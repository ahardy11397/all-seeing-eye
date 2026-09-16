with open("run_stream.py", "r") as f:
    rs = f.read()

rs = rs.replace("        camera.release()\n", "        if camera is not None:\n            camera.release()\n")

with open("run_stream.py", "w") as f:
    f.write(rs)
