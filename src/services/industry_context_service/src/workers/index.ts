import { createDocumentWorker } from "./documentWorker";
import env from "@/config/env";
import { newOpenAIEmbedding } from "@/factory/embeddings";
import Redis from "ioredis";
import { newVectorStore } from "@/factory/vectorStores";

async function main() {
  const redis = new Redis(env.REDIS_URL, { maxRetriesPerRequest: null }); // maxRetriesPerRequest: null is required by bullmq
  const embedding = newOpenAIEmbedding({
    modelName: "text-embedding-3-small",
  });
  const vectorStore = await newVectorStore(embedding, "embeddings");

  const worker = createDocumentWorker(redis, vectorStore, embedding);

  worker.on("error", (err: any) => {
    console.error("Worker error", err);
  });

  worker.on("failed", (job: any, err: any) => {
    console.error("Job failed", job, err);
  });

  worker.on("completed", (job: any, result: any) => {
    console.log("Job completed", job, result);
  });

  console.log("Document worker started");
}

await main().catch(console.error);
