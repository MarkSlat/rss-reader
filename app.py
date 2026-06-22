from src.publisherParser import set_favicon_from_url
from src.rssParser import get_articles_from_publishers
from src.models.feedDB import get_feeds
from src.models.publisher import Publisher


from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>News Feed</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 2rem auto;
            background: #f5f5f5;
        }

        .article {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,.1);
        }

        .header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }

        .favicon {
            width: 20px;
            height: 20px;
            object-fit: contain;
        }

        .publisher {
            color: #666;
            font-size: 0.9rem;
        }

        .date {
            color: #999;
            font-size: 0.85rem;
            margin-left: auto;
        }

        .content {
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }

        .thumbnail {
            width: 120px;
            height: 80px;
            object-fit: cover;
            border-radius: 6px;
            flex-shrink: 0;
        }

        .text {
            flex: 1;
        }

        h2 {
            margin: 0 0 8px 0;
            font-size: 1.2rem;
        }

        p {
            margin: 0;
            color: #444;
            line-height: 1.5;
        }
    </style>
</head>
<body>

<h1>News Feed</h1>

{% for article in articles %}
<div class="article">

    <div class="header">
        {% if article.publisher.favicon_url %}
            <img
                class="favicon"
                src="{{ article.publisher.favicon_url }}"
                alt="{{ article.publisher.name }}">
        {% endif %}

        <span class="publisher">
            {{ article.publisher.name or "Unknown Publisher" }}
        </span>

        <span class="date">
            {{ article.published_date.strftime("%Y-%m-%d %H:%M") }}
        </span>
    </div>

    <div class="content">

        {% if article.image_url %}
            <img
                class="thumbnail"
                src="{{ article.image_url }}"
                alt="{{ article.title }}">
        {% endif %}

        <div class="text">
            <h2>{{ article.title }}</h2>
            <p>{{ article.description }}</p>
        </div>

    </div>

</div>
{% endfor %}

</body>
</html>
"""


@app.route("/")
def index():
    feeds = get_feeds()
    
    publishers = []
    
    for feed in feeds:
        publisher = Publisher(name=feed, rss_url=feed, favicon_url=set_favicon_from_url(feed))
        publishers.append(publisher)
        
    articles = get_articles_from_publishers(publishers)
    
    ordered_articles = sorted(articles, key=lambda x: x.published_date, reverse=True)

    return render_template_string(HTML, articles=ordered_articles)


if __name__ == "__main__":
    app.run(debug=True)

