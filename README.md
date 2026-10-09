# All-Seeing Eye

A real-time Halloween window projection mapping project. An animated eye projected into a round window that tracks passing pedestrians and cars using computer vision.

```
                  +-------------------------+
                  |  Phone (IP Webcam App)  |
                  |     points out window   |
                  +------------+------------+
                               | (Wi-Fi /video stream)
                               v
                  +-------------------------+
                  |      Kali Laptop        |
                  |  - Low-latency reader   |
                  |  - YOLOv8 object detector|
                  |  - Procedural eye engine|
                  |  - Stream & Web servers |
                  +---+-----------------+---+
                      |                 |
  (HTTP :8000)        |                 | (HTTP :8090)
                      v                 v
          +-----------------------+  +--------------------+
          |  Mi Box / Android TV  |  |   Web Dashboard    |
          |  + Projector on window|  |   (live preview &  |
          +-----------------------+  |   instant tuning)  |
                                     +--------------------+
```

---

## Hardware

- **Camera**: Android phone running the free [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) app, aimed outside through the window.
- **Server**: Laptop running Linux (Kali, Ubuntu, etc.) with Python 3.10+. An NVIDIA GPU (e.g. GTX 1660) accelerates YOLO detection, but CPU execution is also supported.
- **Display**:
  - **Wireless / Network (Recommended)**: Android TV / Xiaomi Mi Box / Fire TV connected to the projector via HDMI. The TV's browser displays the eye stream over Wi-Fi—no long HDMI runs needed.
  - **Direct (Alternative)**: Projector plugged directly into the laptop via HDMI.
- **Projection Surface**: Round window, frosted window film, rear-projection fabric, or shower curtain liner.

---

## Quick Start

### 1. Phone Camera Setup
1. Install **IP Webcam** on your Android phone.
2. Connect phone and laptop to the same Wi-Fi network.
3. In IP Webcam settings:
   - Set **Video resolution** to `640x480` (or `800x600` max; lower resolutions reduce latency).
   - Optionally enable **Quality** at ~50-70% for smooth transmission.
4. Tap **Start server** at the bottom of the app.
5. Note the URL displayed on the phone screen (e.g., `http://192.168.1.166:8080/video`).
6. Test connectivity from the laptop:
   ```bash
   curl -I http://<phone-ip>:8080/video
   ```

### 2. Laptop Setup
1. Clone the repository and navigate into the folder:
   ```bash
   cd /mnt/ssd/projects/all-seeing-eye
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(On first run, YOLOv8 will automatically download `yolov8n.pt` ~6 MB).*

4. Configure settings:
   Copy `settings.example.json` to `settings.json` and adjust your phone's camera URL and settings:
   ```bash
   cp settings.example.json settings.json
   ```
   Or edit `src/config.py`:
   ```python
   camera_url: str = "http://<phone-ip>:8080/video"
   ```
   *(To test with a local USB webcam instead, set `use_local_camera = True` and `local_camera_index = 0`)*.

---

## Running the System

### Recommended: Stream Server + Web Dashboard

Run the unified background service:
```bash
./run_stream.py
```

This launches two simultaneous HTTP services:

#### 1. Eye Display Stream (`http://<laptop-ip>:8000/`)
Open this URL in the browser on your **Mi Box / Android TV** connected to your projector:
- **`/` (or `/index.html`)**: Snapshot-polling web viewer optimized specifically for Android TV WebViews (which frequently freeze or drop raw multipart MJPEG streams). Includes auto-centering and black background.
- **`/stream`**: Standard multipart MJPEG stream for browsers or media players (VLC, ffplay).
- **`/snapshot`**: Returns the latest rendered eye frame as JPEG.

Press **F11** or fullscreen in your TV browser to fill the projection window.

#### 2. Web Tuning Dashboard (`http://<laptop-ip>:8090/`)
Open this in your laptop or phone browser to monitor tracking and tune settings in real time:
- **Live Eye Preview**: Real-time rendering of what the projector is displaying.
- **Camera + Tracking View**: Live camera feed showing detected bounding boxes, object class labels (`person` or `vehicle`), confidence scores, parked indicator, and a **warm yellow gaze crosshair** showing exactly where the eye is aiming across the full camera field of view.
- **Live Controls (apply instantly without restart)**:
  - **Min confidence**: Detection confidence threshold (lower = more sensitive, higher = fewer false positives).
  - **Min object size (px²)**: Ignore small background noise and distant targets.
  - **Frames to confirm**: Require N consecutive detection frames before locking gaze.
  - **Detect every N frames**: Run YOLO every N frames (higher = lower CPU/GPU usage; 3 is recommended).
  - **Parked cooldown (s)**: How long to ignore a stationary vehicle after it stops moving.
  - **Parked drift (px)**: Maximum allowable movement before a vehicle is classified as parked.
  - **Eye smoothing**: Speed/damping of eye movement toward targets.
  - **Eye type selection**: Human, monster, zombie, dragon, snake, spider, bug, creepy figure, joker, 3D skull, dancing skeleton, UGA logo.
  - **Reset to defaults**: Restore baseline settings with one click.

---

### Alternative Standalone Modes

- **Local Fullscreen Window (`./run.py`)**:
  Opens a direct Tkinter canvas on the laptop display. Use this if your projector is plugged directly into the laptop via HDMI.
- **Desktop Tkinter Dashboard (`./run_dashboard.py`)**:
  Runs a desktop GUI with side-by-side camera/eye feeds and a slider settings popup.

---

## Key Features

- **Zero-Lag Camera Reader**: OpenCV's default FFmpeg capture buffers several seconds of network video when decoding MJPEG streams. The built-in `Camera` worker thread continuously pulls and discards stale buffer frames in the background using zero-delay demux flags, ensuring the eye tracks real-time motion with minimal latency.
- **Perspective-Correct Gaze Mirroring**: Eye horizontal deflection is inverted so that from the perspective of an outside observer looking in through the window, the eye looks toward the target as they walk or drive past.
- **Smart Parked Vehicle Rejection**: When cars park on the street in front of the house, standard object detectors lock on indefinitely. The detector tracks center displacement across consecutive frames—if a vehicle remains stationary within the drift threshold, it is automatically marked as `[parked]` and ignored during the cooldown period.
- **Procedural Eyeball Engine**:
  - Photorealistic sclera with spherical shading, upper eyelid drop shadow, and glossy wet highlight.
  - Blood vessel capillaries that dynamically shift and rotate with gaze angle.
  - Natural involuntary micro-blinks and pupil dilation changes.
  - Autonomous idle animations (random saccades and smooth scanning sweeps) when no targets are detected.
  - Strict circular crop with solid black background outside the eyeball radius to avoid projecting light bleed outside round windows.

---

## Configuration Reference (`src/config.py` & `settings.json`)

| Setting | Default | Description |
| :--- | :--- | :--- |
| `camera_url` | `http://192.168.1.166:8080/video` | IP Webcam stream endpoint |
| `use_local_camera` | `False` | Set `True` to use local USB webcam |
| `local_camera_index` | `0` | V4L2 device index for local webcam |
| `width`, `height` | `640`, `480` | Render and capture canvas resolution |
| `stream_host` | `0.0.0.0` | Bind host for projector display stream (`127.0.0.1` for local-only) |
| `stream_port` | `8000` | Port for the projector display web stream |
| `stream_fps` | `30` | Target frame rate for network streaming |
| `stream_jpeg_quality` | `85` | JPEG compression quality for stream |
| `dashboard_host` | `0.0.0.0` | Bind host for dashboard server (`127.0.0.1` for local-only) |
| `dashboard_port` | `8090` | Port for the web monitoring dashboard |
| `dashboard_auth_token` | `""` | Optional Bearer / `X-Auth-Token` to protect dashboard endpoints |
| `detection_interval` | `3` | Run YOLO inference every N frames |
| `min_confidence` | `0.5` | Minimum detection confidence threshold |
| `min_box_area` | `1500` | Minimum bounding box area in pixels² |
| `required_detections` | `3` | Consecutive frames needed to confirm target |
| `parked_cooldown_s` | `20.0` | Cooldown period before re-checking parked car |
| `smoothing` | `0.18` | Motion lerp factor (higher = faster, lower = smoother) |
| `eye_type` | `human` | Active eye mode (`monster`, `zombie`, `dragon`, `snake`, `skull`, etc.) |
| `eye_radius` | `160` | Eyeball radius in canvas pixels |
| `iris_radius` | `70` | Iris radius in canvas pixels |
| `pupil_radius` | `28` | Resting pupil radius in canvas pixels |
| `max_pupil_offset` | `45` | Maximum travel distance of iris from center |

---

## Troubleshooting

- **Laggy video / delayed eye tracking**:
  - Ensure the IP Webcam app video resolution is set to `640x480`. High resolutions (1080p+) add network buffering and increase inference time.
  - Ensure the laptop is running on a 5GHz Wi-Fi band or ethernet.
- **Android TV / Mi Box stream freezes**:
  - Use `http://<laptop-ip>:8000/` which uses snapshot polling (`/snapshot`), rather than `/stream`. Android TV WebViews often choke on continuous multipart MJPEG streams.
- **Eye stares at a parked car**:
  - Open the web dashboard at `http://<laptop-ip>:8090/`.
  - Check the `Camera + tracking` card to see if the car is marked `[parked]`.
  - If it does not enter parked mode, slightly increase **Parked drift (px)** or decrease **Parked cooldown (s)**.
- **Eye moves too abruptly or jitters**:
  - Lower the **Eye smoothing** slider on the dashboard (e.g., to `0.10` - `0.15`).
  - Increase **Frames to confirm** to `4` or `5`.

