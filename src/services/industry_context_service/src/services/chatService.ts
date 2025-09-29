import type Redis from "ioredis";
import { v4 as uuidv4 } from "uuid";
import newChatAgent from "./chatAgent";
import { PromptService } from "./promptService";

type ChatService = {
	threadId: string | null;
	question: string;
};

const chatService = async (
	redis: Redis,
	{ threadId, question }: ChatService,
) => {
	threadId = threadId ?? uuidv4();

	const config = { configurable: { thread_id: threadId } };
	const input = [
		{
			role: "user",
			content: question,
		},
	];

	const promptService = new PromptService(redis);
	const systemPrompt = await promptService.getPrompt();

	const chatAget = await newChatAgent({ systemPrompt });
	const output = await chatAget.invoke({ messages: input }, config);

	const aiResponse = output.messages[output.messages.length - 1].content;

	const reponse = {
		threadId,
		question,
		aiResponse,
	};

	return reponse;
};

export default chatService;
