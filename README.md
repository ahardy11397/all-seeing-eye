# All-Seeing Eye

A Halloween projection project: a projected eye in the round front-closet window that watches and follows cars/people as they pass.

## Requirements

- Python 3.10+
- Camera pointed outward
- Projector aimed at the window from inside
- Motion/object detection to track subjects
- Eye renderer that pans/tracks movement

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Project structure

```text
src/
  main.py            # entrypoint
  eye.py             # eye geometry, iris, pupil, blinking
  tracker.py         # camera capture + motion/object detection
  projector.py       # render + project / window preview
  config.py          # tunables
data/
  textures/          # optional iris/sclera assets
```
