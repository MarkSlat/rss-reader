import sqlite3
from datetime import datetime

import numpy as np

from src.models.article import Article
from src.models.publisher import Publisher


class ArticleRepository:
    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_tables(self):
        conn = self._connect()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                rss_url TEXT NOT NULL,
                favicon_url TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                published_date TEXT,
                publisher_id INTEGER NOT NULL,
                image_url TEXT,
                embedding_model TEXT,
                embedding BLOB,
                FOREIGN KEY (publisher_id) REFERENCES publishers(id)
            )
        """)

        conn.commit()
        conn.close()

    def _get_or_create_publisher(self, conn, publisher: Publisher) -> int:
        """
        Returns publisher id, creating/updating publisher if needed.
        """

        # 1. If publisher already has ID → update and return it
        if publisher.id is not None:
            conn.execute(
                """
                UPDATE publishers
                SET name = ?, rss_url = ?, favicon_url = ?
                WHERE id = ?
                """,
                (
                    publisher.name,
                    publisher.rss_url,
                    publisher.favicon_url,
                    publisher.id,
                ),
            )
            return publisher.id

        # 2. Try find by name
        row = conn.execute(
            "SELECT id FROM publishers WHERE name = ?",
            (publisher.name,),
        ).fetchone()

        if row:
            publisher.id = row[0]

            conn.execute(
                """
                UPDATE publishers
                SET rss_url = ?, favicon_url = ?
                WHERE id = ?
                """,
                (
                    publisher.rss_url,
                    publisher.favicon_url,
                    publisher.id,
                ),
            )

            return publisher.id

        # 3. Insert new publisher
        cursor = conn.execute(
            """
            INSERT INTO publishers (name, rss_url, favicon_url)
            VALUES (?, ?, ?)
            """,
            (
                publisher.name,
                publisher.rss_url,
                publisher.favicon_url,
            ),
        )

        publisher.id = cursor.lastrowid
        return publisher.id
    
    def save(self, article: Article):
        conn = self._connect()

        publisher_id = self._get_or_create_publisher(conn, article.publisher)

        embedding_blob = (
            np.array(article.embedding, dtype=np.float32).tobytes()
            if article.embedding is not None
            else None
        )

        conn.execute(
            """
            INSERT OR REPLACE INTO articles (
                url,
                title,
                description,
                published_date,
                publisher_id,
                image_url,
                embedding_model,
                embedding
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article.url,
                article.title,
                article.description,
                article.published_date.isoformat(),
                publisher_id,
                article.image_url,
                article.embedding_model,
                embedding_blob,
            ),
        )

        conn.commit()
        conn.close()

    def get(self, url: str) -> Article | None:
        conn = self._connect()

        row = conn.execute(
            """
            SELECT
                a.url,
                a.title,
                a.description,
                a.published_date,
                a.image_url,
                a.embedding_model,
                a.embedding,

                p.id,
                p.name,
                p.rss_url,
                p.favicon_url

            FROM articles a
            JOIN publishers p ON a.publisher_id = p.id
            WHERE a.url = ?
            """,
            (url,),
        ).fetchone()

        conn.close()

        if row is None:
            return None

        (
            url,
            title,
            description,
            published_date,
            image_url,
            embedding_model,
            embedding_blob,
            publisher_id,
            publisher_name,
            publisher_rss_url,
            publisher_favicon_url,
        ) = row

        embedding = (
            np.frombuffer(embedding_blob, dtype=np.float32).tolist()
            if embedding_blob
            else None
        )

        return Article(
            url=url,
            title=title,
            description=description,
            published_date=datetime.fromisoformat(published_date),
            publisher=Publisher(
                id=publisher_id,
                name=publisher_name,
                rss_url=publisher_rss_url,
                favicon_url=publisher_favicon_url,
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
            f"""
            SELECT
                a.url,
                a.title,
                a.description,
                a.published_date,
                a.image_url,
                a.embedding_model,
                a.embedding,

                p.id,
                p.name,
                p.rss_url,
                p.favicon_url

            FROM articles a
            JOIN publishers p ON a.publisher_id = p.id
            WHERE a.url IN ({placeholders})
            """,
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
                image_url,
                embedding_model,
                embedding_blob,
                publisher_id,
                publisher_name,
                publisher_rss_url,
                publisher_favicon_url,
            ) = row

            embedding = (
                np.frombuffer(embedding_blob, dtype=np.float32).tolist()
                if embedding_blob
                else None
            )

            result[url] = Article(
                url=url,
                title=title,
                description=description,
                published_date=datetime.fromisoformat(published_date),
                publisher=Publisher(
                    id=publisher_id,
                    name=publisher_name,
                    rss_url=publisher_rss_url,
                    favicon_url=publisher_favicon_url,
                ),
                embedding=embedding,
                embedding_model=embedding_model,
                image_url=image_url,
            )

        return result

    def delete(self, url: str):
        conn = self._connect()

        conn.execute(
            "DELETE FROM articles WHERE url = ?",
            (url,),
        )

        conn.commit()
        conn.close()

    def get_all_urls(self) -> list[str]:
        conn = self._connect()

        rows = conn.execute(
            "SELECT url FROM articles"
        ).fetchall()

        conn.close()

        return [r[0] for r in rows]