# -*- coding: utf-8 -*-
"""
API headless para Lightsail: sirve el último estado calculado por
refresh_worker.py (analisis/_state.json) vía GET /api/state.

No recalcula nada por request (eso lo hace la tarea programada cada 15 min),
así que responde instantáneo y no golpea Binance en cada fetch del dashboard.

Config vía variables de entorno (ver .env.example):
  API_PORT        puerto de escucha (default 8787)
  API_KEY_SECRET  valor esperado en el header X-API-Key
  ALLOWED_ORIGIN  origen permitido para CORS (ej. https://tu-app.vercel.app)
"""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import engine  # noqa: E402

engine.load_dotenv()

PORT = int(os.environ.get("API_PORT", "8787"))
API_KEY_SECRET = os.environ.get("API_KEY_SECRET", "")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
STATE_PATH = os.path.join(engine.ANALISIS_DIR, "_state.json")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Headers", "X-API-Key, Content-Type")
        self.end_headers()
        try:
            self.wfile.write(b)
        except Exception:
            pass

    def _authorized(self):
        if not API_KEY_SECRET:
            return True
        return self.headers.get("X-API-Key") == API_KEY_SECRET

    def do_OPTIONS(self):
        self._send(204, "")

    def do_GET(self):
        if self.path == "/health":
            self._send(200, json.dumps({"ok": True, "ts": time.time()}))
            return
        if self.path != "/api/state":
            self._send(404, json.dumps({"error": "not found"}))
            return
        if not self._authorized():
            self._send(401, json.dumps({"error": "unauthorized"}))
            return
        if not os.path.exists(STATE_PATH):
            self._send(503, json.dumps({"status": "no_data", "msg": "Todavía no corrió el refresco inicial."}))
            return
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            self._send(200, f.read())


def main():
    if not API_KEY_SECRET:
        print("AVISO: API_KEY_SECRET no está definido — el endpoint quedará sin autenticación.")
    host = os.environ.get("API_HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, PORT), Handler)
    print(f"API de señales escuchando en http://{host}:{PORT}/api/state")
    server.serve_forever()


if __name__ == "__main__":
    main()
