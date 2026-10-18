import re
with open("run_stream.py", "r") as f:
    rs = f.read()

old_read = """            frame = camera.read()
            if frame is None:
                time.sleep(0.1)
                continue"""

new_read = """            try:
                frame = camera.read()
            except RuntimeError as e:
                print(f"Camera dropped: {e}. Reconnecting...")
                camera.release()
                camera = None
                continue
                
            if frame is None:
                time.sleep(0.1)
                continue"""

rs = rs.replace(old_read, new_read)

with open("run_stream.py", "w") as f:
    f.write(rs)
