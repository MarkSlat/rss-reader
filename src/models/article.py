from dataclasses import dataclass
import datetime

from src.models.publisher import Publisher

@dataclass
class Article:
    title: str
    description: str
    published_date: datetime
    publisher: Publisher
    vector: list[float] | None
    image_url: str | None
    