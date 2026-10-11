from __future__ import annotations

import time

import cv2
import numpy as np
from PIL import Image, ImageTk

from config import settings
from eye import Eye


class Projector:
    def __init__(self, eye: Eye) -> None:
        self.eye = eye

    def frame(self) -> ImageTk.PhotoImage:
        pil = self.eye.render()
        return ImageTk.PhotoImage(pil)

    @staticmethod
    def to_tk(frame: np.ndarray) -> ImageTk.PhotoImage:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        return ImageTk.PhotoImage(pil)
