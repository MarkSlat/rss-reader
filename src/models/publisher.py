from dataclasses import dataclass

@dataclass
class Publisher:
    name: str | None
    rss_url: str
    favicon_url: str | None