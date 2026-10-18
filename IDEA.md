# All-Seeing Eye — Concept & Vision

A real-time Halloween projection-mapping and motion-tracking installation designed to turn a round closet window on the front of the house into an uncanny, reactive animated entity that tracks cars and pedestrians passing by.

---

## 1. Original Core Concept

- **The Illusion**: An animated, living eye projected onto the round window on the front facade of the house.
- **The Interaction**: A camera aimed outside tracks passing pedestrians and vehicles in real time. The projected eye tracks and follows them as they walk or drive by, making the house appear alive and watching.
- **Perspective Mirroring**: Gaze angles are mirrored so that from the street perspective, the eye looks directly at the observer.
- **Window Masking**: Strict circular crop and absolute black background to avoid light bleed beyond the round window frame.

---

## 2. Current Achievements (What Has Been Built)

### Computer Vision & Low-Latency Pipeline
- **Zero-Latency Video Stream Capture**: Custom background thread continuously pulls and drops stale demux buffer frames from network IP Webcam (Android) streams or local USB webcams.
- **YOLOv8 Real-Time Detection**: Tracks persons and vehicles passing in front of the house.
- **Parked Vehicle Rejection**: Drift-displacement tracking marks stationary parked cars on the street as `[parked]` and ignores them during a cooldown period to avoid permanent stare-locks.
- **Detection Confirmation & Motion Smoothing**: Consecutive-frame thresholding filters out false positives; lerp-based smoothing ensures lifelike, fluid gaze tracking without jitter.

### Procedural & Multimodal Creature Engine
- **Procedural Human Eye**:
  - Spherical sclera 3D shading, dynamic shifting blood vessels, upper eyelid drop shadow, corneal specular highlights, and pupil dilation.
  - Involuntary micro-blinking and autonomous idle animations (random saccades and smooth scanning sweeps) when no targets are detected.
- **12 Switchable Creature Modes**:
  - Human (Default procedural)
  - Monster, Zombie, Dragon, Snake, Spider, Bug
  - Creepy Figure
  - Joker (Heath Ledger face & makeup tracking)
  - 3D Skull (multi-angle depth mapping)
  - Dancing Skeleton
  - UGA Logo (University of Georgia bulldog branding)

### Wireless Display & Network Architecture
- **Mi Box / Android TV Wireless Display Server (`:8000`)**:
  - Snapshot-polling viewer (`/`) engineered for Android TV WebViews to eliminate freeze-ups.
  - Fullscreen black border auto-centering for round window projection mapping.
  - Multipart MJPEG endpoint (`/stream`) for external displays.
- **Real-Time Web Dashboard (`:8090`)**:
  - Side-by-side live preview of the projected eye and annotated camera feed.
  - Yellow gaze crosshair visualizing eye look direction across the full camera FOV.
  - Hot-tunable settings (confidence, minimum size, smoothing, blinking, tracking toggle, eye style selection) saved instantly to `settings.json`.
  - Camera control sliders (zoom, focus, exposure, gain, night vision) communicating directly with IP Webcam.
- **Projection Orientation Control**:
  - Software `flip_horizontal` (for rear projection onto window film) and `flip_vertical` (for upside-down ceiling projector mounting).

---

## 3. Future Roadmap & Expansion Ideas

### Audio & Sound FX Reactivity
- **Directional Sound Effects**: Connect outdoor Bluetooth/weatherproof speakers to play squelching eye movements, fleshy blinking, low ambient hums, or heavy breathing synchronized with gaze.
- **Jumpscare Audio Triggers**: Trigger dramatic audio cues (deep growl, sudden screech, or whisper) when a pedestrian stops on the sidewalk or approaches the porch.
- **Voice Lines / Character Dialogue**: Play custom soundbites matching the selected eye type (e.g. Joker laughter, dragon snarl, zombie groans).

### Smart Home & Physical Automation (Home Assistant / MQTT)
- **Porch Light Dimming / Color Synchronization**: Dim or turn porch smart lights blood-red (via Philips Hue / Home Assistant MQTT) when an approaching target is detected.
- **Fog Machine Automation**: Trigger a smart plug or DMX relay connected to a fog machine when people walk into the detection zone.
- **Animatronics Triggering**: Send MQTT signals to activate motorized props or window shutters when trick-or-treaters approach.

### Advanced Tracking & Behavioral AI
- **Dual-Eye / Binocular Mode**: Support projecting two coordinated eyes (or rendering a stereoscopic pair) for wider windows or multiple projector setups.
- **Threat Escalation State Machine**:
  1. *Idle*: Lazy looking around and occasional blinks.
  2. *Curious*: Smoothly follows a passing pedestrian or car across the street.
  3. *Agitated*: If a person stops and stares, iris widens, veins pulse red, and eye narrows.
  4. *Rage / Jumpscare*: Sudden pupil dilation, twitching, bloodshot sclera flash if someone steps onto the driveway.
- **Pedestrian vs. Car Behavioral Distinction**: Differentiate between fast-moving cars (smooth glance across) and walking trick-or-treaters (laser-focused lock-on with closer engagement).

### Hardware & Edge Deployment
- **Edge AI Deployment**: Port the pipeline to an edge accelerator (Coral Edge TPU, Jetson Orin Nano, or Raspberry Pi 5 with Hailo-8) for a standalone, fanless appliance that mounts directly behind the projector.
- **Physical Camera Pan/Tilt Servos**: Control a physical motorized camera or mirror galvanometer to extend the field of view beyond a single static lens.
