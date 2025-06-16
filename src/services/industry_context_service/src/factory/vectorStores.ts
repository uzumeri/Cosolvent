import env from "@/config/env";
import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { PineconeStore } from "@langchain/pinecone";
import { Pinecone as PineconeClient } from "@pinecone-database/pinecone";

const newPineconeStore = async (
	embeddings: EmbeddingsInterface,
	indexName: string,
	namespace?: string | undefined,
) => {
	const pinecone = new PineconeClient({
		apiKey: env.PINECONE_API_KEY,
	});
	const pineconeIndex = pinecone.Index(indexName);
	return await PineconeStore.fromExistingIndex(embeddings, {
		pineconeIndex,
		namespace,
	});
};

export { newPineconeStore };
