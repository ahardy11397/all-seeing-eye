import cv2
import numpy as np
import trimesh
import pyrender
from PIL import Image

# 1. Load image and create depth map
img = Image.open('skull.jpg').convert('RGB')
img = img.resize((300, 300))
arr = np.array(img)
h, w = arr.shape[:2]

yy, xx = np.mgrid[0:h, 0:w]

# Depth map (0 = flat background, higher = closer to camera)
# We want the background to be at depth 0, and the skull to protrude.
# The image has a black background. We can use the image intensity or a mask.
gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
mask = (gray > 10).astype(np.float32)

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

# Mask the depth map so the background stays flat
depth = depth * mask
# Add a base thickness to the skull
depth = depth + (mask * 0.2)

# Scale depth to actual 3D coordinates (Z axis)
# X, Y are 0 to w, 0 to h. Let Z be up to 100
Z = depth * 150.0

# 2. Create mesh using trimesh
# Create vertices: (x, y, z)
# In trimesh, y is often up, but let's just map x,y to x,y
vertices = np.zeros((h * w, 3), dtype=np.float32)
vertices[:, 0] = xx.flatten()
vertices[:, 1] = yy.flatten()
vertices[:, 2] = Z.flatten()

# Create faces (triangulate the grid)
# i = y * w + x
y_idx = np.arange(h - 1).reshape(-1, 1)
x_idx = np.arange(w - 1).reshape(1, -1)
idx = y_idx * w + x_idx

faces1 = np.stack([idx, idx + 1, idx + w], axis=-1).reshape(-1, 3)
faces2 = np.stack([idx + 1, idx + w + 1, idx + w], axis=-1).reshape(-1, 3)
faces = np.vstack([faces1, faces2])

# UVs
uvs = np.zeros((h * w, 2), dtype=np.float32)
uvs[:, 0] = xx.flatten() / float(w)
uvs[:, 1] = 1.0 - (yy.flatten() / float(h)) # image coords to UV (flip Y)

# Create material and mesh
material = trimesh.visual.material.SimpleMaterial(image=img)
visuals = trimesh.visual.TextureVisuals(uv=uvs, image=img)
mesh = trimesh.Trimesh(vertices=vertices, faces=faces, visual=visuals, process=False)

# 3. Render using pyrender
scene = pyrender.Scene(ambient_light=[1.0, 1.0, 1.0])
mesh_node = pyrender.Mesh.from_trimesh(mesh, smooth=False)
scene.add(mesh_node)

# Center the camera
center = np.array([w/2.0, h/2.0, 0])
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
cam_pose = np.eye(4)
cam_pose[0, 3] = w/2.0
cam_pose[1, 3] = h/2.0
cam_pose[2, 3] = 400.0 # move back
scene.add(camera, pose=cam_pose)

# Light
light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
scene.add(light, pose=cam_pose)

r = pyrender.OffscreenRenderer(w, h)
color, depth = r.render(scene)
Image.fromarray(color).save("rendered_3d.jpg")
print("Saved rendered_3d.jpg")
