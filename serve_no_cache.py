import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Force UTF-8 encoding so the browser doesn't guess Windows-1252
        if self.path.endswith(".html"):
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT} with No-Cache headers")
    httpd.serve_forever()
