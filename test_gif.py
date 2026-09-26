from PIL import Image
import numpy as np

img = Image.open("skull.gif")
frames = []
for i in range(img.n_frames):
    img.seek(i)
    # convert to RGB
    rgb = img.convert("RGB")
    # find bounding box to see if it's solid black background
    frames.append(rgb)

print(f"Loaded {len(frames)} frames.")
