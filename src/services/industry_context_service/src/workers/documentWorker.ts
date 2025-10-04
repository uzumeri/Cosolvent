import { Worker, type Job } from "bullmq";
import fs from "node:fs/promises";
import type { Redis } from "ioredis";
import { updateStatus } from "@/repositories/documentRepo";
import { parseDocument } from "@/utils/parseDocument";
import { chunkText } from "@/utils/chunkText";
import type { OpenAIEmbeddings } from "@langchain/openai";
import type { PgVectorStore } from "@/stores/pgVectorStore";

export const DOCUMENT_PROCESSING_WORKER_NAME = "process-document";

interface ProcessDocumentJobData {
  docId: string;
  filePath: string;
  originalName: string;
  mimeType: string;
  uploadedAt: Date;
}

export function createDocumentWorker(redis: Redis, store: PgVectorStore, embeddingModel: OpenAIEmbeddings) {
  // Status updates are written to Postgres via repo
  console.log("Creating document worker");

  const worker = new Worker<ProcessDocumentJobData>(
    DOCUMENT_PROCESSING_WORKER_NAME,
    async (job: Job<ProcessDocumentJobData>) => {
      try {
        // 1. Update status to PROCESSING
        await updateStatus(job.data.docId, "PROCESSING");
        console.log("Processing document", job.data.docId);

        // 2. Read file
        const fileBuffer = await fs.readFile(job.data.filePath);

        // 3. Parse document text
        const text = await parseDocument(fileBuffer, job.data.mimeType);

        // 4. Chunk text
        const chunks = chunkText(text, 500, 50); // 500 tokens with 50 overlap

        // 5. Embed chunks in batches using embeddings
        const embeddings = [];
        for (let i = 0; i < chunks.length; i += 20) {
          const batch = chunks.slice(i, i + 20);
          const batchEmbeddings = await embeddingModel.embedDocuments(batch);
          embeddings.push(...batchEmbeddings);
        }

        // 6. Upsert embeddings to Postgres (pgvector)
        console.log("upserting embeddings to Postgres");
        const records = embeddings.map((embedding, idx) => ({
          id: `${job.data.docId}_chunk_${idx}`,
          metadata: {
            docId: job.data.docId,
            chunkIndex: idx,
            originalName: job.data.originalName,
          },
          embedding,
        }));

        await store.upsert(records);

  // 7. Update status to INDEXED in Postgres
        await updateStatus(job.data.docId, "INDEXED");

        // 8. delete temp file
        await fs.unlink(job.data.filePath);
      } catch (error) {
        console.error(`Failed to process document ${job.data.docId}`, error);

        // Update status to FAILED and record error message
        await updateStatus(job.data.docId, "FAILED", (error as Error).message);

        // Let BullMQ know the job failed
        throw error;
      }
    },
    { connection: redis },
  );

  return worker;
}
