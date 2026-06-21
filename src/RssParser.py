from datetime import datetime
from typing import List

import feedparser

from models.article import Article
from src.models.publisher import Publisher

def formated_date(date_str) -> datetime:
    # Convert the date string to a datetime object
    return datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")

def get_image_from_entry(entry):
    # Placeholder function for extracting image URL from feed entry
    return getattr(entry, 'image', None)

def get_articles_from_publisher(publisher: Publisher):
    feed = feedparser.parse(publisher.rss_url)
    
    articles = []
    
    for entry in feed.entries:
        article = Article(
            title=entry.title,
            description=entry.description,
            published_date=formated_date(entry.published),
            publisher=publisher,
            vector=[],  # Placeholder for vector representation
            image_url=get_image_from_entry(entry)
        )
        articles.append(article)

    return articles

def get_articles_from_publishers(publishers: List[Publisher]):
    all_articles = []
    
    for publisher in publishers:
        articles = get_articles_from_publisher(publisher)
        all_articles.extend(articles)
    
    return all_articles