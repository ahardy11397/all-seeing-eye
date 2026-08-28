from __future__ import annotations

import time

import cv2

from config import settings


class Camera:
    def __init__(self) -> None:
        self.is_local = settings.use_local_camera
        if self.is_local:
            self.cap = cv2.VideoCapture(settings.local_camera_index)
            if not self.cap.isOpened():
                raise RuntimeError("Cannot open local camera")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
        else:
            self.cap = cv2.VideoCapture(settings.camera_url, cv2.CAP_FFMPEG)
            if not self.cap.isOpened():
                raise RuntimeError(f"Cannot open camera stream: {settings.camera_url}")
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def release(self) -> None:
        self.cap.release()
