import cv2
import numpy as np
from PIL import Image

img = Image.open('skull.jpg').convert('RGB')
img = img.resize((300, 300))
arr = np.array(img)
h, w = arr.shape[:2]

yy, xx = np.mgrid[0:h, 0:w]

nx, ny = w*0.5, h*0.55
nose_dist = np.sqrt((xx-nx)**2 + (yy-ny)**2)
depth = np.clip(1.0 - nose_dist/(w*0.3), 0, 1)

cx, cy = w*0.5, h*0.45
cranium_dist = np.sqrt((xx-cx)**2 + (yy-cy)**2)
depth_cranium = np.clip(0.7 - cranium_dist/(w*0.45), 0, 1)
depth = np.maximum(depth, depth_cranium)

lx, ly = w*0.35, h*0.45
rx, ry = w*0.65, h*0.45
l_dist = np.sqrt((xx-lx)**2*0.6 + (yy-ly)**2)
r_dist = np.sqrt((xx-rx)**2*0.6 + (yy-ry)**2)
eye_depth = np.clip(1.0 - np.minimum(l_dist, r_dist)/(w*0.2), 0, 1)

depth = depth - eye_depth * 0.5
depth = np.clip(depth, 0, 1)

depth = cv2.GaussianBlur(depth, (15, 15), 0)

gx = 1.0 # looking right
gy = 0.0

shift_x = 40
shift_y = 40

# create displacement map
dx = (depth * gx * shift_x).astype(np.float32)
dy = (depth * gy * shift_y).astype(np.float32)

map_x = (xx.astype(np.float32) - dx)
map_y = (yy.astype(np.float32) - dy)

warped = cv2.remap(arr, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

Image.fromarray(warped).save('warped_parallax.jpg')
Image.fromarray((depth*255).astype(np.uint8)).save('depth.jpg')
print("Saved warped_parallax.jpg")
