import numpy as np

def centroid(cluster):
    return np.mean([a.embedding for a in cluster], axis=0)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def cluster_articles(articles, threshold=0.7):
    clusters = []

    for article in articles:
        placed = False

        for cluster in clusters:
            sim = cosine_similarity(article.embedding, centroid(cluster))

            if sim >= threshold:
                cluster.append(article)
                placed = True
                break

        if not placed:
            clusters.append([article])

    return clusters