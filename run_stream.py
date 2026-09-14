from __future__ import annotations

import io
import math
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
from monster_eye import MonsterEye
from dashboard_server import make_dashboard_server, store
from stream_server import broadcaster, make_server


def _jpeg(pil: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    pil.convert("RGB").save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def _annotate_camera(frame, detection, eye, parked: bool):
    """Camera frame with tracking box, label, and a crosshair where the eye looks."""
    import numpy as np

    vis = frame.copy()
    h, w = vis.shape[:2]

    if detection and detection.box:
        x1, y1, x2, y2 = detection.box
        color = (60, 220, 60)  # lime BGR
        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
        label = detection.label
        if parked:
            label += " [parked]"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        ty = max(th + 6, y1 - 6)
        cv2.rectangle(vis, (x1, ty - th - 6), (x1 + tw + 6, ty), color, -1)
        cv2.putText(vis, label, (x1 + 3, ty - 4), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (0, 0, 0), 1, cv2.LINE_AA)

    # crosshair: gaze DIRECTION mapped across the full frame. The iris's
    # physical travel is small (max_pupil_offset px), but full deflection in a
    # direction means the eye is looking all the way that way — so normalize
    # the gaze vector and map -1..1 onto the full camera view.
    gx, gy = eye.gaze()
    look_x = int((gx * 0.5 + 0.5) * (w - 1))
    look_y = int((gy * 0.5 + 0.5) * (h - 1))

    color = (60, 200, 255)  # warm yellow BGR
    gap = 10
    length = 18
    cv2.line(vis, (look_x - gap - length, look_y), (look_x - gap, look_y), color, 2)
    cv2.line(vis, (look_x + gap, look_y), (look_x + gap + length, look_y), color, 2)
    cv2.line(vis, (look_x, look_y - gap - length), (look_x, look_y - gap), color, 2)
    cv2.line(vis, (look_x, look_y + gap), (look_x, look_y + gap + length), color, 2)
    cv2.circle(vis, (look_x, look_y), 2, color, -1, cv2.LINE_AA)
    return vis


def main() -> int:
    camera = Camera()
    detector = Detector()
    eye = Eye(settings.width, settings.height)

    # public stream for the Mi Box
    stream_srv = make_server(broadcaster, settings.stream_port)
    threading.Thread(target=stream_srv.serve_forever, daemon=True).start()

    # local dashboard with previews + settings
    dash_srv = make_dashboard_server(store, settings.dashboard_port, detector)
    threading.Thread(target=dash_srv.serve_forever, daemon=True).start()

    host_note = f"http://0.0.0.0:{settings.dashboard_port}/"
    print(f"Dashboard: {host_note}   (open on this machine)")
    print(f"Eye stream: http://0.0.0.0:{settings.stream_port}/  (open on the Mi Box)")

    frame_interval = 1.0 / max(1, settings.stream_fps)
    quality = settings.stream_jpeg_quality
    fps_values: list[float] = []

    try:
        while True:
            current_eye_type = getattr(settings, "eye_type", "human")
            if (current_eye_type == "human" and type(eye).__name__ != "Eye") or                (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye"):
                if current_eye_type == "monster":
                    eye = MonsterEye(settings.width, settings.height)
                else:
                    eye = Eye(settings.width, settings.height)

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

            parked = detector._vehicle_parked_until > time.time()

            target_x = detection.x if detection else None
            target_y = detection.y if detection else None
            eye.update(target_x, target_y, time.time())
            eye_pil = eye.render()

            # public stream: plain eye, black background
            broadcaster.publish(_jpeg(eye_pil, quality))

            # dashboard: eye preview + annotated camera
            cam_vis = _annotate_camera(frame, detection, eye, parked)
            cam_pil = Image.fromarray(cv2.cvtColor(cam_vis, cv2.COLOR_BGR2RGB))
            cam_pil = cam_pil.resize((settings.width, settings.height))

            fps_values.append(1.0 / (time.perf_counter() - t0) if time.perf_counter() - t0 > 0 else 0)
            if len(fps_values) > 30:
                fps_values.pop(0)

            store.publish(
                _jpeg(eye_pil, 80),
                _jpeg(cam_pil, 80),
                {
                    "fps": sum(fps_values) / len(fps_values),
                    "detection": (
                        {"label": detection.label, "x": detection.x, "y": detection.y,
                         "box": list(detection.box),
                         "conf": round(float(detection.conf), 2)}
                        if detection else None
                    ),
                    "parked": parked,
                    "iris": {"x": eye.iris_x, "y": eye.iris_y},
                },
            )

            elapsed = time.perf_counter() - t0
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        stream_srv.shutdown()
        dash_srv.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
