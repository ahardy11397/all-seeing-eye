with open("src/camera.py", "r") as f:
    content = f.read()

import re

old_block = r"    def _reader_loop\(self\) -> None:.*?    def read\(self\):"
match = re.search(old_block, content, flags=re.DOTALL)
if match:
    new_loop = """    def _reader_loop(self) -> None:
        try:
            while not self._stop.is_set():
                ok, frame = self.cap.read()
                if not ok or frame is None or frame.size == 0:
                    self._fail_count += 1
                    if self._fail_count >= self._max_fails:
                        with self._lock:
                            self._frame = None
                        time.sleep(0.05)
                        continue
                    time.sleep(0.01)
                    continue
                self._fail_count = 0
                with self._lock:
                    self._frame = frame
                time.sleep(0.001)
            self.cap.release()
        except Exception as e:
            print(f"Camera thread exiting: {e}")
            try:
                self.cap.release()
            except:
                pass

    def read(self):"""
    content = content.replace(match.group(0), new_loop)
    with open("src/camera.py", "w") as f:
        f.write(content)
