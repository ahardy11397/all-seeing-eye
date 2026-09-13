from __future__ import annotations

import threading
import time

import cv2

from config import settings


class Camera:
    """Camera reader with latest-frame semantics.

    A background thread continuously grabs frames from the stream. `read()`
    returns the most recent one and discards older ones. Without this, the
    FFmpeg capture buffers several seconds of MJPEG frames and every consumer
    (detection, overlays) lags behind real time by that backlog.
    """

    def __init__(self) -> None:
        self.is_local = settings.use_local_camera
        self._fail_count = 0
        self._max_fails = 40

        if self.is_local:
            self.cap = cv2.VideoCapture(settings.local_camera_index)
            if not self.cap.isOpened():
                raise RuntimeError("Cannot open local camera")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
        else:
            # FFMPEG flags: no buffered input, no B-frames, low-latency demux
            import os
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtmp_buffer;0|fflags;nobuffer|flags;low_delay|max_delay;0"
            )
            self.cap = cv2.VideoCapture(settings.camera_url, cv2.CAP_FFMPEG)
            if not self.cap.isOpened():
                raise RuntimeError(f"Cannot open camera stream: {settings.camera_url}")
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._lock = threading.Lock()
        self._frame = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def _reader_loop(self) -> None:
        while not self._stop.is_set():
            ok, frame = self.cap.read()
            if not ok or frame is None or frame.size == 0:
                self._fail_count += 1
                if self._fail_count >= self._max_fails:
                    # surface failure; main loop will raise on repeated reads
                    with self._lock:
                        self._frame = None
                    time.sleep(0.05)
                    continue
                time.sleep(0.01)
                continue
            self._fail_count = 0
            with self._lock:
                self._frame = frame  # keep only the newest frame
            # small yield so the grab loop keeps the buffer drained
            time.sleep(0.001)

    def read(self):
        with self._lock:
            frame = self._frame
            self._frame = None  # consume: next read waits for a fresher frame
        if frame is None:
            self._fail_count += 1
            if self._fail_count >= self._max_fails * 4:
                raise RuntimeError(
                    f"Camera stream stalled: no fresh frames from {settings.camera_url}"
                )
            return None
        self._fail_count = 0
        return frame

    def release(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2.0)
        self.cap.release()
