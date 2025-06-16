import { tool } from "@langchain/core/tools";
import type { PineconeStore } from "@langchain/pinecone";
import { z } from "zod";

const retrieveSchema = z.object({ query: z.string() });

type supportedStores = PineconeStore;

const createRetrieveTool = (store: supportedStores) => {
	return tool(
		async ({ query }: { query: string }) => {
			const retrievedDocs = await store.similaritySearch(query, 3);
			const serialized = retrievedDocs
				.map(
					(doc) =>
						`Source: ${doc.metadata.source}\nContent: ${doc.pageContent}`,
				)
				.join("\n");
			return serialized;
		},
		{
			name: "retrieve",
			description: "Retrieve information related to a query.",
			schema: retrieveSchema,
		},
	);
};

export default createRetrieveTool;
