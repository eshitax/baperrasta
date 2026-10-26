#!/usr/bin/env python3
import json
import os
import secrets
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
PORT = int(os.environ.get("PORT", "8080"))
BOARD_FILE = ROOT / "data" / "board.json"
HTML_PAGES = {
    "/about": "about.html",
    "/privacy": "privacy.html",
    "/disclaimer": "disclaimer.html",
}
MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".webmanifest": "application/manifest+json",
    ".json": "application/json; charset=utf-8",
    ".xml": "application/xml",
    ".txt": "text/plain; charset=utf-8",
    ".woff2": "font/woff2",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".mp3": "audio/mpeg",
    ".svg": "image/svg+xml",
}


def week_id():
    import math
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).timestamp() * 1000
    t = math.floor((now + 21600000) / 86400000)
    start = (t - (t + 5) % 7) * 86400000
    return datetime.fromtimestamp(start / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def load_board():
    if BOARD_FILE.exists():
        try:
            return json.loads(BOARD_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"ok": True, "week": week_id(), "top": [], "all": [], "cut": 0}


def fetch_live_board():
    req = urllib.request.Request(
        "https://baperrasta.com/api/board",
        headers={"User-Agent": "BaperRastaClone/1.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        data = r.read()
    board = json.loads(data)
    if board.get("ok"):
        BOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
        BOARD_FILE.write_bytes(data)
        return board
    raise ValueError("board")


def rank_for(loss, rows):
    better = sum(1 for row in rows if row.get("loss", 0) > loss)
    return better + 1


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, **MIME}

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def rewrite_path(self):
        raw = self.path.split("?", 1)[0].rstrip("/") or "/"
        if raw.startswith("/api/board"):
            return "board"
        if raw in HTML_PAGES:
            qs = ""
            if "?" in self.path:
                qs = "?" + self.path.split("?", 1)[1]
            self.path = "/" + HTML_PAGES[raw] + qs
        return None

    def do_GET(self):
        if self.rewrite_path() == "board":
            self.send_board()
            return
        super().do_GET()

    def do_HEAD(self):
        if self.rewrite_path() == "board":
            self.send_board()
            return
        super().do_HEAD()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            body = {}
        if path == "/api/run":
            self.send_json({"t": secrets.token_urlsafe(16), "ok": True})
            return
        if path == "/api/score":
            self.send_json(self.score(body))
            return
        if path == "/api/name":
            name = str(body.get("name") or "").strip()[:24]
            if not name:
                self.send_json({"ok": False, "error": "empty"}, 400)
                return
            self.send_json({"ok": True, "name": name})
            return
        if path == "/api/subscribe":
            email = str(body.get("email") or "").strip()
            if "@" not in email:
                self.send_json({"ok": False}, 400)
                return
            self.send_json({"ok": True})
            return
        self.send_json({"ok": False}, 404)

    def send_board(self):
        try:
            board = fetch_live_board()
        except Exception:
            board = load_board()
        self.send_json(board)

    def score(self, body):
        board = load_board()
        loss = int(body.get("loss") or 0)
        rows = board.get("top") or []
        cut = int(board.get("cut") or 0)
        week = board.get("week") or week_id()
        if loss <= cut:
            return {
                "ok": True,
                "week": week,
                "cut": cut,
                "best": loss,
                "rank": None,
                "need": cut + 50 - loss,
                "named": False,
            }
        rank = rank_for(loss, rows)
        return {
            "ok": True,
            "week": week,
            "cut": cut,
            "best": loss,
            "rank": rank,
            "need": 0,
            "named": False,
        }

    def send_json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("Baper Rasta at http://0.0.0.0:%s" % PORT, flush=True)
    httpd.serve_forever()
