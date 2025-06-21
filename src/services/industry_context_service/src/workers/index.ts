import { connectToDB } from "@/lib/db";
import { createDocumentWorker } from "./documentWorker";
import env from "@/config/env";
import { newOpenAIEmbedding } from "@/factory/embeddings";
import Redis from "ioredis";
import { Pinecone } from "@pinecone-database/pinecone";

async function main() {
  const db = await connectToDB();
  const redis = new Redis(env.REDIS_URL, { maxRetriesPerRequest: null }); // maxRetriesPerRequest: null is required by bullmq
  const embedding = newOpenAIEmbedding({
    modelName: "text-embedding-3-small",
  });
  const pc = new Pinecone({ apiKey: env.PINECONE_API_KEY });
  const pcIndex = pc.Index(env.PINECONE_INDEX_NAME);

  const worker = createDocumentWorker(db, redis, pcIndex, embedding);

  worker.on("error", (err) => {
    console.error("Worker error", err);
  });

  worker.on("failed", (job, err) => {
    console.error("Job failed", job, err);
  });

  worker.on("completed", (job, result) => {
    console.log("Job completed", job, result);
  });

  console.log("Document worker started");
}

await main().catch(console.error);
