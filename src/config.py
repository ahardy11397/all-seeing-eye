from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    camera_url: str = "http://192.168.1.166:8080/video"
    width: int = 640
    height: int = 480
    fps: int = 30
    eye_radius: int = 160
    iris_radius: int = 70
    pupil_radius: int = 28
    max_pupil_offset: int = 45
    smoothing: float = 0.25
    blink_interval_s: tuple[float, float] = (2.5, 7.0)
    blink_duration_s: tuple[float, float] = (0.08, 0.18)
    idle_glance_interval_s: tuple[float, float] = (1.5, 4.0)
    idle_glance_duration_s: tuple[float, float] = (0.8, 2.0)
    detection_interval: int = 3
    use_local_camera: bool = False
    local_camera_index: int = 0


settings = Settings()
