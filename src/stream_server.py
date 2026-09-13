from __future__ import annotations

import io
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config import settings


class FrameBroadcaster:
    """Holds the latest rendered eye JPEG. Stream clients pull it at their own pace."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jpeg: bytes | None = None
        self._seq = 0
        self._event = threading.Event()

    def publish(self, jpeg: bytes) -> None:
        with self._lock:
            self._jpeg = jpeg
            self._seq += 1
        self._event.set()

    def latest(self) -> tuple[int, bytes | None]:
        with self._lock:
            return self._seq, self._jpeg

    def wait_for_frame(self, timeout: float = 2.0) -> None:
        self._event.wait(timeout)
        self._event.clear()


broadcaster = FrameBroadcaster()


class _Handler(BaseHTTPRequestHandler):
    broadcaster: FrameBroadcaster = None  # type: ignore[assignment]

    def log_message(self, fmt, *args):  # quiet
        pass

    def do_GET(self):  # noqa: N802
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._serve_html()
        elif path == "/stream":
            self._serve_stream()
        elif path == "/snapshot":
            self._serve_snapshot()
        else:
            self.send_error(404)

    def _serve_html(self) -> None:
        html = """<!DOCTYPE html><html><head><title>All-Seeing Eye</title>
<style>
html,body{margin:0;padding:0;background:#000;height:100%;overflow:hidden}
#eye{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
max-width:100vw;max-height:100vh;}
</style></head><body>
<img id="eye" src="/snapshot">
<script>
// MJPEG streams don't work in Android WebView; poll fresh snapshots instead.
var img = document.getElementById('eye');
var last = 0;

function refresh() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/snapshot?t=' + Date.now(), true);
  xhr.responseType = 'blob';
  xhr.onload = function() {
    if (xhr.status === 200 && xhr.response.size > 0) {
      var url = URL.createObjectURL(xhr.response);
      img.src = url;
      if (last) { URL.revokeObjectURL(last); }
      last = url;
    }
    setTimeout(refresh, 40);
  };
  xhr.onerror = function() { setTimeout(refresh, 500); };
  xhr.send();
}
refresh();
</script>
</body></html>"""
        data = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        last_seq = -1
        frame_interval = 1.0 / max(1, settings.stream_fps)
        try:
            while True:
                seq, jpeg = self.broadcaster.latest()
                if jpeg is not None and seq != last_seq:
                    last_seq = seq
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(jpeg)}\r\n\r\n".encode())
                    self.wfile.write(jpeg)
                    self.wfile.write(b"\r\n")
                time.sleep(frame_interval)
        except (BrokenPipeError, ConnectionResetError):
            return

    def _serve_snapshot(self) -> None:
        _, jpeg = self.broadcaster.latest()
        if jpeg is None:
            self.send_error(503)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(jpeg)))
        self.end_headers()
        self.wfile.write(jpeg)


def make_server(broadcaster: FrameBroadcaster, port: int) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (_Handler,), {"broadcaster": broadcaster})
    return ThreadingHTTPServer(("0.0.0.0", port), handler)
