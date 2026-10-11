from PIL import Image
import numpy as np

img = Image.open('skull_human.gif')
guesses = {
    0: [(80, 115)],
    1: [(75, 115), (145, 115)],
    2: [(95, 115), (160, 115)],
    3: [(110, 115), (180, 115)],
    4: [(175, 115)]
}
best = {}

for i in range(5):
    img.seek(i)
    arr = np.array(img.convert('L'))
    best[i] = []
    for x, y in guesses[i]:
        # search window 60x60
        y1, y2 = max(0, y-30), min(arr.shape[0], y+30)
        x1, x2 = max(0, x-30), min(arr.shape[1], x+30)
        
        window = arr[y1:y2, x1:x2]
        my, mx = np.unravel_index(np.argmin(window), window.shape)
        
        true_x, true_y = x1 + mx, y1 + my
        best[i].append((true_x, true_y))
        print(f"Frame {i}: Found dark spot at ({true_x}, {true_y}) with val {window[my, mx]}")
