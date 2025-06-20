import { Worker, type Job } from "bullmq";
import fs from "node:fs/promises";
import type { Db } from "mongodb";
import type { Redis } from "ioredis";
import { getDocumentCollection } from "@/models/document";
import { parseDocument } from "@/utils/parseDocument";
import { chunkText } from "@/utils/chunkText";
import type { OpenAIEmbeddings } from "@langchain/openai";
import type { Index, RecordMetadata } from "@pinecone-database/pinecone";

export const DOCUMENT_PROCESSING_WORKER_NAME = "process-document";

interface ProcessDocumentJobData {
  docId: string;
  filePath: string;
  originalName: string;
  mimeType: string;
  uploadedAt: Date;
}

export function createDocumentWorker(
  db: Db,
  redis: Redis,
  pinecone: Index<RecordMetadata>,
  embeddingModel: OpenAIEmbeddings,
) {
  const documentsCollection = getDocumentCollection(db);
  console.log("Creating document worker");

  const worker = new Worker<ProcessDocumentJobData>(
    DOCUMENT_PROCESSING_WORKER_NAME,
    async (job: Job<ProcessDocumentJobData>) => {
      try {
        // 1. Update status to PROCESSING
        await documentsCollection.updateOne(
          { docId: job.data.docId },
          { $set: { status: "PROCESSING", updatedAt: new Date() } },
        );
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

        // 6. Upsert embeddings to Pinecone
        console.log("upserting embeddings to Pinecone");
        const vectors = embeddings.map((embedding, idx) => ({
          id: `${job.data.docId}_chunk_${idx}`,
          metadata: {
            docId: job.data.docId,
            chunkIndex: idx,
            originalName: job.data.originalName,
          },
          values: embedding,
        }));

        await pinecone.upsert(vectors);

        // 7. Update MongoDB status to INDEXED
        await documentsCollection.updateOne(
          { docId: job.data.docId },
          { $set: { status: "INDEXED", updatedAt: new Date() } },
        );

        // 8. delete temp file
        await fs.unlink(job.data.filePath);
      } catch (error) {
        console.error(`Failed to process document ${job.data.docId}`, error);

        // Update status to FAILED and record error message
        await documentsCollection.updateOne(
          { docId: job.data.docId },
          {
            $set: {
              status: "FAILED",
              updatedAt: new Date(),
              error: (error as Error).message,
            },
          },
        );

        // Let BullMQ know the job failed
        throw error;
      }
    },
    { connection: redis },
  );

  return worker;
}
