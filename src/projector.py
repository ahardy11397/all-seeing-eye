from __future__ import annotations

from PIL import Image, ImageTk

from .config import settings
from .eye import Eye


class Projector:
    def __init__(self, eye: Eye) -> None:
        self.eye = eye

    def frame(self) -> ImageTk.PhotoImage:
        pil = self.eye.render()
        return ImageTk.PhotoImage(pil)
