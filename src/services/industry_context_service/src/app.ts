import { Hono } from "hono";
import connectToRedis from "./lib/redis";
import healthzRoutes from "./routes/healthz";
import adminRoutes from "./routes/admin";
import queryRoutes from "./routes/query";
import { newVectorStore } from "./factory/vectorStores";
import { newOpenAIEmbedding } from "./factory/embeddings";
import env from "./config/env";

import mcpRoutes from "./routes/mcp";

const main = async () => {
  const app = new Hono();
  const redis = await connectToRedis();
  const embedding = newOpenAIEmbedding({});
  const store = await newVectorStore(embedding, "participant_embeddings");

  app.route("/healthz", healthzRoutes);
  app.get("/health", (c) => c.json({ status: "ok" }));
  app.route("/admin", adminRoutes(redis, store));
  app.route("/query", queryRoutes(redis));
  app.route("/mcp", mcpRoutes(redis));

  return app;
};

export default await main();
