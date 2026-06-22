from src.rssParser import get_parsed_article_for_embedding
from src.models import article

import requests

EMBEDDING_URL = "http://localhost:11434"

def set_embedding(article: article, model: str = "qwen3-embedding:0.6b") -> article:
    text = get_parsed_article_for_embedding(article)

    response = requests.post(
    f"{EMBEDDING_URL}/api/embeddings",
    json={
        "model": model,
        "prompt": text
    }
)
    response.raise_for_status()

    embedding_data = response.json()
    article.embedding = embedding_data["embedding"]
    article.embedding_model = model
    return article