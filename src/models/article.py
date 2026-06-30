from dataclasses import dataclass
import datetime

from src.models.publisher import Publisher

@dataclass
class Article:
    url: str
    title: str
    description: str
    published_date: datetime
    publisher: Publisher
    embedding: list[float] | None
    embedding_model: str | None
    image_url: str | None
