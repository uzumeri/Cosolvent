import {
  deleteDocument,
  getAllDocuments,
  uploadDocument,
} from "@/controllers/documentController";
import { DocumentService } from "@/services/documentService";
import type { PineconeStore } from "@langchain/pinecone";
import { Hono } from "hono";
import type Redis from "ioredis";
import type { Db } from "mongodb";

const documentRoutes = (db: Db, redis: Redis, pinecone: PineconeStore) => {
  const router = new Hono();

  const ds = new DocumentService(db, redis, pinecone);

  router.get("/", getAllDocuments(ds));
  router.post("/", uploadDocument(ds));
  router.delete("/:id", deleteDocument(ds));

  return router;
};

export default documentRoutes;
