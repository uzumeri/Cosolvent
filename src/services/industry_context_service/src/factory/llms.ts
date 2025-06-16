import env from "@/config/env";
import { ChatOpenAI } from "@langchain/openai";

const newOpenAIChatModel = ({
	modelName = "gpt-4",
}: {
	modelName?: string;
}) => {
	return new ChatOpenAI({
		modelName,
		openAIApiKey: env.OPENAI_API_KEY,
	});
};

export { newOpenAIChatModel };
