import { v4 as uuidv4 } from "uuid";
import chatApp from "./chatAgent";

type ChatService = {
	threadId: string | null;
	question: string;
};

const chatService = async ({ threadId, question }: ChatService) => {
	if (!threadId) {
		threadId = uuidv4();
	}

	const config = { configurable: { thread_id: threadId } };
	const input = [
		{
			role: "user",
			content: question,
		},
	];

	const output = await chatApp.invoke({ messages: input }, config);
	const aiResponse = output.messages[output.messages.length - 1].content;
	const reponse = {
		threadId,
		question,
		aiResponse,
	};

	return reponse;
};

export default chatService;
