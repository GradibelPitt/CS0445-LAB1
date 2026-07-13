from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Event:
    id: str; title: str; venue: str | None; district: str | None
    starts_at: str | None; ends_at: str | None; url: str
    source: str; category: str | None = None; image: str | None = None
    updated_at: str = datetime.now().date().isoformat()
    def dict(self): return asdict(self)

class EventSource(ABC):
    name: str
    @abstractmethod
    async def fetch(self) -> list[Event]: ...
