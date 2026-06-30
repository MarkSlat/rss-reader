from datetime import timezone
from src.clustering import cluster_articles
from src.embeddings import set_embedding
from src.publisherParser import set_favicon_from_url
from src.RssParser import get_articles_from_publishers
from src.models.feedDB import get_feeds
from src.models.publisher import Publisher


from flask import Flask, render_template_string, render_template

app = Flask(__name__)

@app.route("/")
def index():
    feeds = get_feeds()
    
    publishers = []
    
    for feed in feeds:
        publisher = Publisher(name=feed, rss_url=feed, favicon_url=set_favicon_from_url(feed))
        publishers.append(publisher)
        
    articles = get_articles_from_publishers(publishers)
    

    embedded_articles = []

    for article in articles:
        embedded_articles.append(set_embedding(article))
        # print(f"Title: {article.title}, Embedding Model: {article.embedding}, Embedding Length: {len(article.embedding) if article.embedding else 0}")
    

    clusters = cluster_articles(embedded_articles)

    clusters.sort(
        key=lambda c: c.median_date.astimezone(timezone.utc).replace(tzinfo=None),
        reverse=True,
    )

    return render_template("index.jinja2", clusters=clusters)


if __name__ == "__main__":
    app.run(debug=True)

