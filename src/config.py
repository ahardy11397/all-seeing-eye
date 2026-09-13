from __future__ import annotations

from dataclasses import dataclass


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
    blink_interval_s: tuple[float, float] = (8.0, 25.0)
    blink_duration_s: tuple[float, float] = (0.12, 0.25)
    idle_glance_interval_s: tuple[float, float] = (1.2, 3.5)
    idle_glance_duration_s: tuple[float, float] = (1.2, 2.8)
    detection_interval: int = 3
    min_confidence: float = 0.7
    min_box_area: int = 8000
    required_detections: int = 3
    parked_cooldown_s: float = 20.0
    use_local_camera: bool = False
    local_camera_index: int = 0
    # streaming to display device (Mi Box / Android TV browser)
    stream_port: int = 8000
    stream_fps: int = 30
    stream_jpeg_quality: int = 85
    # eye animation
    eye_smoothing: float = 0.18
    idle_mode_time_s: float = 3.5
    # debug
    debug_overlay: bool = True


settings = Settings()
