# WTFDIPI — Application Context Document

## Purpose

WTFDIPI ("Where The F*** Did I Put It") is a personal item-location tracker. It solves the problem of forgetting where physical objects are stored around a home or workspace.

The system maintains two registries — **locations** (storage spots described in plain language) and **items** (things that get stored) — and lets the user record which item is in which location. When the user needs to find something, they search by item name and get back the location along with a timestamp of when it was placed there.

## Hosting

The application is designed to run on a **Raspberry Pi** on a local network, accessible from any device (phone, tablet, laptop) via a web browser. It uses no external services or cloud dependencies — everything runs locally.

## Tech Stack

- **Backend**: Python 3 / Flask
- **Frontend**: Single-page HTML with vanilla JavaScript (no build step, no framework)
- **Database**: SQLite (single file: `wtfdipi.db`)
- **Fonts**: JetBrains Mono (loaded from Google Fonts CDN)

## Project Structure

```
wtfdipi/
├── app.py               # Flask server, REST API, and DB initialization
├── requirements.txt     # Single dependency: flask>=3.0
├── templates/
│   └── index.html       # Complete frontend (HTML + CSS + JS in one file)
└── wtfdipi.db           # SQLite database (auto-created on first run)
```

## Data Model

Two tables in SQLite:

**locations**
| Column     | Type    | Notes                          |
|------------|---------|--------------------------------|
| id         | INTEGER | Primary key, autoincrement     |
| name       | TEXT    | Unique, case-insensitive       |
| created_at | TEXT    | ISO datetime, default now      |

**items**
| Column      | Type    | Notes                                        |
|-------------|---------|----------------------------------------------|
| id          | INTEGER | Primary key, autoincrement                   |
| name        | TEXT    | Unique, case-insensitive                     |
| location_id | INTEGER | FK → locations(id), ON DELETE SET NULL        |
| placed_at   | TEXT    | ISO datetime, set when item is placed        |
| created_at  | TEXT    | ISO datetime, default now                    |

When a location is deleted, any items assigned to it have their `location_id` and `placed_at` set to NULL (they become unassigned, not deleted).

## REST API

All endpoints accept/return JSON. Base path: `/api`.

**Locations**
- `GET    /locations`         — List all locations
- `POST   /locations`         — Create location `{name}`
- `PUT    /locations/<id>`    — Rename location `{name}`
- `DELETE /locations/<id>`    — Delete location (unassigns its items)

**Items**
- `GET    /items`             — List all items (joined with location name)
- `POST   /items`             — Create item `{name}`
- `PUT    /items/<id>`        — Rename item `{name}`
- `DELETE /items/<id>`        — Delete item

**Placement**
- `POST   /items/<id>/place`   — Assign item to location `{location_id}`
- `POST   /items/<id>/unplace` — Clear item's location

**Search**
- `GET    /search?q=<query>`  — Search items by name (SQL LIKE match)

## Frontend

The UI is a single-page app with four tab views:

1. **Find** (🔍) — Text search across item names; results show location and time placed
2. **Put** (📌) — Two dropdowns (item + location) to record a placement; shows current assignments and unassigned items
3. **Items** (🏷) — CRUD list of items with inline edit
4. **Locations** (📍) — CRUD list of locations; each card shows items stored there

Design uses a dark theme with monospace typography and an orange accent color (`#e85d26`). All state is fetched from the API on each action (no client-side caching).

## Running

```bash
pip install -r requirements.txt
python3 app.py
# Serves on http://0.0.0.0:5000
```

Optional systemd service configuration is documented in the project README for auto-start on boot. For heavier use, gunicorn can replace the built-in Flask dev server.
