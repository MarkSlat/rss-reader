// src/server.ts
import { fetchAllFeeds } from "./rss";
import { setArticles, getArticles } from "./store";

const server = Bun.serve({
  port: 3000,

  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/api/articles") {
      return new Response(JSON.stringify(getArticles()), {
        headers: { "Content-Type": "application/json" },
      });
    }

    if (url.pathname === "/") {
      return new Response(
        await Bun.file("public/index.html").text(),
        { headers: { "Content-Type": "text/html" } }
      );
    }

    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Server running at http://localhost:${server.port}`);

// Fetch feeds on startup
const articles = await fetchAllFeeds();
setArticles(articles);
