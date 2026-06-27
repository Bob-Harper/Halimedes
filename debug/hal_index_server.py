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
        # Classes
        if isinstance(node, ast.ClassDef):
            symbols.append(f"CLASS:{node.name}")

        # Functions (with signature)
        elif isinstance(node, ast.FunctionDef):
            params = []
            for arg in node.args.args:
                params.append(arg.arg)

            # Handle *args and **kwargs
            if node.args.vararg:
                params.append("*" + node.args.vararg.arg)
            if node.args.kwarg:
                params.append("**" + node.args.kwarg.arg)

            signature = f"{node.name}({', '.join(params)})"
            symbols.append(f"FUNC:{signature}")

        # Async functions
        elif isinstance(node, ast.AsyncFunctionDef):
            params = [arg.arg for arg in node.args.args]
            signature = f"{node.name}({', '.join(params)})"
            symbols.append(f"ASYNC:{signature}")

        # Imports
        elif isinstance(node, ast.Import):
            for n in node.names:
                symbols.append(f"IMPORT:{n.name}")

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                symbols.append(f"FROM:{node.module}")

    return symbols


WHITELIST_DIRS = {
    "audio_input",
    "audio_output",
    "body",
    "cortex",
    "dsl",
    "eyes",
    "helpers",
    "reflex",
    "vision_components",
    "vision_processing",
}

ROOT_FILES = {"main.py"}

def indexer():
    while True:
        new_index = {}

        # 1. Include root-level files (like main.py)
        for f in ROOT_FILES:
            full = os.path.join(ROOT, f)
            if os.path.isfile(full):
                mtime = os.path.getmtime(full)
                sha = sha256_of_file(full)
                symbols = extract_symbols(full)
                new_index[f] = {
                    "path": f,
                    "mtime": mtime,
                    "hash": sha,
                    "symbols": symbols,
                }

        # 2. Include ONLY top-level .py files inside whitelisted dirs
        for d in WHITELIST_DIRS:
            dir_path = os.path.join(ROOT, d)
            if not os.path.isdir(dir_path):
                continue

            for f in os.listdir(dir_path):
                if not f.endswith(".py"):
                    continue

                full = os.path.join(dir_path, f)
                rel = os.path.join(d, f)

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

        if path.startswith("/all"):
            prefix = self._query("path") or self._query("file")

            with LOCK:
                if prefix:
                    subset = {
                        k: v for k, v in INDEX.items()
                        if k == prefix or k.startswith(prefix + "/")
                    }
                    return self._json(subset)

                return self._json(INDEX)


        if path.startswith("/info"):
            # Accept both ?path= and ?file=
            q = self._query("path") or self._query("file")
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
            q = self._query("path") or self._query("file")
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
