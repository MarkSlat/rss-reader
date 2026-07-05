from os import path
import os
from sentence_transformers import SentenceTransformer

from src.RssParser import get_parsed_article_for_embedding
from src.models import article

import requests

MODELS_DIR = "model_cache"

os.makedirs(MODELS_DIR, exist_ok=True)

def set_embedding(article: article, model: str = "all-mpnet-base-v2") -> article:
    text = get_parsed_article_for_embedding(article)

    transformerModel = SentenceTransformer(model, cache_folder=MODELS_DIR)

    embedding_data = transformerModel.encode(text, convert_to_tensor=True)
    article.embedding = embedding_data.tolist()
    article.embedding_model = model
    return article

def set_embeddings(articles: list[article], model: str = "all-mpnet-base-v2") -> list[article]:
    transformerModel = SentenceTransformer(model, cache_folder=MODELS_DIR)

    for article in articles:
        text = get_parsed_article_for_embedding(article)
        embedding_data = transformerModel.encode(text, convert_to_tensor=True)
        article.embedding = embedding_data.tolist()
        article.embedding_model = model

    return articles