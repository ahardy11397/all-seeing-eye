from __future__ import annotations

import io
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import cv2
from PIL import Image

from camera import Camera
from config import settings
from detector import Detector
from eye import Eye
from stream_server import broadcaster, make_server


def main() -> int:
    camera = Camera()
    detector = Detector()
    eye = Eye(settings.width, settings.height)

    server = make_server(broadcaster, settings.stream_port)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"Eye stream: http://0.0.0.0:{settings.stream_port}/  (open this on the Mi Box browser)")

    frame_interval = 1.0 / max(1, settings.stream_fps)
    quality = settings.stream_jpeg_quality

    try:
        while True:
            t0 = time.perf_counter()
            frame = camera.read()
            if frame is None:
                time.sleep(0.1)
                continue

            try:
                detection = detector.detect(frame)
            except Exception as exc:
                print(f"detection error: {exc}", file=sys.stderr)
                detection = None

            target_x = detection.x if detection else None
            target_y = detection.y if detection else None
            eye.update(target_x, target_y, time.time())
            pil = eye.render()

            buf = io.BytesIO()
            pil.convert("RGB").save(buf, format="JPEG", quality=quality)
            broadcaster.publish(buf.getvalue())

            # keep pace with target fps
            elapsed = time.perf_counter() - t0
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
