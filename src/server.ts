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

        if (url.pathname === "/api/refresh" && req.method === "POST") {
            const articles = await fetchAllFeeds();
            setArticles(articles);

            return new Response(
                JSON.stringify({ success: true }),
                { headers: { "Content-Type": "application/json" } }
            );
        }

        if (url.pathname === "/style.css") {
            return new Response(
                await Bun.file("public/style.css").text(),
                { headers: { "Content-Type": "text/css" } }
            );
        }

        return new Response("Not Found", { status: 404 });
    },
});

console.log(`Server running at http://localhost:${server.port}`);

// Fetch feeds on startup
const articles = await fetchAllFeeds();
setArticles(articles);
