from datetime import timezone
from src.RssParser import get_articles_from_publishers
from flask import Flask, render_template, jsonify
import threading

from src.models.publisher import Publisher
from src.publisherParser import set_favicon_from_url
from src.models.feedDB import get_feeds
from src.db.articleRepository import ArticleRepository
from src.clustering import cluster_articles
from src.embeddings import set_embedding

app = Flask(__name__)

repo = ArticleRepository("news.db")

# Prevent simultaneous refresh calls
refresh_lock = threading.Lock()

@app.route("/refresh")
def refresh():
    with refresh_lock:

        feeds = get_feeds()

        publishers = [
            Publisher(
                name=feed,
                rss_url=feed,
                favicon_url=set_favicon_from_url(feed),
            )
            for feed in feeds
        ]

        articles = get_articles_from_publishers(publishers)

        cached = repo.bulk_get([a.url for a in articles])

        new_count = 0
        reused_count = 0

        final_articles = []

        for article in articles:
            existing = cached.get(article.url)

            if existing and existing.embedding:
                article.embedding = existing.embedding
                article.embedding_model = existing.embedding_model
                reused_count += 1
            else:
                set_embedding(article)
                repo.save(article)
                new_count += 1

            final_articles.append(article)

        return jsonify({
            "total": len(final_articles),
            "new_embeddings": new_count,
            "cached_embeddings": reused_count,
        })

@app.route("/")
def index():
    conn = repo._connect()

    rows = conn.execute("SELECT url FROM articles").fetchall()
    conn.close()

    urls = [r[0] for r in rows]

    cached = repo.bulk_get(urls)

    articles = [
        a for a in cached.values()
        if a.embedding is not None
    ]

    clusters = cluster_articles(articles)

    clusters.sort(
        key=lambda c: c.median_date.astimezone(timezone.utc).replace(tzinfo=None),
        reverse=True,
    )

    return render_template("index.jinja2", clusters=clusters)

if __name__ == "__main__":
    app.run(debug=True)