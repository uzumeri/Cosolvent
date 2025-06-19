import { writeFile } from "node:fs/promises";
import path from "node:path";
import { type DocumentSchema, getDocumentCollection } from "@/models/document";
import type { Job } from "bullmq";
import type { Redis } from "ioredis";
import type { Db } from "mongodb";
import { ObjectId } from "mongodb";
import { v4 as uuidv4 } from "uuid";
import { newDocumentQueue } from "@/queues/documentQueue";
import { DOCUMENT_PROCESSING_WORKER_NAME } from "@/workers/documentWorker";
import type { PineconeStore } from "@langchain/pinecone";

interface UploadDocumentInput {
  file: {
    name: string;
    type: string;
    data: Uint8Array;
  };
}

export class DocumentService {
  constructor(
    private db: Db,
    private redis: Redis,
    private pinecone: PineconeStore,
  ) {}

  private documentsCollection() {
    return getDocumentCollection(this.db);
  }

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

    await this.documentsCollection().insertOne(metadata);

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

    await this.documentsCollection().updateOne(
      { docId },
      { $set: { jobId: job.id, updatedAt: new Date() } },
    );

    return {
      message: "Document upload accepted for processing.",
      docId,
      jobId: job.id,
      status: "QUEUED",
    };
  }

  async deleteDocument(id: string) {
    const result = await this.documentsCollection().findOne({
      _id: new ObjectId(id),
    });
    if (!result) {
      throw new Error("Document not found");
    }

    await this.documentsCollection().deleteOne({ _id: new ObjectId(id) });

    await this.pinecone.delete({ filter: { docId: result.docId } });
  }

  async getAllDocuments() {
    const docs = await this.documentsCollection()
      .find()
      .sort({ createdAt: -1 })
      .toArray();

    return docs;
  }
}
