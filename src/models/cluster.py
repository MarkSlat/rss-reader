from dataclasses import dataclass
from datetime import datetime
from src.models.article import Article


@dataclass
class Cluster:
    articles: list[Article]
    median_date: datetime