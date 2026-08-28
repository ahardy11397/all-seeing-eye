# All-Seeing Eye

Halloween front-window projection. An eye in the round closet window that watches cars and people.

## Hardware

- Android phone with IP Webcam app
- Laptop running Kali Linux
- Mini projector aimed at the window from inside

## Setup

1. On the phone:
   - Install **IP Webcam**
   - Make sure phone and laptop are on the same Wi-Fi
   - Set video resolution to **640x480** or lower in the app settings
   - Start the server
   - Note the exact URL shown in the app; it should end in `/video`
2. On the laptop:
   - Verify the stream is reachable:
     ```bash
     curl -I http://<phone-ip>:8080/video
     ```
   - Clone this repo
   - Create venv and install deps:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
   - Edit `src/config.py` and set `camera_url` to the exact `/video` URL
   - If the stream keeps failing, switch to local webcam testing:
     ```bash
     # in src/config.py
     use_local_camera = True
     local_camera_index = 0
     ```
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
- If camera init fails, the app shows an error and exits instead of crashing
