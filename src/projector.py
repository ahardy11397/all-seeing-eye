from __future__ import annotations

import time

import cv2
import numpy as np
from PIL import Image
try:
    from PIL import ImageTk
except ImportError:
    ImageTk = None

from config import settings
from eye import Eye


def apply_orientation_flips(image: Image.Image) -> Image.Image:
    """Apply horizontal and/or vertical flips according to settings."""
    if getattr(settings, "flip_horizontal", False):
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if getattr(settings, "flip_vertical", False):
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image


class Projector:
    def __init__(self, eye: Eye) -> None:
        self.eye = eye

    def frame(self) -> ImageTk.PhotoImage:
        pil = apply_orientation_flips(self.eye.render())
        return ImageTk.PhotoImage(pil)

    @staticmethod
    def to_tk(frame: np.ndarray) -> ImageTk.PhotoImage:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        return ImageTk.PhotoImage(pil)
