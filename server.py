"""Serve any TDengine assets to a CesiumJS page.

Edit query.sql to match your tables. The browser only receives JSON.
The database password stays in this process.
"""

from __future__ import annotations

import base64
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "index.html"
QUERY_FILE = ROOT / "query.sql"
SEED_FILE = ROOT / "seed.sql"
TRACK_FILE = ROOT / "track.sql"
SAMPLE_MARK = "cesium-tdengine:sample"

CACHE_SECONDS = float(os.environ.get("CACHE_SECONDS", "4"))

_lock = threading.Lock()
_cache = {"at": 0.0, "body": None}
_seed_lock = threading.Lock()
_seeded = False
_env_loaded = False
_httpd: ThreadingHTTPServer | None = None


def load_env() -> None:
    """Apply a .env file when a variable is not already set."""
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def connection() -> tuple[str, str, str]:
    load_env()
    url = os.environ.get("TAOS_URL", "http://localhost:6041/rest/sql")
    user = os.environ.get("TAOS_USER", "root")
    password = os.environ.get("TAOS_PASSWORD", "taosdata")
    return url, user, password


def bind_address() -> tuple[str, int]:
    load_env()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8095"))
    return host, port


def load_sql(path: Path) -> str:
    lines = []
    for line in path.read_text().splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines).strip().rstrip(";").strip()


def statements(path: Path) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    for line in path.read_text().splitlines():
        if line.strip().startswith("--"):
            continue
        buf.append(line)
        if line.rstrip().endswith(";"):
            stmt = "\n".join(buf).strip().rstrip(";").strip()
            if stmt:
                chunks.append(stmt)
            buf = []
    tail = "\n".join(buf).strip().rstrip(";").strip()
    if tail:
        chunks.append(tail)
    return chunks


def query(sql: str) -> list[dict]:
    url, user, password = connection()
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    request = Request(
        url,
        data=sql.encode(),
        headers={"Authorization": f"Basic {token}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            body = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(detail or f"HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"cannot reach {url}: {exc.reason}") from exc
    if body.get("code") != 0:
        raise RuntimeError(body.get("desc") or json.dumps(body))
    names = [column[0] for column in body.get("column_meta") or []]
    return [dict(zip(names, row)) for row in body.get("data") or []]


def table_missing(message: str) -> bool:
    text = message.lower()
    return "not exist" in text or "does not exist" in text


def seed_sample() -> None:
    global _seeded
    with _seed_lock:
        if _seeded:
            return
        for stmt in statements(SEED_FILE):
            query(stmt)
        _seeded = True
        print("Created sample database geo (PUMP-12, TANK-7, METER-4).", flush=True)


def assets() -> dict:
    with _lock:
        if _cache["body"] is not None and time.time() - _cache["at"] < CACHE_SECONDS:
            return _cache["body"]
    sql = load_sql(QUERY_FILE)
    try:
        rows = query(sql)
    except RuntimeError as exc:
        sample = SAMPLE_MARK in QUERY_FILE.read_text()
        if sample and table_missing(str(exc)):
            seed_sample()
            rows = query(sql)
        else:
            raise
    clean = []
    for row in rows:
        if row.get("lon") is None or row.get("lat") is None:
            continue
        if row.get("height") is None:
            row["height"] = 0
        clean.append(row)
    body = {"source": "TDengine", "assets": clean}
    with _lock:
        _cache.update(at=time.time(), body=body)
    return body


def track(asset_id: str) -> dict:
    if not TRACK_FILE.exists():
        raise RuntimeError(
            "Copy examples/track.sql to track.sql to serve paths for moving assets."
        )
    if not asset_id or not all(ch.isalnum() or ch in "-_." for ch in asset_id):
        raise RuntimeError(
            "id may only contain letters, numbers, and . _ -"
        )
    sql = load_sql(TRACK_FILE).replace("{id}", asset_id)
    return {"id": asset_id, "samples": query(sql)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)

    def _send(self, code: int, payload, content_type: str) -> None:
        data = payload if isinstance(payload, bytes) else payload.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/assets":
            try:
                self._send(200, json.dumps(assets()), "application/json")
            except Exception as exc:  # noqa: BLE001
                self._send(502, json.dumps({"error": str(exc)}), "application/json")
            return
        if parsed.path == "/api/track":
            asset_id = (parse_qs(parsed.query).get("id") or [""])[0]
            try:
                self._send(200, json.dumps(track(asset_id)), "application/json")
            except Exception as exc:  # noqa: BLE001
                self._send(502, json.dumps({"error": str(exc)}), "application/json")
            return
        self._send(404, "not found", "text/plain; charset=utf-8")


def start() -> str:
    """Bind the page and return its address. The port moves forward if busy."""
    global _httpd
    if _httpd is not None:
        host, port = _httpd.server_address[:2]
        return f"http://{host}:{port}/"
    host, port = bind_address()
    last_error: OSError | None = None
    for candidate in range(port, port + 20):
        try:
            _httpd = ThreadingHTTPServer((host, candidate), Handler)
            break
        except OSError as exc:
            last_error = exc
    if _httpd is None:
        raise SystemExit(f"Could not bind {host}:{port}: {last_error}")
    bound_host, bound_port = _httpd.server_address[:2]
    shown = "127.0.0.1" if bound_host in ("0.0.0.0", "::") else bound_host
    url, _, _ = connection()
    print(f"TDengine  {url}", flush=True)
    print(f"Query     {QUERY_FILE}", flush=True)
    return f"http://{shown}:{bound_port}/"


def serve_forever() -> None:
    if _httpd is None:
        start()
    assert _httpd is not None
    _httpd.serve_forever()


def main() -> None:
    url = start()
    print(f"Open      {url}", flush=True)
    serve_forever()


if __name__ == "__main__":
    main()
