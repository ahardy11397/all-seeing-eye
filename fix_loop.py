with open("run_stream.py", "r") as f:
    rs = f.read()

import re

# Find everything from "while True:" down to "fps_values.append..."
match = re.search(r'(        while True:.*?)(            fps_values\.append)', rs, flags=re.DOTALL)
if match:
    old_block = match.group(1)
    
    new_block = """        last_cam_retry = 0.0
        while True:
            current_eye_type = getattr(settings, "eye_type", "human")
            if (current_eye_type == "human" and type(eye).__name__ != "Eye") or \
               (current_eye_type == "monster" and type(eye).__name__ != "MonsterEye") or \
               (current_eye_type == "zombie" and type(eye).__name__ != "ZombieEye") or \
               (current_eye_type == "dragon" and type(eye).__name__ != "DragonEye"):
                if current_eye_type == "monster":
                    eye = MonsterEye(settings.width, settings.height)
                elif current_eye_type == "zombie":
                    eye = ZombieEye(settings.width, settings.height)
                elif current_eye_type == "dragon":
                    eye = DragonEye(settings.width, settings.height)
                else:
                    eye = Eye(settings.width, settings.height)

            t0 = time.perf_counter()
            frame = None
            
            if camera is None:
                if time.time() - last_cam_retry > 5.0:
                    try:
                        camera = Camera()
                    except:
                        pass
                    last_cam_retry = time.time()
            else:
                try:
                    frame = camera.read()
                except RuntimeError as e:
                    print(f"Camera dropped: {e}. Reconnecting...", file=sys.stderr)
                    camera.release()
                    camera = None
            
            if frame is not None:
                try:
                    detection = detector.detect(frame)
                except Exception as exc:
                    print(f"detection error: {exc}", file=sys.stderr)
                    detection = None
                parked = getattr(detector, "_vehicle_parked_until", 0) > time.time()
                target_x = detection.x if detection else None
                target_y = detection.y if detection else None
            else:
                detection = None
                parked = False
                target_x = None
                target_y = None

            eye.update(target_x, target_y, time.time())
            eye_pil = eye.render()

            # public stream: plain eye, black background
            broadcaster.publish(_jpeg(eye_pil, quality))

            # dashboard: eye preview + annotated camera
            if frame is not None:
                cam_vis = _annotate_camera(frame, detection, eye, parked)
                cam_pil = Image.fromarray(cv2.cvtColor(cam_vis, cv2.COLOR_BGR2RGB))
            else:
                import numpy as np
                cam_vis = np.zeros((settings.height, settings.width, 3), dtype=np.uint8)
                cv2.putText(cam_vis, "NO SIGNAL", (settings.width//2 - 90, settings.height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                cam_pil = Image.fromarray(cam_vis)
                
            cam_pil = cam_pil.resize((settings.width, settings.height))

"""
    
    rs = rs.replace(old_block, new_block)
    
    with open("run_stream.py", "w") as f:
        f.write(rs)
