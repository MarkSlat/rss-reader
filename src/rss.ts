// src/rss.ts
import Parser from "rss-parser";
import { FEEDS } from "./feeds";

const parser = new Parser();

export type Article = {
  title: string;
  link: string;
  published: string;
  source: string;
};

export async function fetchAllFeeds(): Promise<Article[]> {
  const articles: Article[] = [];

  for (const feed of FEEDS) {
    try {
      const parsed = await parser.parseURL(feed.url);

      for (const item of parsed.items) {
        articles.push({
          title: item.title ?? "No title",
          link: item.link ?? "",
          published: item.pubDate ?? "",
          source: feed.name,
        });
      }
    } catch (err) {
      console.error(`Failed to fetch ${feed.name}`, err);
    }
  }

  return articles;
}
