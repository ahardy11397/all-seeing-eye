with open("src/camera.py", "r") as f:
    cam = f.read()

import re

old_loop = """    def _reader_loop(self) -> None:
        while not self._stop.is_set():
            ok, frame = self.cap.read()"""

new_loop = """    def _reader_loop(self) -> None:
        try:
            while not self._stop.is_set():
                ok, frame = self.cap.read()"""

cam = cam.replace(old_loop, new_loop)

old_loop_end = """            # small yield so the grab loop keeps the buffer drained
            time.sleep(0.001)"""

new_loop_end = """            # small yield so the grab loop keeps the buffer drained
            time.sleep(0.001)
        # Safely release here in the same thread to prevent segfaults
        self.cap.release()
        except Exception as e:
            print(f"Camera thread exiting: {e}")
            try:
                self.cap.release()
            except:
                pass"""

cam = cam.replace(old_loop_end, new_loop_end)

old_release = """    def release(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2.0)
        self.cap.release()"""

new_release = """    def release(self) -> None:
        self._stop.set()
        # Don't join or call cap.release() here, as cap.read() might be blocked
        # in the other thread, and calling release concurrently causes a Segfault!"""

cam = cam.replace(old_release, new_release)

with open("src/camera.py", "w") as f:
    f.write(cam)
