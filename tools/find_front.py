from PIL import Image
import numpy as np

img = Image.open("skull.gif")
symmetries = []

for i in range(img.n_frames):
    img.seek(i)
    arr = np.array(img.convert("L"))
    flipped = np.fliplr(arr)
    
    # Calculate absolute difference between the image and its flipped version
    diff = np.sum(np.abs(arr.astype(float) - flipped.astype(float)))
    symmetries.append(diff)

front = np.argmin(symmetries)
back = np.argmax(symmetries) # roughly side profile
print(f"Most symmetric frame (front or back): {front}")
# We might have two minimums (front and back of head).
# Let's find local minimums.
from scipy.signal import find_peaks
# invert symmetries to find peaks
inv_sym = max(symmetries) - np.array(symmetries)
peaks, _ = find_peaks(inv_sym, distance=30)
print("Symmetric peaks at frames:", peaks)
