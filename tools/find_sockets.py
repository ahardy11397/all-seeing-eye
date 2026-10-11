from PIL import Image
import numpy as np
import cv2

img = Image.open('skull_human.gif')

for i in range(img.n_frames):
    img.seek(i)
    arr = np.array(img.convert('L'))
    
    # We want to find the two darkest regions in the face
    # The eyes are roughly in the middle vertically, and distributed horizontally
    h, w = arr.shape
    roi = arr[int(h*0.3):int(h*0.6), :]
    
    # Threshold to find dark spots (sockets)
    _, thresh = cv2.threshold(roi, 30, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    centers = []
    for c in contours:
        # filter by size
        if cv2.contourArea(c) > 20:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"]) + int(h*0.3)
                centers.append((cx, cy))
    
    centers = sorted(centers, key=lambda x: x[0])
    # if it's profile (like frame 0 or 4), we might only see 1 eye socket or it might be merged
    print(f"Frame {i}: Sockets {centers}")
