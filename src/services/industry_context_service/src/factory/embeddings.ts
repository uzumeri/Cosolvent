import { OpenAIEmbeddings } from "@langchain/openai";
import env from "@/config/env";

const newOpenAIEmbedding = ({
	modelName = "openai/text-embedding-3-small",
}: {
	modelName?: string;
}) => {
	return new OpenAIEmbeddings({
		modelName,
		openAIApiKey: env.OPENROUTER_API_KEY,
		configuration: {
			baseURL: "https://openrouter.ai/api/v1",
		},
	});
};

export { newOpenAIEmbedding };
