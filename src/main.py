from __future__ import annotations

import time

import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

from camera import Camera
from config import settings
from detector import Detector
from eye import Eye
from projector import Projector


def main() -> int:
    root = tk.Tk()
    root.title("All-Seeing Eye")
    root.configure(bg="black")
    if settings.fullscreen:
        root.attributes("-fullscreen", True)

    width = settings.width
    height = settings.height
    eye = Eye(width, height)
    camera = Camera()
    detector = Detector()
    projector = Projector(eye)

    canvas = tk.Canvas(root, width=width, height=height, bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    img_id = canvas.create_image(0, 0, anchor="nw", image=None)
    label = tk.Label(canvas, text="Initializing camera...", fg="white", bg="black")
    canvas.create_window(width // 2, height // 2, window=label)

    fps_values = []

    def tick() -> None:
        t0 = time.perf_counter()
        try:
            frame = camera.read()
        except RuntimeError as exc:
            label.configure(text=str(exc))
            root.after(100, tick)
            return

        if frame is None:
            label.configure(text="No camera frame")
            root.after(100, tick)
            return

        try:
            detection = detector.detect(frame)
        except Exception as exc:
            label.configure(text=f"Detection error: {exc}")
            root.after(100, tick)
            return

        target_x = detection.x if detection else None
        target_y = detection.y if detection else None

        eye.update(target_x, target_y, time.time())
        photo = projector.frame()
        canvas.itemconfig(img_id, image=photo)
        label.configure(text="")

        if settings.debug_overlay and detection and detection.box:
            x1, y1, x2, y2 = detection.box
            canvas.create_rectangle(x1, y1, x2, y2, outline="lime", width=2)
            canvas.create_text(x1, y1 - 10, text=detection.label, fill="lime", anchor="sw")

        dt = time.perf_counter() - t0
        fps_values.append(1.0 / dt if dt > 0 else 0)
        if len(fps_values) > 30:
            fps_values.pop(0)
        avg_fps = sum(fps_values) / len(fps_values)

        root.title(f"All-Seeing Eye — {avg_fps:.1f} FPS")

        if settings.fullscreen:
            root.after(int(1000 / settings.fps), tick)
        else:
            root.after(1, tick)

    root.after(200, tick)
    try:
        root.mainloop()
    finally:
        camera.release()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
