import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
frame = np.zeros((480, 640, 3), dtype=np.uint8)
results = model.track(frame, persist=True, classes=[0, 2, 5, 7], verbose=False)
if results:
    boxes = results[0].boxes
    if boxes is not None:
        print("has boxes")
        print(hasattr(boxes, "id"))
