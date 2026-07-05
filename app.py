from datetime import timezone
from src.RssParser import get_articles_from_publishers
from flask import Flask, render_template, jsonify, request, redirect

import threading

from src.models.publisher import Publisher
from src.publisherParser import set_favicon_from_url
from src.models.feedDB import get_feeds
from src.db.articleRepository import ArticleRepository
from src.db.publisherRepository import PublisherRepository
from src.clustering import cluster_articles
from src.embeddings import set_embedding, set_embeddings

app = Flask(__name__)

repo = ArticleRepository("news.db")
publisher_repo = PublisherRepository("news.db")

refresh_lock = threading.Lock()

@app.route("/refresh")
def refresh():
    with refresh_lock:

        publishers = publisher_repo.get_all()

        # fallback: if DB empty, seed from feeds once
        if not publishers:
            feeds = get_feeds()

            publishers = [
                Publisher(
                    name=feed,
                    rss_url=feed,
                    favicon_url=set_favicon_from_url(feed),
                )
                for feed in feeds
            ]

            for p in publishers:
                publisher_repo.save(p)

        articles = get_articles_from_publishers(publishers)

        cached = repo.bulk_get([a.url for a in articles])

        new_articles = []
        final_articles = []
        reused_count = 0

        for article in articles:
            existing = cached.get(article.url)

            if existing and existing.embedding:
                article.embedding = existing.embedding
                article.embedding_model = existing.embedding_model
                reused_count += 1
            else:
                new_articles.append(article)

            final_articles.append(article)

        # Generate embeddings in one batch
        if new_articles:
            set_embeddings(new_articles)

            for article in new_articles:
                repo.save(article)

        return jsonify(
            {
                "total": len(final_articles),
                "new_embeddings": len(new_articles),
                "cached_embeddings": reused_count,
            }
        )

@app.route("/")
def index():
    urls = repo.get_all_urls()
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

@app.route("/publishers", methods=["GET"])
def publishers_page():
    publishers = publisher_repo.get_all()
    return render_template("publishers.jinja2", publishers=publishers)

@app.route("/publishers/save", methods=["POST"])
def save_publisher():
    publisher_id = request.form.get("id")

    publisher = Publisher(
        id=int(publisher_id) if publisher_id else None,
        name=request.form["name"],
        rss_url=request.form["rss_url"],
        favicon_url=request.form.get("favicon_url") or None,
    )

    publisher_repo.save(publisher)

    return redirect("/publishers")

@app.route("/publishers/delete/<int:publisher_id>", methods=["POST"])
def delete_publisher(publisher_id):
    publisher_repo.delete(publisher_id)
    return redirect("/publishers")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)