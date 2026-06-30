import sqlite3
import numpy as np
from datetime import datetime

from src.models.article import Article
from src.models.publisher import Publisher


class ArticleRepository:
    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path
        self._create_table()

    def _connect(self):
        # IMPORTANT: new connection per call = thread safe
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self):
        conn = self._connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                published_date TEXT,
                publisher TEXT,
                image_url TEXT,
                embedding_model TEXT,
                embedding BLOB
            )
        """)
        conn.commit()
        conn.close()

    def get(self, url: str) -> Article | None:
        conn = self._connect()

        row = conn.execute(
            "SELECT * FROM articles WHERE url = ?",
            (url,),
        ).fetchone()

        conn.close()

        if not row:
            return None

        (
            url,
            title,
            description,
            published_date,
            publisher_name,
            image_url,
            embedding_model,
            embedding_blob,
        ) = row

        embedding = (
            np.frombuffer(embedding_blob, dtype=np.float32).tolist()
            if embedding_blob else None
        )

        return Article(
            url=url,
            title=title,
            description=description,
            published_date=datetime.fromisoformat(published_date),
            publisher=Publisher(
                name=publisher_name,
                rss_url="",
                favicon_url=None,
            ),
            embedding=embedding,
            embedding_model=embedding_model,
            image_url=image_url,
        )

    def bulk_get(self, urls: list[str]) -> dict[str, Article]:
        if not urls:
            return {}

        conn = self._connect()

        placeholders = ",".join("?" for _ in urls)

        rows = conn.execute(
            f"SELECT * FROM articles WHERE url IN ({placeholders})",
            urls,
        ).fetchall()

        conn.close()

        result = {}

        for row in rows:
            (
                url,
                title,
                description,
                published_date,
                publisher_name,
                image_url,
                embedding_model,
                embedding_blob,
            ) = row

            embedding = (
                np.frombuffer(embedding_blob, dtype=np.float32).tolist()
                if embedding_blob else None
            )

            result[url] = Article(
                url=url,
                title=title,
                description=description,
                published_date=datetime.fromisoformat(published_date),
                publisher=Publisher(
                    name=publisher_name,
                    rss_url="",
                    favicon_url=None,
                ),
                embedding=embedding,
                embedding_model=embedding_model,
                image_url=image_url,
            )

        return result

    def save(self, article: Article):
        conn = self._connect()

        embedding_blob = (
            np.array(article.embedding, dtype=np.float32).tobytes()
            if article.embedding else None
        )

        conn.execute("""
            INSERT OR REPLACE INTO articles (
                url, title, description, published_date,
                publisher, image_url, embedding_model, embedding
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.url,
            article.title,
            article.description,
            article.published_date.isoformat(),
            article.publisher.name,
            article.image_url,
            article.embedding_model,
            embedding_blob,
        ))

        conn.commit()
        conn.close()