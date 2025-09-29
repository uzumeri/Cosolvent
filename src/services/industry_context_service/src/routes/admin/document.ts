import {
  deleteDocument,
  getAllDocuments,
  uploadDocument,
} from "@/controllers/documentController";
import { DocumentService } from "@/services/documentService";
import type { PgVectorStore } from "@/stores/pgVectorStore";
import { Hono } from "hono";
import type Redis from "ioredis";
const documentRoutes = (redis: Redis, store: PgVectorStore) => {
  const router = new Hono();

  const ds = new DocumentService(redis, store);

  router.get("/", getAllDocuments(ds));
  router.post("/", uploadDocument(ds));
  router.delete("/:id", deleteDocument(ds));

  return router;
};

export default documentRoutes;
