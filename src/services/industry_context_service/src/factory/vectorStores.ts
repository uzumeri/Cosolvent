import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { newPgVectorStore } from "@/stores/pgVectorStore";

export const newVectorStore = async (
  embeddings: EmbeddingsInterface,
  indexName: string,
  namespace?: string,
) => newPgVectorStore(embeddings, indexName, namespace);

