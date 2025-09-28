import env from "@/config/env";
import { ChatOpenAI } from "@langchain/openai";

const newOpenAIChatModel = ({
	modelName = "openai/gpt-5",
}: {
	modelName?: string;
}) => {
	return new ChatOpenAI({
		modelName,
		openAIApiKey: env.OPENROUTER_API_KEY,
		configuration: {
			baseURL: "https://openrouter.ai/api/v1",
		},
	});
};

export { newOpenAIChatModel };
