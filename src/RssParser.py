from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List

import feedparser

from src.models.article import Article
from src.models.publisher import Publisher

def formated_date(date_str) -> datetime:
    try:
        # ISO 8601
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass

    try:
        # RFC 2822 / RSS / email dates
        return parsedate_to_datetime(date_str)
    except (TypeError, ValueError):
        raise ValueError(f"Unsupported date format: {date_str}")

def get_image_from_entry(entry):
    # RSS media:content
    for media in getattr(entry, "media_content", []):
        url = media.get("url")
        if url:
            return url

    # RSS media:thumbnail
    for media in getattr(entry, "media_thumbnail", []):
        url = media.get("url")
        if url:
            return url

    # Atom/RSS image enclosures
    for link in getattr(entry, "links", []):
        href = link.get("href")
        rel = link.get("rel", "")
        typ = link.get("type", "")

        if href and (
            typ.startswith("image/")
            or rel == "enclosure"
        ):
            return href

    # Some feeds expose image directly
    image = getattr(entry, "image", None)
    if isinstance(image, dict):
        return image.get("href") or image.get("url")

    return None

def get_description_from_entry(entry):
    description = getattr(entry, "description", None)
    if description:
        return description

    summary = getattr(entry, "summary", None)
    if summary:
        return summary

    content_list = getattr(entry, "content", [])
    if content_list and isinstance(content_list, list):
        for content in content_list:
            if isinstance(content, dict) and "value" in content:
                return content["value"]

    return None

def get_articles_from_publisher(publisher: Publisher):
    feed = feedparser.parse(publisher.rss_url)
    
    articles = []
    
    for entry in feed.entries:
        article = Article(
            title=entry.title,
            description=get_description_from_entry(entry),
            published_date=formated_date(entry.published),
            publisher=publisher,
            embedding=[],  # Placeholder for vector representation
            embedding_model=None,  # Placeholder for embedding model name
            image_url=get_image_from_entry(entry)
        )

        if article.description is None:
            continue  # Skip articles without a valid published date

        articles.append(article)

    return articles

def get_articles_from_publishers(publishers: List[Publisher]):
    all_articles = []
    
    for publisher in publishers:
        articles = get_articles_from_publisher(publisher)
        all_articles.extend(articles)
    
    return all_articles

def order_articles_by_date(articles: List[Article]):
    return sorted(articles, key=lambda x: x.published_date, reverse=True)


def get_parsed_article_for_embedding(article: Article):
    return f"Title: {article.title}. Description: {article.description}"