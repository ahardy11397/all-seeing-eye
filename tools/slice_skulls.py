from PIL import Image

img = Image.open('/home/ahard/.gemini/antigravity/brain/7bfb6392-131a-41ec-8421-4dc421292dba/skull_spritesheet_1790368653872.jpg')
w, h = img.size

# The image is 1024x1024. The 4 skulls are horizontally aligned.
# Let's crop into 4 equal vertical slices.
slice_w = w // 4

frames = []
for i in range(4):
    crop = img.crop((i * slice_w, 0, (i + 1) * slice_w, h))
    # crop out the extra vertical black space to make it square again
    # The skulls are centered.
    crop_h = slice_w
    offset_y = (h - crop_h) // 2
    crop = crop.crop((0, offset_y, slice_w, offset_y + crop_h))
    frames.append(crop)

# Frame 0: Left profile
# Frame 1: Slight left
# Frame 2: Straight
# Frame 3: Slight right

# Generate 5 frames (-1 to +1):
f0 = frames[0]
f1 = frames[1]
f2 = frames[2]
f3 = frames[3]
f4 = frames[0].transpose(Image.FLIP_LEFT_RIGHT)

frames_out = [f0, f1, f2, f3, f4]
frames_out[0].save('skull_human.gif', save_all=True, append_images=frames_out[1:], duration=200, loop=0)
print("Saved skull_human.gif")
