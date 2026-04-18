#!/usr/bin/env python3
import os
import ast
import json
import time
import hashlib
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

ROOT = "/home/msutt/hal"
INDEX = {}
LOCK = threading.Lock()

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_symbols(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
    except Exception:
        return []

    symbols = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            symbols.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            symbols.append(node.name)
        elif isinstance(node, ast.Import):
            for n in node.names:
                symbols.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                symbols.append(node.module)
    return symbols

def indexer():
    while True:
        new_index = {}
        for root, dirs, files in os.walk(ROOT):
            # skip venvs, git, caches
            dirs[:] = [d for d in dirs if d not in (".git", ".venv", "__pycache__")]

            for f in files:
                if not f.endswith(".py"):
                    continue

                full = os.path.join(root, f)
                rel = os.path.relpath(full, ROOT)
                mtime = os.path.getmtime(full)
                sha = sha256_of_file(full)
                symbols = extract_symbols(full)

                new_index[rel] = {
                    "path": rel,
                    "mtime": mtime,
                    "hash": sha,
                    "symbols": symbols,
                }

        with LOCK:
            INDEX.clear()
            INDEX.update(new_index)

        time.sleep(2)

class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        path = self.path

        if path.startswith("/tree"):
            query = urllib.parse.urlparse(path).query
            params = urllib.parse.parse_qs(query)
            prefix = params.get("path", [""])[0].strip()

            with LOCK:
                listing = sorted(INDEX.keys())

            if prefix:
                filtered = [
                    p for p in listing
                    if p == prefix or p.startswith(prefix + "/")
                ]
                return self._json(filtered)

            return self._json(listing)


        if path.startswith("/info"):
            q = self._query("path")
            if not q:
                return self._json({"error": "missing path"}, 400)

            with LOCK:
                info = INDEX.get(q)
            if not info:
                return self._json({"error": "not found"}, 404)

            return self._json(info)

        if path.startswith("/search"):
            sym = self._query("symbol")
            if not sym:
                return self._json({"error": "missing symbol"}, 400)

            results = []
            with LOCK:
                for rel, meta in INDEX.items():
                    if sym in meta["symbols"]:
                        results.append(rel)

            return self._json(results)
        if path.startswith("/file"):
            q = self._query("path")
            if not q:
                return self._json({"error": "missing path"}, 400)

            full = os.path.join(ROOT, q)
            if not os.path.isfile(full):
                return self._json({"error": "not found"}, 404)

            try:
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                return self._json({"error": str(e)}, 500)

            return self._json({"path": q, "content": content})

        return self._json({"error": "unknown endpoint"}, 404)

    def _query(self, key):
        if "?" not in self.path:
            return None
        _, qs = self.path.split("?", 1)
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                if k == key:
                    return v
        return None
    
def main():
    t = threading.Thread(target=indexer, daemon=True)
    t.start()

    server = HTTPServer(("0.0.0.0", 8765), Handler)
    print("HAL Index Server running on port 8765")
    server.serve_forever()

if __name__ == "__main__":
    main()
