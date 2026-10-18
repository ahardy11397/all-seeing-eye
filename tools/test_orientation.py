#!/usr/bin/env python3
"""Automated tests for output image flip settings and orientation logic."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
from PIL import Image
from config import Settings, settings
from projector import apply_orientation_flips


def test_settings_defaults_and_serialization():
    s = Settings()
    assert s.flip_horizontal is False
    assert s.flip_vertical is False

    tmp_path = "scratch_test_settings_tmp.json"
    try:
        s.flip_horizontal = True
        s.flip_vertical = True
        s.save(tmp_path)

        # Check trailing newline
        with open(tmp_path, "r") as f:
            content = f.read()
        assert content.endswith("\n"), "Settings file must end with newline"

        # Check reload
        s2 = Settings()
        s2.load(tmp_path)
        assert s2.flip_horizontal is True
        assert s2.flip_vertical is True
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    print("PASS: Settings defaults and serialization")


def test_apply_orientation_flips():
    # Asymmetric test image: red pixel only at top-left (0, 0)
    arr = np.zeros((10, 10, 3), dtype=np.uint8)
    arr[0, 0] = [255, 0, 0]
    img = Image.fromarray(arr)

    # 1. No flip
    settings.flip_horizontal = False
    settings.flip_vertical = False
    out = apply_orientation_flips(img.copy())
    assert list(out.getpixel((0, 0))) == [255, 0, 0]

    # 2. Horizontal flip only (top-right should be red)
    settings.flip_horizontal = True
    settings.flip_vertical = False
    out = apply_orientation_flips(img.copy())
    assert list(out.getpixel((9, 0))) == [255, 0, 0]
    assert list(out.getpixel((0, 0))) == [0, 0, 0]

    # 3. Vertical flip only (bottom-left should be red)
    settings.flip_horizontal = False
    settings.flip_vertical = True
    out = apply_orientation_flips(img.copy())
    assert list(out.getpixel((0, 9))) == [255, 0, 0]
    assert list(out.getpixel((0, 0))) == [0, 0, 0]

    # 4. Both flips (bottom-right should be red)
    settings.flip_horizontal = True
    settings.flip_vertical = True
    out = apply_orientation_flips(img.copy())
    assert list(out.getpixel((9, 9))) == [255, 0, 0]
    assert list(out.getpixel((0, 0))) == [0, 0, 0]

    # Reset
    settings.flip_horizontal = False
    settings.flip_vertical = False
    print("PASS: apply_orientation_flips transformations")


def test_dashboard_server_bool_parsing():
    import threading
    import time
    import requests
    import dashboard_server as ds

    class MockStore:
        def latest(self):
            return (1, b"eye", b"cam", {"fps": 30, "detection": None, "parked": False, "iris": {"x": 0, "y": 0}})

    ds.store = MockStore()
    server = ds.make_dashboard_server(ds.store, 8097, None, host="127.0.0.1")
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)

    base = "http://127.0.0.1:8097"
    try:
        # Check initial state exposes flip settings
        st = requests.get(f"{base}/api/state").json()["settings"]
        assert "flip_horizontal" in st
        assert "flip_vertical" in st

        # Test native boolean True
        r = requests.post(f"{base}/api/settings", json={"flip_horizontal": True}).json()
        assert r["ok"] is True
        assert r["applied"]["flip_horizontal"] is True
        assert settings.flip_horizontal is True

        # Test string boolean "false" (must parse as False, not True!)
        r = requests.post(f"{base}/api/settings", json={"flip_horizontal": "false"}).json()
        assert r["ok"] is True
        assert r["applied"]["flip_horizontal"] is False
        assert settings.flip_horizontal is False

        # Test string boolean "true"
        r = requests.post(f"{base}/api/settings", json={"flip_vertical": "true"}).json()
        assert r["ok"] is True
        assert r["applied"]["flip_vertical"] is True
        assert settings.flip_vertical is True

        # Test string boolean "0"
        r = requests.post(f"{base}/api/settings", json={"flip_vertical": "0"}).json()
        assert r["ok"] is True
        assert r["applied"]["flip_vertical"] is False
        assert settings.flip_vertical is False

        # Reset
        requests.post(f"{base}/api/settings", json={"flip_horizontal": False, "flip_vertical": False})
    finally:
        server.shutdown()
    print("PASS: dashboard_server boolean parsing & API handling")


if __name__ == "__main__":
    test_settings_defaults_and_serialization()
    test_apply_orientation_flips()
    test_dashboard_server_bool_parsing()
    print("ALL TESTS PASSED!")
