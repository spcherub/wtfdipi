# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

WTFDIPI ("Where The F*** Did I Put It") is a personal item-location tracker designed to run on a Raspberry Pi. Users register locations and items, record where items are placed, and search to find them later.

## Running the App

```bash
pip install -r requirements.txt
python3 app.py
```

The dev server starts on `http://0.0.0.0:8000`. For production, use gunicorn:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

## Architecture

The entire app is two files:

- **`app.py`** — Flask backend: SQLite DB layer, all 8 REST API endpoints, and the single route serving the frontend
- **`templates/index.html`** — Single-page app with vanilla HTML/CSS/JS; no build step, no framework

**Data model (SQLite, auto-created as `wtfdipi.db`):**
- `locations(id, name UNIQUE, created_at)`
- `items(id, name UNIQUE, location_id FK, placed_at, created_at)`

**API surface:**
- `GET/POST /api/locations`, `PUT/DELETE /api/locations/<id>`
- `GET/POST /api/items`, `PUT/DELETE /api/items/<id>`
- `POST /api/items/<id>/place`, `POST /api/items/<id>/unplace`
- `GET /api/search?q=`
- `POST /api/locations/import` (CSV bulk import)

## Frontend

Four-tab SPA: **Find** (search), **Put** (place/unplace items), **Items** (manage item registry), **Locations** (manage location registry). Client-side state holds loaded items/locations arrays; no frontend build tooling.

## No Tests

There is no test suite. Manual browser testing is the intended approach given the project's simplicity.
