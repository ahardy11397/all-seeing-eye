import re
with open("src/eye.py", "r") as f:
    eye = f.read()

old_block = """    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        if target_x is not None and target_y is not None:
            tx = max(0, min(self.width, target_x))
            ty = max(0, min(self.height, target_y))
            self.idle_mode = "idle"
            self.idle_glance_started_at = None
            self.idle_next_switch = now + random.uniform(2.0, 5.0)
        else:
            tx, ty = self._idle_target(now)"""

new_block = """    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        if target_x is not None and target_y is not None:
            # Add organic microsaccades so the eye doesn't look dead when locked on
            if not hasattr(self, "_saccade_target"):
                self._saccade_target = (0, 0)
                self._next_saccade = now
            
            if now > self._next_saccade:
                import random
                # Dart within a 15px radius to "examine" the target
                self._saccade_target = (random.randint(-15, 15), random.randint(-15, 15))
                self._next_saccade = now + random.uniform(0.3, 1.8)
                
            tx = max(0, min(self.width, target_x + self._saccade_target[0]))
            ty = max(0, min(self.height, target_y + self._saccade_target[1]))
            self.idle_mode = "idle"
            self.idle_glance_started_at = None
            self.idle_next_switch = now + random.uniform(2.0, 5.0)
        else:
            tx, ty = self._idle_target(now)"""

eye = eye.replace(old_block, new_block)

with open("src/eye.py", "w") as f:
    f.write(eye)
