import cv2
import numpy as np
from PIL import Image

img = Image.open('skull.jpg').convert('RGB')
img = img.resize((500, 500))
arr = np.array(img)
h, w = arr.shape[:2]

gx = 1.0 # full right
gy = 0.5 # slightly down

shrink_r = max(0, gx * h * 0.15)
shrink_l = max(0, -gx * h * 0.15)

shrink_b = max(0, gy * w * 0.15)
shrink_t = max(0, -gy * w * 0.15)

tx = gx * w * 0.15
ty = gy * h * 0.15

tl = [0 + tx + shrink_t, 0 + ty + shrink_l]
tr = [w + tx - shrink_t, 0 + ty + shrink_r]
br = [w + tx - shrink_b, h + ty - shrink_r]
bl = [0 + tx + shrink_b, h + ty - shrink_l]

src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
dst_pts = np.float32([tl, tr, br, bl])

M = cv2.getPerspectiveTransform(src_pts, dst_pts)
warped = cv2.warpPerspective(arr, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

Image.fromarray(warped).save('warped_skull.jpg')
print("Saved warped_skull.jpg")
