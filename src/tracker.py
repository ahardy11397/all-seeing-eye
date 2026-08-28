from __future__ import annotations

import time

import cv2
import numpy as np

from .config import settings


class Tracker:
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(settings.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
        self.prev_gray: np.ndarray | None = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=False
        )

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None, None
        return frame, self._target_for_frame(frame)

    def _target_for_frame(self, frame: np.ndarray):
        fg = self.bg_subtractor.apply(frame)
        _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        fg = cv2.dilate(fg, np.ones((5, 5), np.uint8), iterations=1)
        contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) < 400:
            return None

        m = cv2.moments(contour)
        if m["m00"] == 0:
            return None
        cx = int(m["m10"] / m["m00"])
        cy = int(m["m01"] / m["m00"])
        return cx, cy

    def release(self) -> None:
        self.cap.release()
        cv2.destroyAllWindows()
