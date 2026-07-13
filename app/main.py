from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB = DATA / "irvine.db"

app = FastAPI(title="Irvine Life Guide", version="1.1.0")
app.mount("/assets", StaticFiles(directory=ROOT / "app" / "static"), name="assets")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DATA.mkdir(exist_ok=True)
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS places (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, name_zh TEXT NOT NULL,
          district TEXT NOT NULL, category TEXT NOT NULL, address TEXT,
          lat REAL, lng REAL, price_level INTEGER DEFAULT 0,
          tags TEXT NOT NULL DEFAULT '[]', description TEXT NOT NULL,
          description_zh TEXT NOT NULL, website TEXT, source TEXT,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, venue TEXT,
          district TEXT, starts_at TEXT, ends_at TEXT, url TEXT,
          source TEXT, category TEXT, image TEXT, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS favorites (
          item_type TEXT NOT NULL, item_id TEXT NOT NULL,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY(item_type, item_id)
        );
        """)
        if conn.execute("SELECT COUNT(*) FROM places").fetchone()[0] == 0:
            places = json.loads((DATA / "places.json").read_text(encoding="utf-8"))
            conn.executemany("""
              INSERT INTO places VALUES (:id,:name,:name_zh,:district,:category,:address,
              :lat,:lng,:price_level,:tags,:description,:description_zh,:website,:source,:updated_at)
            """, [{**p, "tags": json.dumps(p.get("tags", []), ensure_ascii=False)} for p in places])
        if conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
            events = json.loads((DATA / "events.sample.json").read_text(encoding="utf-8"))
            conn.executemany("INSERT INTO events VALUES (:id,:title,:venue,:district,:starts_at,:ends_at,:url,:source,:category,:image,:updated_at)", events)


class Favorite(BaseModel):
    item_type: str
    item_id: str


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "app" / "static" / "index.html")


@app.get("/map")
def map_page() -> FileResponse:
    return FileResponse(ROOT / "app" / "static" / "map.html")


@app.get("/api/places")
def places(district: str | None = None, category: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT p.*, EXISTS(SELECT 1 FROM favorites f WHERE f.item_type='place' AND f.item_id=p.id) favorite FROM places p WHERE 1=1"
    args: list[Any] = []
    if district:
        sql += " AND district=?"
        args.append(district)
    if category:
        sql += " AND category=?"
        args.append(category)
    if q:
        sql += " AND (name LIKE ? OR name_zh LIKE ? OR description LIKE ? OR description_zh LIKE ?)"
        args.extend([f"%{q}%"] * 4)
    sql += " ORDER BY district, name"
    with connect() as conn:
        rows = [dict(r) for r in conn.execute(sql, args)]
    for row in rows:
        row["tags"] = json.loads(row["tags"])
        row["favorite"] = bool(row["favorite"])
    return rows


@app.get("/api/events")
def events() -> list[dict[str, Any]]:
    with connect() as conn:
        return [dict(r) for r in conn.execute("""
          SELECT e.*, EXISTS(SELECT 1 FROM favorites f WHERE f.item_type='event' AND f.item_id=e.id) favorite
          FROM events e ORDER BY starts_at
        """)]


@app.post("/api/favorites")
def add_favorite(fav: Favorite) -> dict[str, bool]:
    if fav.item_type not in {"place", "event"}:
        raise HTTPException(400, "Invalid item_type")
    with connect() as conn:
        conn.execute("INSERT OR IGNORE INTO favorites(item_type,item_id) VALUES (?,?)", (fav.item_type, fav.item_id))
    return {"ok": True}


@app.delete("/api/favorites/{item_type}/{item_id}")
def delete_favorite(item_type: str, item_id: str) -> dict[str, bool]:
    with connect() as conn:
        conn.execute("DELETE FROM favorites WHERE item_type=? AND item_id=?", (item_type, item_id))
    return {"ok": True}


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    with connect() as conn:
        districts = [r[0] for r in conn.execute("SELECT DISTINCT district FROM places ORDER BY district")]
        categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM places ORDER BY category")]
    return {"districts": districts, "categories": categories}
