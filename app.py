#!/usr/bin/env python3
"""WTFDIPI — Where The F*** Did I Put It
A Flask app for tracking where you put things.
"""

import csv
import io
import os
import sqlite3
from datetime import datetime, timezone
from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wtfdipi.db")


# ── Database helpers ──────────────────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
            location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
            placed_at   TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    db.close()


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API: Locations ────────────────────────────────────────────────────────────

@app.route("/api/locations", methods=["GET"])
def list_locations():
    db = get_db()
    rows = db.execute("SELECT * FROM locations ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/locations", methods=["POST"])
def add_location():
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO locations (name) VALUES (?)", (name,))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Location already exists"}), 409
    return jsonify({"id": cur.lastrowid, "name": name}), 201


@app.route("/api/locations/<int:loc_id>", methods=["PUT"])
def update_location(loc_id):
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    db.execute("UPDATE locations SET name = ? WHERE id = ?", (name, loc_id))
    db.commit()
    return jsonify({"id": loc_id, "name": name})


@app.route("/api/locations/<int:loc_id>", methods=["DELETE"])
def delete_location(loc_id):
    db = get_db()
    db.execute("UPDATE items SET location_id = NULL, placed_at = NULL WHERE location_id = ?", (loc_id,))
    db.execute("DELETE FROM locations WHERE id = ?", (loc_id,))
    db.commit()
    return "", 204


@app.route("/api/locations/import", methods=["POST"])
def import_locations_csv():
    """Import locations from a CSV file.

    Accepts a multipart/form-data POST with a single file field named 'file'.
    The CSV must have a header row containing a 'name' column (case-insensitive).
    A plain single-column CSV with no header is also accepted — every row is
    treated as a location name.

    Returns a JSON summary:
        {imported: N, skipped: N, errors: [{row: N, value: "...", reason: "..."}]}
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded — send a 'file' field"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "No filename provided"}), 400
    if not f.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only .csv files are accepted"}), 415

    try:
        content = f.read().decode("utf-8-sig")  # strip BOM if present
    except UnicodeDecodeError:
        return jsonify({"error": "File must be UTF-8 encoded"}), 400

    reader = csv.DictReader(io.StringIO(content))

    # Detect whether there is a 'name' header (case-insensitive).
    # If the CSV has no recognised header we fall back to treating the first
    # (and only expected) column as the location name.
    fieldnames = [fn.strip().lower() for fn in (reader.fieldnames or [])]
    has_name_header = "name" in fieldnames

    if not has_name_header:
        # Re-read as a plain list, no header
        reader = csv.reader(io.StringIO(content))

    db = get_db()
    imported = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header row
        if has_name_header:
            # DictReader row — normalise keys to lowercase
            normalised = {k.strip().lower(): v.strip() for k, v in row.items()}
            name = normalised.get("name", "")
        else:
            # Plain csv.reader row
            if not row:
                continue
            name = row[0].strip()

        if not name:
            errors.append({"row": row_num, "value": "", "reason": "Empty name — skipped"})
            skipped += 1
            continue

        try:
            db.execute("INSERT INTO locations (name) VALUES (?)", (name,))
            imported += 1
        except sqlite3.IntegrityError:
            errors.append({"row": row_num, "value": name, "reason": "Already exists — skipped"})
            skipped += 1

    db.commit()
    return jsonify({"imported": imported, "skipped": skipped, "errors": errors}), 200


# ── API: Items ────────────────────────────────────────────────────────────────

@app.route("/api/items", methods=["GET"])
def list_items():
    db = get_db()
    rows = db.execute(
        """
        SELECT i.id, i.name, i.location_id, i.placed_at, i.created_at,
               l.name AS location_name
        FROM items i
        LEFT JOIN locations l ON l.id = i.location_id
        ORDER BY i.name
        """
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/items", methods=["POST"])
def add_item():
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO items (name) VALUES (?)", (name,))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Item already exists"}), 409
    return jsonify({"id": cur.lastrowid, "name": name}), 201


@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    db.execute("UPDATE items SET name = ? WHERE id = ?", (name, item_id))
    db.commit()
    return jsonify({"id": item_id, "name": name})


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    db = get_db()
    db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    return "", 204


# ── API: Placement ────────────────────────────────────────────────────────────

@app.route("/api/items/<int:item_id>/place", methods=["POST"])
def place_item(item_id):
    location_id = (request.json or {}).get("location_id")
    if not location_id:
        return jsonify({"error": "location_id is required"}), 400
    now = datetime.now(timezone.utc).isoformat()
    db = get_db()
    db.execute(
        "UPDATE items SET location_id = ?, placed_at = ? WHERE id = ?",
        (location_id, now, item_id),
    )
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/items/<int:item_id>/unplace", methods=["POST"])
def unplace_item(item_id):
    db = get_db()
    db.execute(
        "UPDATE items SET location_id = NULL, placed_at = NULL WHERE id = ?",
        (item_id,),
    )
    db.commit()
    return jsonify({"ok": True})


# ── API: Search ───────────────────────────────────────────────────────────────

@app.route("/api/search", methods=["GET"])
def search_items():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    db = get_db()
    rows = db.execute(
        """
        SELECT i.id, i.name, i.location_id, i.placed_at,
               l.name AS location_name
        FROM items i
        LEFT JOIN locations l ON l.id = i.location_id
        WHERE i.name LIKE ?
        ORDER BY i.name
        """,
        (f"%{q}%",),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
