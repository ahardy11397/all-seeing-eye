from PIL import Image, ImageDraw

img = Image.open('skull_human.gif')

sockets = {
    0: [(80, 120)],
    1: [(75, 120), (145, 120)],
    2: [(95, 120), (160, 120)],
    3: [(110, 120), (180, 120)],
    4: [(175, 120)]
}

frames = []
for i in range(5):
    img.seek(i)
    rgb = img.convert('RGB')
    draw = ImageDraw.Draw(rgb)
    for x, y in sockets[i]:
        draw.ellipse([x-5, y-5, x+5, y+5], fill=(255,0,0))
    frames.append(rgb)

frames[0].save('sockets_debug.gif', save_all=True, append_images=frames[1:], duration=500, loop=0)
print("Saved sockets_debug.gif")
