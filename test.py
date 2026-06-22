from src.clustering import cluster_articles
from src.embeddings import set_embedding
from src.publisherParser import set_favicon_from_url
from src.rssParser import get_articles_from_publishers
from src.models.feedDB import get_feeds
from src.models.publisher import Publisher


feeds = get_feeds()
    
publishers = []

for feed in feeds:
    publisher = Publisher(name=feed, rss_url=feed, favicon_url=set_favicon_from_url(feed))
    publishers.append(publisher)
    
articles = get_articles_from_publishers(publishers)

ordered_articles = sorted(articles, key=lambda x: x.published_date, reverse=True)

embedded_articles = []

for article in ordered_articles[:75]:
    embedded_articles.append(set_embedding(article))
    # print(f"Title: {article.title}, Embedding Model: {article.embedding}, Embedding Length: {len(article.embedding) if article.embedding else 0}")
    

clustered_articles = cluster_articles(embedded_articles)

print("Clustered Articles:")
for i, cluster in enumerate(clustered_articles):
    print(f"\nCluster {i + 1}:")
    for article in cluster:
        print(f"Title: {article.title}, Description: {article.description[:50]}, Publisher: {article.publisher.name}")