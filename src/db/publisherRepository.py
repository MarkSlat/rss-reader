import sqlite3

from src.models.publisher import Publisher


class PublisherRepository:
    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path
        self._create_table()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_table(self):
        conn = self._connect()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                rss_url TEXT NOT NULL,
                favicon_url TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get(self, publisher_id: int) -> Publisher | None:
        conn = self._connect()

        row = conn.execute(
            """
            SELECT
                id,
                name,
                rss_url,
                favicon_url
            FROM publishers
            WHERE id = ?
            """,
            (publisher_id,),
        ).fetchone()

        conn.close()

        if row is None:
            return None

        return Publisher(
            id=row[0],
            name=row[1],
            rss_url=row[2],
            favicon_url=row[3],
        )

    def get_by_name(self, name: str) -> Publisher | None:
        conn = self._connect()

        row = conn.execute(
            """
            SELECT
                id,
                name,
                rss_url,
                favicon_url
            FROM publishers
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        conn.close()

        if row is None:
            return None

        return Publisher(
            id=row[0],
            name=row[1],
            rss_url=row[2],
            favicon_url=row[3],
        )

    def get_all(self) -> list[Publisher]:
        conn = self._connect()

        rows = conn.execute(
            """
            SELECT
                id,
                name,
                rss_url,
                favicon_url
            FROM publishers
            ORDER BY name
            """
        ).fetchall()

        conn.close()

        return [
            Publisher(
                id=row[0],
                name=row[1],
                rss_url=row[2],
                favicon_url=row[3],
            )
            for row in rows
        ]

    def save(self, publisher: Publisher) -> Publisher:
        """
        Inserts a new publisher if publisher.id is None.
        Otherwise updates the existing publisher.
        Returns the publisher with its id populated.
        """
        conn = self._connect()

        if publisher.id is None:
            cursor = conn.execute(
                """
                INSERT INTO publishers (
                    name,
                    rss_url,
                    favicon_url
                )
                VALUES (?, ?, ?)
                """,
                (
                    publisher.name,
                    publisher.rss_url,
                    publisher.favicon_url,
                ),
            )

            publisher.id = cursor.lastrowid

        else:
            conn.execute(
                """
                UPDATE publishers
                SET
                    name = ?,
                    rss_url = ?,
                    favicon_url = ?
                WHERE id = ?
                """,
                (
                    publisher.name,
                    publisher.rss_url,
                    publisher.favicon_url,
                    publisher.id,
                ),
            )

        conn.commit()
        conn.close()

        return publisher

    def delete(self, publisher_id: int):
        conn = self._connect()

        conn.execute(
            """
            DELETE FROM publishers
            WHERE id = ?
            """,
            (publisher_id,),
        )

        conn.commit()
        conn.close()

    def exists(self, publisher_id: int) -> bool:
        conn = self._connect()

        row = conn.execute(
            """
            SELECT 1
            FROM publishers
            WHERE id = ?
            LIMIT 1
            """,
            (publisher_id,),
        ).fetchone()

        conn.close()

        return row is not None

    def exists_by_name(self, name: str) -> bool:
        conn = self._connect()

        row = conn.execute(
            """
            SELECT 1
            FROM publishers
            WHERE name = ?
            LIMIT 1
            """,
            (name,),
        ).fetchone()

        conn.close()

        return row is not None

    def update(self, publisher: Publisher):
        if publisher.id is None:
            raise ValueError("Publisher must have an id before updating.")

        conn = self._connect()

        conn.execute(
            """
            UPDATE publishers
            SET
                name = ?,
                rss_url = ?,
                favicon_url = ?
            WHERE id = ?
            """,
            (
                publisher.name,
                publisher.rss_url,
                publisher.favicon_url,
                publisher.id,
            ),
        )

        conn.commit()
        conn.close()