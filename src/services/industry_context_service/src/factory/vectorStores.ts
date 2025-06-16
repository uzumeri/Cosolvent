import { PineconeStore } from "@langchain/pinecone";
import { Pinecone as PineconeClient } from "@pinecone-database/pinecone";
import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import env from "@/config/env";

const pinecone = new PineconeClient();
const pineconeIndex = pinecone.Index(env.PINECONE_API_KEY);

const pineconeStore = async (
	namespace: string,
	embeddings: EmbeddingsInterface,
) => {
	return await PineconeStore.fromExistingIndex(embeddings, {
		pineconeIndex,
		namespace,
	});
};

export { pineconeStore };
