---
type: "query"
date: "2026-10-11T17:29:38.898856+00:00"
question: "Why does main() connect Camera Streaming & Video Ingestion to 15 different rendering models, dispatch stores, and display communities?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["run_stream_main", "src_main_main", "CameraManager", "make_server", "make_dashboard_server", "Projector"]
---

# Q: Why does main() connect Camera Streaming & Video Ingestion to 15 different rendering models, dispatch stores, and display communities?

## Answer

Expanded from original query via vocab: [main, camera, stream, eye, dispatch, dashboard, render, model, display, projector, store, tracker]. Traversal of graphify-out/graph.json revealed that main() acts as the central composition root and event loop hub across run_stream.py (headless streaming pipeline) and src/main.py (Tkinter projector pipeline). Specifically, run_stream_main (run_stream.py:L116) bridges Camera Streaming & Video Ingestion (via CameraManager:L145, .get_frame():L179, Detector:L117) to MJPEG Stream Broadcaster (make_server:L121), Dashboard State Store (make_dashboard_server:L125), and all 12 procedural rendering models (MonsterEye:L150, ZombieEye:L152, DragonEye:L154, SnakeEye:L156, SpiderEye:L158, BugEye:L160, CreepyFigure:L162, JokerEye:L164, Skull:L167, DancingSkeleton:L170, UgaLogo:L172). In src/main.py (L28), src_main_main serves the same role for local Tkinter projection (Projector:L40, tick():L129).

## Outcome

- Signal: useful

## Source Nodes

- run_stream_main
- src_main_main
- CameraManager
- make_server
- make_dashboard_server
- Projector