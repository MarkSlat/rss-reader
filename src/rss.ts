// src/rss.ts
import Parser from "rss-parser";
import { FEEDS } from "./feeds";

const parser = new Parser();

export type Article = {
  title: string;
  link: string;
  published: string;
  source: string;
  pubDate?: Date;
  creator?: string;
  content?: string;
  categories?: string[];
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
          pubDate: item.pubDate ? new Date(item.pubDate) : undefined,
          creator: item.creator ?? undefined,
          content: item.content ?? undefined,
          categories: item.categories ?? undefined,
        });
      }
    } catch (err) {
      console.error(`Failed to fetch ${feed.name}`, err);
    }
  }

  articles.sort((a, b) => {
    const dateA = a.pubDate ? a.pubDate.getTime() : 0;
    const dateB = b.pubDate ? b.pubDate.getTime() : 0;
    return dateB - dateA;
  });

  return articles;
}
