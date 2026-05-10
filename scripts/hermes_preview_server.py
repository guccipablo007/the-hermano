#!/usr/bin/env python3
import json
import mimetypes
import os
from pathlib import Path
from flask import Flask, abort, send_file
INDEX = Path("/root/.hermes/preview_links/index.json")
HOST = os.environ.get("HERMES_PREVIEW_HOST", "0.0.0.0")
PORT = int(os.environ.get("HERMES_PREVIEW_PORT", "9124"))
ALLOWED_ROOTS = [Path("/root/.hermes/newcoin_outputs"), Path("/root/.hermes/file_outputs"), Path("/root/.hermes/telegram_outputs"), Path("/root/.hermes/model_routing/test_outputs"), Path("/root/.hermes/rebuild_notes"), Path("/root/.hermes/scripts")]
ALLOWED_SUFFIXES = {".html", ".htm", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".md", ".json", ".csv"}
app = Flask(__name__)
def load_index():
    try: return json.loads(INDEX.read_text())
    except Exception: return {}
def is_allowed_path(path: Path):
    try: resolved = path.resolve()
    except Exception: return False
    if not resolved.is_file() or resolved.suffix.lower() not in ALLOWED_SUFFIXES: return False
    for root in ALLOWED_ROOTS:
        rr = root.resolve()
        if resolved == rr or rr in resolved.parents: return True
    return False
@app.route("/p/<token>")
def preview(token):
    item = load_index().get(token)
    if not item: abort(404)
    path = Path(item.get("path", ""))
    if not is_allowed_path(path): abort(403)
    if path.suffix.lower() in [".html", ".htm"]: return send_file(path, mimetype="text/html")
    return send_file(path, mimetype=mimetypes.guess_type(path.name)[0] or "application/octet-stream")
@app.route("/health")
def health(): return "OK\n"
if __name__ == "__main__": app.run(host=HOST, port=PORT)
