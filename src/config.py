from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    camera_index: int = 0
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
    preview: bool = True
    fullscreen: bool = False


settings = Settings()
