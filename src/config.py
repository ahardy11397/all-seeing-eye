from __future__ import annotations

from dataclasses import dataclass, asdict, fields
import json
import os

@dataclass
class Settings:
    camera_url: str = "http://192.168.1.166:8080/video"
    width: int = 640
    height: int = 480
    fps: int = 30
    eye_radius: int = 160
    iris_radius: int = 70
    pupil_radius: int = 28
    max_pupil_offset: int = 45
    smoothing: float = 0.18
    blink_enabled: bool = False
    blink_interval_s: tuple[float, float] = (2.0, 8.0)
    blink_duration_s: tuple[float, float] = (0.12, 0.25)
    tracking_enabled: bool = True
    idle_glance_interval_s: tuple[float, float] = (1.2, 3.5)
    idle_glance_duration_s: tuple[float, float] = (1.2, 2.8)
    
    detection_interval: int = 3
    min_confidence: float = 0.5
    min_box_area: int = 1500
    required_detections: int = 3
    parked_cooldown_s: float = 20.0
    parked_drift_px: int = 25
    use_local_camera: bool = False
    local_camera_index: int = 0
    
    stream_port: int = 8000
    stream_fps: int = 30
    stream_jpeg_quality: int = 85
    dashboard_port: int = 8090
    
    eye_type: str = "human"
    
    # Camera controls (0-100 sliders)
    cam_zoom: int = 0
    cam_focus_distance: int = 0
    cam_exposure: int = 50
    cam_gain: int = 50
    cam_night_vision_exposure: int = 50
    cam_night_vision_gain: int = 50
    cam_night: bool = False

    idle_mode_time_s: float = 3.5
    fullscreen: bool = True
    debug_overlay: bool = True

    def load(self, path="settings.json"):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                for fld in fields(self):
                    if fld.name in data:
                        setattr(self, fld.name, data[fld.name])
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save(self, path="settings.json"):
        try:
            with open(path, "w") as f:
                json.dump(asdict(self), f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

settings = Settings()
settings.load()
