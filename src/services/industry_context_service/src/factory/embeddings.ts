import { OpenAIEmbeddings } from "@langchain/openai";

const newOpenAIEmbedding = ({
	modelName = "text-embedding-3-small",
}: {
	modelName?: string;
}) => {
	return new OpenAIEmbeddings({
		modelName,
		openAIApiKey: process.env.OPENAI_API_KEY,
	});
};

export { newOpenAIEmbedding };
