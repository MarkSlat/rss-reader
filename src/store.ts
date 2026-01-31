// src/store.ts
import type { Article } from "./rss";

let articles: Article[] = [];

export function setArticles(newArticles: Article[]) {
  articles = newArticles;
}

export function getArticles() {
  return articles;
}
