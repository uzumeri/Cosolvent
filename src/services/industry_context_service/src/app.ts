import { Hono } from "hono";
import { connectToDB } from "./lib/db";
import connectToRedis from "./lib/redis";
import indexRoutes from "./routes";
import adminRoutes from "./routes/admin";
import queryRoutes from "./routes/query";
import { newPineconeStore } from "./factory/vectorStores";
import { newOpenAIEmbedding } from "./factory/embeddings";
import env from "./config/env";

const main = async () => {
  const app = new Hono();
  const db = await connectToDB();
  const redis = await connectToRedis();
  const embedding = newOpenAIEmbedding({});
  const pinecone = await newPineconeStore(embedding, env.PINECONE_INDEX_NAME);

  app.route("/", indexRoutes);
  app.route("/admin", adminRoutes(db, redis, pinecone));
  app.route("/query", queryRoutes(db, redis));

  return app;
};

export default await main();
