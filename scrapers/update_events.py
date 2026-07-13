from __future__ import annotations
import asyncio, sqlite3
from pathlib import Path
from feeds import SOURCES
ROOT=Path(__file__).resolve().parents[1]; DB=ROOT/'data'/'irvine.db'
async def main():
    gathered=[]
    for source in SOURCES:
        try: gathered.extend(await source.fetch())
        except Exception as exc: print(f"[warn] {source.name}: {exc}")
    with sqlite3.connect(DB) as conn:
        conn.executemany("""INSERT INTO events(id,title,venue,district,starts_at,ends_at,url,source,category,image,updated_at)
        VALUES(:id,:title,:venue,:district,:starts_at,:ends_at,:url,:source,:category,:image,:updated_at)
        ON CONFLICT(id) DO UPDATE SET title=excluded.title,url=excluded.url,updated_at=excluded.updated_at""",[e.dict() for e in gathered])
    print(f"Updated {len(gathered)} events")
if __name__=='__main__': asyncio.run(main())
