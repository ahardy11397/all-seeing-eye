with open("src/detector.py", "r") as f:
    content = f.read()

old_logic = """                    if shift < self.parked_drift_px:
                        track.parked_until = now + settings.parked_cooldown_s
                        track.history = [track.history[-1]] # keep last position"""

new_logic = """                    if shift < self.parked_drift_px:
                        track.parked_until = now + settings.parked_cooldown_s
                        track.history = [track.history[-1]] # keep last position
                    else:
                        track.parked_until = 0.0"""

content = content.replace(old_logic, new_logic)

# Let's also increase matching distance from 60 to 100 for better tracking of fast cars
content = content.replace("if dist < 60 and dist < best_dist:", "if dist < 120 and dist < best_dist:")

with open("src/detector.py", "w") as f:
    f.write(content)
