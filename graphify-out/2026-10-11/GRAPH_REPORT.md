# Graph Report - all-seeing-eye  (2026-10-11)

## Corpus Check
- 134 files · ~67,671 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .pt 1)

## Summary
- 434 nodes · 791 edges · 53 communities (15 shown, 38 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 115 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `667840c0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_stream.py
- main
- All-Seeing Eye Project
- DragonEye
- JokerEye
- MonsterEye
- SnakeEye
- ZombieEye
- json
- Skull
- Eye
- UgaLogo
- DashboardHandler
- main
- make_dashboard_server
- SettingsPanel
- test_js.js
- BugEye
- Dashboard
- SpiderEye
- CreepyFigure
- DancingSkeleton
- Tracker
- ._build_static_layers
- create_joker.py
- patch_dispatch.py
- test_index.py
- patch_file
- fix_tk_syntax2.py
- all-seeing-eye
- Q: Why does main() connect Camera Streaming & Video Ingestion to 15 different rendering models, dispatch stores, and display communities?
- Q: How does Smart Parked Vehicle Rejection work in Detector and filter out stationary cars?

## God Nodes (most connected - your core abstractions)
1. `main()` - 26 edges
2. `Eye` - 25 edges
3. `Dashboard` - 21 edges
4. `Detector` - 17 edges
5. `main()` - 17 edges
6. `tick()` - 14 edges
7. `DragonEye` - 14 edges
8. `JokerEye` - 14 edges
9. `tick()` - 14 edges
10. `MonsterEye` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Perspective-Correct Gaze Mirroring` --implements--> `Eye`  [INFERRED]
  README.md → src/eye.py
- `Zero-Lag Camera Reader` --implements--> `Camera`  [INFERRED]
  README.md → src/camera.py
- `Web Tuning Dashboard (:8090)` --implements--> `make_dashboard_server()`  [INFERRED]
  README.md → src/dashboard_server.py
- `Smart Parked Vehicle Rejection` --implements--> `Detector`  [INFERRED]
  README.md → src/detector.py
- `Procedural Eyeball Engine` --implements--> `Eye`  [INFERRED]
  README.md → src/eye.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Computer Vision and Rendering Dependencies** — requirements_numpy, requirements_opencv_python, requirements_pillow, requirements_ultralytics [EXTRACTED 1.00]
- **Eye Tracking Optimization and Stabilization Mechanisms** — readme_zero_lag_camera_reader, readme_perspective_gaze_mirroring, readme_smart_parked_vehicle_rejection, readme_android_tv_snapshot_polling [INFERRED 0.85]
- **Human Skull Anatomical Structures and Rendering** — skull_human_visualization, skull_human_eye_sockets, skull_human_cranium, skull_human_rotational_frames [INFERRED 0.85]
- **Real-Time Tracking and Projection Pipeline** — readme_phone_ip_webcam, readme_zero_lag_camera_reader, readme_yolov8_object_detector, readme_procedural_eyeball_engine, readme_eye_display_stream_server [INFERRED 0.95]

## Communities (53 total, 38 thin omitted)

### Community 2 - "main"
Cohesion: 0.10
Nodes (9): YOLOv8 Object Detector, ultralytics, _annotate_camera(), CameraManager, main(), Camera, Detection, Detector (+1 more)

### Community 3 - "All-Seeing Eye Project"
Cohesion: 0.07
Nodes (16): Halloween Window Projection Tracking, All-Seeing Eye Project, Configuration & Settings System, Eye Display Stream Server (:8000), Eye Type Variations, Phone IP Webcam Stream, Procedural Eyeball Engine, Round Window Projection Mapping (+8 more)

### Community 5 - "DragonEye"
Cohesion: 0.19
Nodes (3): DragonEye, catmull_rom(), draw_vessel()

### Community 6 - "JokerEye"
Cohesion: 0.19
Nodes (3): JokerEye, catmull_rom(), draw_vessel()

### Community 7 - "MonsterEye"
Cohesion: 0.19
Nodes (3): MonsterEye, catmull_rom(), draw_vessel()

### Community 8 - "SnakeEye"
Cohesion: 0.19
Nodes (3): SnakeEye, catmull_rom(), draw_vessel()

### Community 9 - "ZombieEye"
Cohesion: 0.19
Nodes (3): ZombieEye, catmull_rom(), draw_vessel()

### Community 10 - "json"
Cohesion: 0.29
Nodes (3): post(), get(), post()

### Community 11 - "Skull"
Cohesion: 0.21
Nodes (6): Human Cranium and Sutures, Skull Eye Sockets and Orbit Anatomy, Mandible and Maxilla Dentition, Multi-Angle Yaw Rotation Frames, Human Skull 3D Visualization, Skull

### Community 13 - "UgaLogo"
Cohesion: 0.20
Nodes (5): UgaLogo, Georgia Bulldogs Athletics Branding, University of Georgia Logo, Projection Graphic Asset, University of Georgia

### Community 15 - "main"
Cohesion: 0.32
Nodes (3): main(), tick(), Projector

### Community 18 - "test_js.js"
Cohesion: 0.32
Nodes (6): document, fetch(), FIELDS, pollState(), push(), STR_FIELDS

### Community 20 - "Dashboard"
Cohesion: 0.38
Nodes (3): Dashboard, tick(), main()

### Community 51 - "Q: Why does main() connect Camera Streaming & Video Ingestion to 15 different rendering models, dispatch stores, and display communities?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Why does main() connect Camera Streaming & Video Ingestion to 15 different rendering models, dispatch stores, and display communities?, Source Nodes

### Community 52 - "Q: How does Smart Parked Vehicle Rejection work in Detector and filter out stationary cars?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: How does Smart Parked Vehicle Rejection work in Detector and filter out stationary cars?, Source Nodes

## Knowledge Gaps
- **11 isolated node(s):** `all-seeing-eye`, `Human Cranium and Sutures`, `Mandible and Maxilla Dentition`, `Georgia Bulldogs Athletics Branding`, `Projection Graphic Asset` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 177 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `run_stream.py`, `All-Seeing Eye Project`, `DragonEye`, `JokerEye`, `MonsterEye`, `SnakeEye`, `ZombieEye`, `Skull`, `Eye`, `UgaLogo`, `make_dashboard_server`, `BugEye`, `SpiderEye`, `CreepyFigure`, `DancingSkeleton`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `main()` (e.g. with `.get_frame()` and `BugEye`) actually correct?**
  _`main()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `all-seeing-eye`, `Human Cranium and Sutures`, `Mandible and Maxilla Dentition` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `run_stream.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12098188194038574 - nodes in this community are weakly interconnected._
- **Why does `Eye` connect `Eye` to `run_stream.py`, `main`, `All-Seeing Eye Project`, `main`, `Dashboard`, `._build_static_layers`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Eye` (e.g. with `Perspective-Correct Gaze Mirroring` and `Procedural Eyeball Engine`) actually correct?**
  _`Eye` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `re` be split into smaller, more focused modules?**
  _Cohesion score 0.047619047619047616 - nodes in this community are weakly interconnected._