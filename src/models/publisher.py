from dataclasses import dataclass

@dataclass
class Publisher:
    name: str
    rss_url: str
    favicon_url: str