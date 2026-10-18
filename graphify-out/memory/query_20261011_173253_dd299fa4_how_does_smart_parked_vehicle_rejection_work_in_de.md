---
type: "query"
date: "2026-10-11T17:32:53.770285+00:00"
question: "How does Smart Parked Vehicle Rejection work in Detector and filter out stationary cars?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["Smart Parked Vehicle Rejection", "Detector", "Track", "Detection", "Settings"]
---

# Q: How does Smart Parked Vehicle Rejection work in Detector and filter out stationary cars?

## Answer

Expanded from original query via vocab: [parked, vehicle, rejection, detector, detect, detection, tracker, tracking, tracks]. Traversal of graphify-out/graph.json reveals that Smart Parked Vehicle Rejection (README.md) is implemented by Detector._update_tracks() in src/detector.py:L49-L94. When YOLOv8 detects a vehicle (classes 2, 5, 7 at L107), Detector matches it to a Track history (L54-L65). If track.label == 'vehicle' and history has >= 6 frames, it computes the bounding box bounding span shift = hypot(max(xs)-min(xs), max(ys)-min(ys)) (L80). If shift < settings.parked_drift_px (default 25px in src/config.py:L30), it marks track.parked_until = now + settings.parked_cooldown_s (default 20.0s at L82). During candidate selection in detect() (L135-L149), any detection whose track has parked_until > now is skipped (L144-L145), allowing pedestrians or moving cars to take priority.

## Outcome

- Signal: useful

## Source Nodes

- Smart Parked Vehicle Rejection
- Detector
- Track
- Detection
- Settings