import re
with open("run_stream.py", "r") as f:
    rs = f.read()

# Reorder main() to start servers first, and handle camera creation safely
old_main = """def main() -> int:
    camera = Camera()
    detector = Detector()
    eye = Eye(settings.width, settings.height)

    # public stream for the Mi Box
    stream_srv = make_server(broadcaster, settings.stream_port)
    threading.Thread(target=stream_srv.serve_forever, daemon=True).start()

    # local dashboard with previews + settings
    dash_srv = make_dashboard_server(store, settings.dashboard_port, detector)
    threading.Thread(target=dash_srv.serve_forever, daemon=True).start()"""

new_main = """def main() -> int:
    detector = Detector()
    eye = Eye(settings.width, settings.height)

    # public stream for the Mi Box
    stream_srv = make_server(broadcaster, settings.stream_port)
    threading.Thread(target=stream_srv.serve_forever, daemon=True).start()

    # local dashboard with previews + settings
    dash_srv = make_dashboard_server(store, settings.dashboard_port, detector)
    threading.Thread(target=dash_srv.serve_forever, daemon=True).start()
    
    # Try to initialize camera, but don't crash if it's temporarily offline
    try:
        camera = Camera()
    except Exception as e:
        print(f"Warning: Failed to connect to camera on startup: {e}")
        camera = None"""

rs = rs.replace(old_main, new_main)

# We also need to handle `camera` being None in the while True loop!
old_loop = """            t0 = time.perf_counter()
            frame = camera.read()
            if frame is None:
                time.sleep(0.1)
                continue"""

new_loop = """            t0 = time.perf_counter()
            if camera is None:
                # Retry connection every 5 seconds
                import time
                time.sleep(5)
                try:
                    camera = Camera()
                except:
                    pass
                continue
                
            frame = camera.read()
            if frame is None:
                time.sleep(0.1)
                continue"""
rs = rs.replace(old_loop, new_loop)

with open("run_stream.py", "w") as f:
    f.write(rs)
