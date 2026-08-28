from __future__ import annotations

import time
import tkinter as tk
from importlib.util import find_spec

import cv2
import numpy as np
from PIL import Image, ImageTk

from config import Settings, settings
from eye import Eye
from projector import Projector
from tracker import Tracker


def main() -> int:
    root = tk.Tk()
    root.title("All-Seeing Eye")
    root.configure(bg="black")

    width = settings.width
    height = settings.height
    eye = Eye(width, height)
    tracker = Tracker()
    projector = Projector(eye)

    canvas = tk.Canvas(root, width=width, height=height, bg="black", highlightthickness=0)
    canvas.pack()

    img_id = canvas.create_image(0, 0, anchor="nw", image=None)
    label = tk.Label(canvas, text="Initializing camera...", fg="white", bg="black")
    canvas.create_window(width // 2, height // 2, window=label)

    def tick() -> None:
        frame, target = tracker.read()
        if frame is None:
            label.configure(text="No camera frame")
            root.after(100, tick)
            return

        eye.update(target[0] if target else None, target[1] if target else None, time.time())
        photo = projector.frame()
        canvas.itemconfig(img_id, image=photo)
        root.after(int(1000 / settings.fps), tick)

    root.after(200, tick)
    try:
        root.mainloop()
    finally:
        tracker.release()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
