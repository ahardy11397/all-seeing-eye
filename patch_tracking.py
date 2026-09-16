with open("run_stream.py", "r") as f:
    text = f.read()

old_block = """            if frame is not None:
                try:
                    detection = detector.detect(frame)
                except Exception as exc:
                    print(f"detection error: {exc}", file=sys.stderr)
                    detection = None"""

new_block = """            if frame is not None:
                if getattr(settings, "tracking_enabled", True):
                    try:
                        detection = detector.detect(frame)
                    except Exception as exc:
                        print(f"detection error: {exc}", file=sys.stderr)
                        detection = None
                else:
                    detection = None
                    detector._last_detection = None  # Clear history so it doesn't get stuck"""

text = text.replace(old_block, new_block)
with open("run_stream.py", "w") as f:
    f.write(text)
