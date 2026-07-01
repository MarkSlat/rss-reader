from dataclasses import dataclass

@dataclass
class Publisher:
    id: int | None = None
    name: str | None = None
    rss_url: str = ""
    favicon_url: str | None = None