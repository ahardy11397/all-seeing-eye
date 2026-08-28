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


class Dashboard:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("All-Seeing Eye — Prototype Dashboard")
        self.root.configure(bg="#111")

        self.camera = Camera()
        self.detector = Detector()
        self.eye = Eye(settings.width, settings.height)

        self.fps_values = []
        self.detection_label = tk.StringVar(value="No detection")
        self.eye_state = tk.StringVar(value="idle")

        self._build_ui()

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, bg="#111")
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Camera + Tracking", fg="white", bg="#111", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(top, textvariable=self.detection_label, fg="#0f0", bg="#111", font=("Arial", 12)).pack(side=tk.RIGHT)

        self.cam_canvas = tk.Canvas(self.root, width=settings.width, height=settings.height, bg="black", highlightthickness=0)
        self.cam_canvas.pack(padx=10, pady=5)

        bottom = tk.Frame(self.root, bg="#111")
        bottom.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(bottom, text="Simulated Eye", fg="white", bg="#111", font=("Arial", 14, "bold")).pack(anchor="w")
        tk.Label(bottom, textvariable=self.eye_state, fg="#0ff", bg="#111", font=("Arial", 12)).pack(anchor="w")

        self.eye_canvas = tk.Canvas(self.root, width=settings.width, height=settings.height, bg="black", highlightthickness=0)
        self.eye_canvas.pack(padx=10, pady=5)

        self.cam_img_id = self.cam_canvas.create_image(0, 0, anchor="nw", image=None)
        self.eye_img_id = self.eye_canvas.create_image(0, 0, anchor="nw", image=None)

        self.cam_canvas.image = None
        self.eye_canvas.image = None

    def _draw_debug_overlay(self, detection) -> None:
        self.cam_canvas.delete("debug")
        if detection and detection.box:
            x1, y1, x2, y2 = detection.box
            self.cam_canvas.create_rectangle(x1, y1, x2, y2, outline="lime", width=2, tags="debug")
            self.cam_canvas.create_text(x1, y1 - 10, text=detection.label, fill="lime", anchor="sw", tags="debug")
            self.detection_label.set(f"{detection.label} at ({detection.x}, {detection.y})")
        else:
            self.detection_label.set("No detection")
    def run(self) -> int:
        def tick() -> None:
            t0 = time.perf_counter()
            frame = self.camera.read()
            if frame is None:
                self.detection_label.set("Camera frame lost")
                self.root.after(100, tick)
                return

            try:
                detection = self.detector.detect(frame)
            except Exception as exc:
                self.detection_label.set(f"Detection error: {exc}")
                self.root.after(100, tick)
                return

            self._draw_debug_overlay(detection)

            target_x = detection.x if detection else None
            target_y = detection.y if detection else None
            self.eye.update(target_x, target_y, time.time())

            cam_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cam_pil = Image.fromarray(cam_rgb).resize((settings.width, settings.height))
            cam_photo = ImageTk.PhotoImage(cam_pil)
            self.cam_canvas.itemconfig(self.cam_img_id, image=cam_photo)
            self.cam_canvas.image = cam_photo

            eye_pil = self.eye.render()
            eye_photo = ImageTk.PhotoImage(eye_pil)
            self.eye_canvas.itemconfig(self.eye_img_id, image=eye_photo)
            self.eye_canvas.image = eye_photo

            dt = time.perf_counter() - t0
            self.fps_values.append(1.0 / dt if dt > 0 else 0)
            if len(self.fps_values) > 30:
                self.fps_values.pop(0)
            avg_fps = sum(self.fps_values) / len(self.fps_values)
            self.eye_state.set(f"{avg_fps:.1f} FPS | tracking" if detection else f"{avg_fps:.1f} FPS | idle")

            self.root.after(int(1000 / settings.fps), tick)

        self.root.after(200, tick)
        try:
            self.root.mainloop()
        finally:
            self.camera.release()
        return 0


def main() -> int:
    return Dashboard().run()


if __name__ == "__main__":
    raise SystemExit(main())
