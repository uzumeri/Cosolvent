import { DOCUMENT_PROCESSING_WORKER_NAME } from "@/workers/documentWorker";
import { Queue } from "bullmq";
import type { Redis } from "ioredis";

let queue: Queue;

export const newDocumentQueue = (redis: Redis) => {
  if (!queue) {
    queue = new Queue(DOCUMENT_PROCESSING_WORKER_NAME, { connection: redis });
  }
  return queue;
};
