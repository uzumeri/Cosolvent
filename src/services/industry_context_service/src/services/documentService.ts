import { writeFile } from "node:fs/promises";
import path from "node:path";
import { type DocumentSchema } from "@/models/document";
import { insertDocument, setJobId, deleteByDocId, findByDocId, listAll } from "@/repositories/documentRepo";
import type { Job } from "bullmq";
import type { Redis } from "ioredis";
import { v4 as uuidv4 } from "uuid";
import { newDocumentQueue } from "@/queues/documentQueue";
import { DOCUMENT_PROCESSING_WORKER_NAME } from "@/workers/documentWorker";
import type { PgVectorStore } from "@/stores/pgVectorStore";

interface UploadDocumentInput {
  file: {
    name: string;
    type: string;
    data: Uint8Array;
  };
}

export class DocumentService {
  constructor(private redis: Redis, private store: PgVectorStore) {}

  // Postgres-backed repo used instead of a collection

  private documentsQue() {
    return newDocumentQueue(this.redis);
  }

  async uploadDocument({ file }: UploadDocumentInput) {
    const docId = uuidv4();
    const fileExt = path.extname(file.name);
    const tempPath = path.join("/app/tmp", `${docId}${fileExt}`);
    const now = new Date();

    // 1. Write file to shared disk with the worker
    await writeFile(tempPath, file.data);

    // 2. Insert document metadata
    const metadata: DocumentSchema = {
      docId,
      filename: file.name,
      mimeType: file.type,
      size: file.data.byteLength,
      path: tempPath,
      status: "QUEUED",
      jobId: null,
      createdAt: now,
      updatedAt: now,
    };

  await insertDocument(metadata);

    // Enqueue job for background processing
    const job: Job = await this.documentsQue().add(
      DOCUMENT_PROCESSING_WORKER_NAME,
      {
        docId,
        filePath: tempPath,
        originalName: file.name,
        mimeType: file.type,
        uploadedAt: now,
      },
    );

    await setJobId(docId, String(job.id));

    return {
      message: "Document upload accepted for processing.",
      docId,
      jobId: job.id,
      status: "QUEUED",
    };
  }

  async deleteDocument(id: string) {
  const result = await findByDocId(id);
    if (!result) {
      throw new Error("Document not found");
    }

  await deleteByDocId(id);
  }

  async getAllDocuments() {
    return await listAll();
  }
}
