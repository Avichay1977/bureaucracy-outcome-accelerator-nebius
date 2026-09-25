from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

OUT = Path(r"C:\Users\tuchm\Documents\AVI_OS\Competitions\Amazon_Alexa_2026\amazon-alexa-bureaucracy-outcome-demo.webm")

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8766")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()
    def do_POST(self):
        if self.path != "/save":
            self.send_error(404); return
        n = int(self.headers.get("Content-Length","0"))
        data = self.rfile.read(n)
        OUT.write_bytes(data)
        self.send_response(200); self.cors()
        self.send_header("Content-Type","application/json")
        body = ("{\"saved\":true,\"bytes\":%d}" % len(data)).encode()
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

ThreadingHTTPServer(("127.0.0.1",8767),H).serve_forever()