import type { Collection, Db } from "mongodb";

export type DocumentStatus = "QUEUED" | "PROCESSING" | "INDEXED" | "FAILED";

export interface DocumentSchema {
  docId: string;
  filename: string;
  mimeType: string;
  size: number;
  path: string; // temp file path or S3 key
  status: DocumentStatus;
	error?: string;
  jobId: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export const getDocumentCollection = (db: Db): Collection<DocumentSchema> =>
  db.collection<DocumentSchema>("documents");
