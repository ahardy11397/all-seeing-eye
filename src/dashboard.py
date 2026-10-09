from __future__ import annotations

import time
import tkinter as tk

import cv2
from PIL import Image, ImageTk

from camera import Camera
from config import settings
from detector import Detector
from eye import Eye
from monster_eye import MonsterEye
from zombie_eye import ZombieEye
from dragon_eye import DragonEye
from snake_eye import SnakeEye
from spider_eye import SpiderEye
from bug_eye import BugEye
from creepy_figure import CreepyFigure
from joker_eye import JokerEye
from skull import Skull
from dancing_skeleton import DancingSkeleton
from uga_logo import UgaLogo


class SettingsPanel(tk.Toplevel):
    """Live-tunable detection + eye settings. Sliders write straight into
    `settings`, so changes take effect on the next frame."""

    def __init__(self, master, detector: Detector) -> None:
        super().__init__(master)
        self.title("Detection & Eye Settings")
        self.configure(bg="#181818")
        self.resizable(False, False)
        self.detector = detector

        outer = tk.Frame(self, bg="#181818", padx=14, pady=10)
        outer.pack(fill=tk.BOTH, expand=True)

        tk.Label(outer, text="Detection sensitivity", fg="#fff", bg="#181818",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))

        # lower confidence = more sensitive (more detections, more false positives)
        self._slider(outer, "Confidence threshold (lower = more sensitive)",
                     0.10, 0.95, settings.min_confidence, 0.01,
                     lambda v: (setattr(settings, "min_confidence", float(v)), settings.save()))

        # lower min area = smaller objects tracked
        self._slider(outer, "Min object size (px², lower = smaller objects)",
                     500, 40000, settings.min_box_area, 200,
                     lambda v: (setattr(settings, "min_box_area", int(float(v))), settings.save()))

        # lower required = faster lock-on, more jitter
        self._slider(outer, "Frames to confirm detection",
                     1, 10, settings.required_detections, 1,
                     lambda v: (setattr(settings, "required_detections", int(float(v))), settings.save()))

        # detection every N frames — 1 = most responsive, most CPU
        self._slider(outer, "Run detection every N frames",
                     1, 10, settings.detection_interval, 1,
                     lambda v: (setattr(settings, "detection_interval", int(float(v))), settings.save()))

        tk.Label(outer, text="Parked-vehicle rejection", fg="#fff", bg="#181818",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))

        self._slider(outer, "Parked cooldown (s)",
                     5.0, 60.0, settings.parked_cooldown_s, 1.0,
                     lambda v: (setattr(settings, "parked_cooldown_s", float(v)), settings.save()))

        self._slider(outer, "Max drift to count as parked (px)",
                     2, 40, getattr(settings, "parked_drift_px", 25), 1,
                     lambda v: (setattr(settings, "parked_drift_px", int(float(v))), settings.save()))

        tk.Label(outer, text="Eye style", fg="#fff", bg="#181818",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))

        self.eye_type_var = tk.StringVar(value=getattr(settings, "eye_type", "human"))
        
        def on_eye_type_change(*args):
            setattr(settings, "eye_type", self.eye_type_var.get())
            
        self.eye_type_var.trace_add("write", on_eye_type_change)
        
        dropdown = tk.OptionMenu(outer, self.eye_type_var, "human", "monster", "zombie", "dragon", "snake", "spider", "bug", "creepy_figure")
        dropdown.config(bg="#181818", fg="#ccc", highlightthickness=0)
        dropdown["menu"].config(bg="#181818", fg="#ccc")
        dropdown.pack(anchor="w", pady=3)

        tk.Label(outer, text="Eye animation", fg="#fff", bg="#181818", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))

        self._slider(outer, "Eye smoothing (higher = snappier)",
                     0.05, 0.6, settings.smoothing, 0.01,
                     lambda v: (setattr(settings, "smoothing", float(v)), settings.save()))

        btns = tk.Frame(outer, bg="#181818")
        btns.pack(fill=tk.X, pady=(12, 0))
        tk.Button(btns, text="Reset to defaults", command=self._reset).pack(side=tk.LEFT)

    def _slider(self, parent, label, from_, to, current, resolution, command):
        row = tk.Frame(parent, bg="#181818")
        row.pack(fill=tk.X, pady=3)
        val_var = tk.StringVar(value=self._fmt(current))

        def on_move(v):
            command(v)
            val_var.set(self._fmt(float(v)))

        tk.Label(row, text=label, fg="#ccc", bg="#181818", font=("Arial", 10)).pack(anchor="w")
        srow = tk.Frame(row, bg="#181818")
        srow.pack(fill=tk.X)
        tk.Scale(srow, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL,
                 command=on_move, length=260, bg="#181818", fg="#ccc",
                 highlightthickness=0, showvalue=False).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(srow, textvariable=val_var, fg="#0f0", bg="#181818",
                 font=("Arial", 10), width=8, anchor="e").pack(side=tk.RIGHT)

    @staticmethod
    def _fmt(v: float) -> str:
        return f"{v:.2f}" if isinstance(v, float) and v < 10 else f"{int(round(v))}"

def _reset(self) -> None:
        defaults = type(settings)()
        for field in ("min_confidence", "min_box_area", "required_detections",
                      "detection_interval", "parked_cooldown_s", "smoothing"):
            setattr(settings, field, getattr(defaults, field))
        setattr(settings, "eye_type", "human")
        settings.parked_drift_px = 25
        settings.save()
        self.destroy()
        SettingsPanel(self.master, self.detector)


class Dashboard:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("All-Seeing Eye — Prototype Dashboard")
        self.root.configure(bg="#111")

        self.camera = Camera()
        self.detector = Detector()
        self.settings_panel: SettingsPanel | None = None

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

        tk.Label(bottom, text="Simulated Eye", fg="white", bg="#111", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(bottom, textvariable=self.eye_state, fg="#0ff", bg="#111", font=("Arial", 12)).pack(side=tk.RIGHT)
        tk.Button(bottom, text="⚙ Settings", command=self._toggle_settings,
                  bg="#222", fg="white", activebackground="#333",
                  relief=tk.FLAT, padx=10).pack(side=tk.RIGHT, padx=(0, 12))

        self.eye_canvas = tk.Canvas(self.root, width=settings.width, height=settings.height, bg="black", highlightthickness=0)
        self.eye_canvas.pack(padx=10, pady=5)

        self.cam_img_id = self.cam_canvas.create_image(0, 0, anchor="nw", image=None)
        self.eye_img_id = self.eye_canvas.create_image(0, 0, anchor="nw", image=None)

        self.cam_canvas.image = None
        self.eye_canvas.image = None

    def _toggle_settings(self) -> None:
        if self.settings_panel is not None and self.settings_panel.winfo_exists():
            self.settings_panel.destroy()
            self.settings_panel = None
        else:
            self.settings_panel = SettingsPanel(self.root, self.detector)

    def _draw_debug_overlay(self, detection) -> None:
        self.cam_canvas.delete("debug")
        if detection and detection.box:
            x1, y1, x2, y2 = detection.box
            self.cam_canvas.create_rectangle(x1, y1, x2, y2, outline="lime", width=2, tags="debug")
            self.cam_canvas.create_text(x1, y1 - 10, text=detection.label, fill="lime", anchor="sw", tags="debug")
            parked = ""
            if self.detector._vehicle_parked_until > time.time():
                parked = " [parked]"
            self.detection_label.set(f"{detection.label} ({detection.x}, {detection.y}){parked}")
        else:
            if self.detector._vehicle_parked_until > time.time():
                self.detection_label.set("Parked vehicle ignored")
            else:
                self.detection_label.set("No detection")

    def run(self) -> int:
        def tick() -> None:
            current_eye_type = getattr(settings, "eye_type", "human")
            if type(self.eye).__name__.lower().replace("eye", "").replace("creepyfigure", "creepy_figure").replace("ugalogo", "uga_logo").replace("dancingskeleton", "dancing_skeleton") != current_eye_type and not (current_eye_type == "human" and type(self.eye).__name__ == "Eye"):

                if current_eye_type == "monster": self.eye = MonsterEye(settings.width, settings.height)

                elif current_eye_type == "zombie": self.eye = ZombieEye(settings.width, settings.height)

                elif current_eye_type == "dragon": self.eye = DragonEye(settings.width, settings.height)

                elif current_eye_type == "snake": self.eye = SnakeEye(settings.width, settings.height)

                elif current_eye_type == "spider": self.eye = SpiderEye(settings.width, settings.height)

                elif current_eye_type == "bug": self.eye = BugEye(settings.width, settings.height)

                elif current_eye_type == "creepy_figure": self.eye = CreepyFigure(settings.width, settings.height)

                elif current_eye_type == "joker": self.eye = JokerEye(settings.width, settings.height)


                elif current_eye_type == "skull": self.eye = Skull(settings.width, settings.height)


                elif current_eye_type == "dancing_skeleton": self.eye = DancingSkeleton(settings.width, settings.height)

                elif current_eye_type == "uga_logo": self.eye = UgaLogo(settings.width, settings.height)

                else: self.eye = Eye(settings.width, settings.height)

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
