"""
Receipt Splitter — Flask upload server.

Receives photo uploads from the PWA and saves them to your
Google Drive Receipts folder so read_receipts.py picks them up.

Setup (run once, in PowerShell):
    pip install flask flask-cors pyopenssl
    python server.py

On your iPhone, open (via Tailscale):
    https://<tailscale-hostname>:5555

Accept the self-signed cert warning once — then camera works fine.

Upload format matches read_receipts.py:
    Receipts/<id>.jpg   — the photo
    Receipts/<id>.json  — { id, timestamp, description, photo, status }
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# ── Config ──────────────────────────────────────────────────────────
# Set GDRIVE_ROOT env var to your Google Drive path, e.g. C:\Users\<you>\My Drive
GDRIVE_ROOT    = os.environ.get("GDRIVE_ROOT", r"C:\Users\<your-username>\My Drive")
RECEIPTS_QUEUE = os.path.join(GDRIVE_ROOT, "Receipts")
PORT           = int(os.environ.get("PORT", 5555))

app = Flask(__name__)
CORS(app, origins="*")


@app.route("/upload", methods=["POST"])
def upload():
    photo_file = request.files.get("photo")
    meta_str   = request.form.get("metadata", "{}")

    if not photo_file:
        return jsonify({"error": "no photo"}), 400

    try:
        meta = json.loads(meta_str)
    except json.JSONDecodeError:
        return jsonify({"error": "bad metadata JSON"}), 400

    raw_id = meta.get("id", "")
    if not re.fullmatch(r'rcpt_[0-9]+_[a-z0-9]{5}', raw_id):
        return jsonify({"error": "invalid receipt id"}), 400
    receipt_id = raw_id
    os.makedirs(RECEIPTS_QUEUE, exist_ok=True)

    header_bytes = photo_file.stream.read(8)
    is_jpeg = header_bytes[:3] == b'\xff\xd8\xff'
    is_png  = header_bytes[:8] == b'\x89PNG\r\n\x1a\n'
    if not (is_jpeg or is_png):
        return jsonify({"error": "invalid image — must be JPEG or PNG"}), 400
    photo_file.stream.seek(0)

    ext = "jpg" if is_jpeg else "png"
    photo_filename = f"{receipt_id}.{ext}"
    photo_file.save(os.path.join(RECEIPTS_QUEUE, photo_filename))

    ts_raw = meta.get("timestamp", "")
    try:
        datetime.fromisoformat(ts_raw)
        timestamp = ts_raw
    except (ValueError, TypeError):
        timestamp = datetime.now().isoformat()

    description = meta.get("description", "")[:2000]

    record = {
        "id":          receipt_id,
        "timestamp":   timestamp,
        "description": description,
        "photo":       photo_filename,
        "status":      "QUEUED",
    }
    with open(os.path.join(RECEIPTS_QUEUE, f"{receipt_id}.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"[{datetime.now():%H:%M:%S}] saved {receipt_id} — {description[:60]}")
    return jsonify({"status": "ok", "id": receipt_id})


@app.route("/ping")
def ping():
    pending = 0
    if os.path.exists(RECEIPTS_QUEUE):
        pending = sum(1 for f in os.listdir(RECEIPTS_QUEUE) if f.endswith(".json"))
    return jsonify({"status": "ok", "pending_receipts": pending})


if __name__ == "__main__":
    Path(RECEIPTS_QUEUE).mkdir(parents=True, exist_ok=True)
    print(f"Receipt Splitter server → https://0.0.0.0:{PORT}")
    print(f"Receipts queue         → {RECEIPTS_QUEUE}")
    print()
    # ssl_context='adhoc' generates a self-signed cert — accept once in Safari, then camera works.
    app.run(host="0.0.0.0", port=PORT, debug=False, ssl_context="adhoc")
