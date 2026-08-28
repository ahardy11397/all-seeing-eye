# All-Seeing Eye

Halloween front-window projection. An eye in the round closet window that watches cars and people.

## Hardware

- Android phone with IP Webcam app
- Laptop running Kali Linux
- Mini projector aimed at the window from inside

## Setup

1. On the phone:
   - Install IP Webcam
   - Start server, note the IP/port shown (default `http://<phone-ip>:8080/video`)
2. On the laptop:
   - Clone this repo
   - Create venv and install deps:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
   - Edit `src/config.py` and set `camera_url` to your phone's stream URL
   - Connect projector, set it as primary display if needed
3. Run dashboard:
   ```bash
   ./run_dashboard.py
   ```
4. Run fullscreen projection:
   ```bash
   ./run.py
   ```

## Notes

- First run downloads `yolov8n.pt` automatically (~6 MB)
- Detection runs every 3rd frame by default to keep CPU usage down
- When nothing is detected, the eye does idle glances/scan instead of staring at center
