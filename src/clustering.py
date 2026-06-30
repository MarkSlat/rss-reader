from datetime import datetime
import numpy as np

from src.models.article import Article
from src.models.cluster import Cluster


def centroid(cluster: Cluster) -> np.ndarray:
    embeddings = [a.embedding for a in cluster.articles if a.embedding is not None]
    return np.mean(embeddings, axis=0)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def median_datetime(dates: list[datetime]) -> datetime:
    timestamps = sorted(dt.timestamp() for dt in dates)
    median_ts = float(np.median(timestamps))
    return datetime.fromtimestamp(median_ts)


def cluster_articles(
    articles: list[Article], threshold: float = 0.7
) -> list[Cluster]:
    clusters: list[Cluster] = []

    for article in articles:
        if article.embedding is None:
            continue

        placed = False

        for cluster in clusters:
            sim = cosine_similarity(article.embedding, centroid(cluster))

            if sim >= threshold:
                cluster.articles.append(article)
                cluster.median_date = median_datetime(
                    [a.published_date for a in cluster.articles]
                )
                placed = True
                break

        if not placed:
            clusters.append(
                Cluster(
                    articles=[article],
                    median_date=article.published_date,
                )
            )

    return clusters