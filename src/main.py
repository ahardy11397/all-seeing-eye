from __future__ import annotations

import time
import tkinter as tk

import cv2
import numpy as np
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

    def tick() -> None:
        frame = camera.read()
        if frame is None:
            label.configure(text="No camera frame")
            root.after(100, tick)
            return

        detection = detector.detect(frame)
        target_x = detection.x if detection else None
        target_y = detection.y if detection else None

        eye.update(target_x, target_y, time.time())
        photo = projector.frame()
        canvas.itemconfig(img_id, image=photo)

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
