with open("src/detector.py", "r") as f:
    content = f.read()

content = content.replace("track.history.clear() # clear to avoid re-triggering constantly while parked", "track.history = [track.history[-1]] # keep last position")

with open("src/detector.py", "w") as f:
    f.write(content)
