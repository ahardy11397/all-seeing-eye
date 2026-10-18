with open("run_stream.py", "r") as f:
    rs = f.read()

import re

mgr = """class CameraManager:
    def __init__(self):
        self.camera = None
        self.connecting = False
        self.last_attempt = 0.0

    def get_frame(self):
        if self.camera is not None:
            try:
                return self.camera.read()
            except RuntimeError as e:
                import sys
                print(f"Camera dropped: {e}. Reconnecting...", file=sys.stderr)
                try:
                    self.camera.release()
                except:
                    pass
                self.camera = None
                return None
        else:
            import time
            if not self.connecting and time.time() - self.last_attempt > 5.0:
                self.connecting = True
                self.last_attempt = time.time()
                import threading
                threading.Thread(target=self._connect, daemon=True).start()
            return None

    def _connect(self):
        try:
            self.camera = Camera()
        except:
            pass
        finally:
            self.connecting = False

"""

# Insert mgr before main()
rs = rs.replace("def main() -> int:", mgr + "def main() -> int:")

# Replace the camera retry block
match = re.search(r'(            if camera is None:.*?)(            if frame is not None:)', rs, flags=re.DOTALL)
if match:
    old_block = match.group(1)
    new_block = """            frame = cam_mgr.get_frame()
            
"""
    rs = rs.replace(old_block, new_block)
    
    # replace `last_cam_retry = 0.0`
    rs = rs.replace("        last_cam_retry = 0.0\n", "        cam_mgr = CameraManager()\n")

with open("run_stream.py", "w") as f:
    f.write(rs)
