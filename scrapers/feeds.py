from __future__ import annotations
import hashlib
import re
import httpx
from bs4 import BeautifulSoup
from .base import Event, EventSource

class LinkCalendarSource(EventSource):
    """Conservative fallback scraper. Extracts event-like links without bypassing access controls."""
    def __init__(self, name: str, url: str, district: str, category: str):
        self.name, self.url, self.district, self.category = name, url, district, category
    async def fetch(self) -> list[Event]:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent":"IrvineAtlas/1.0 (+public community guide)"}) as client:
            response = await client.get(self.url); response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser"); out=[]; seen=set()
        for a in soup.select("a[href]"):
            title=" ".join(a.get_text(" ", strip=True).split()); href=a.get("href","")
            if len(title)<8 or title.lower() in seen: continue
            if not re.search(r"event|festival|concert|class|workshop|market|movie|calendar", title+" "+href, re.I): continue
            seen.add(title.lower()); url=str(response.url.join(href)); eid=hashlib.sha1((self.name+url).encode()).hexdigest()[:16]
            out.append(Event(eid,title,self.name,self.district,None,None,url,self.name,self.category))
        return out[:40]

SOURCES=[
 LinkCalendarSource("City of Irvine","https://www.cityofirvine.org/events","Irvine","城市活动"),
 LinkCalendarSource("Irvine Spectrum Center","https://www.irvinespectrumcenter.com/events-promotions","Irvine Spectrum","娱乐购物"),
 LinkCalendarSource("UC Irvine","https://events.uci.edu","UCI / University Town Center","校园活动"),
]
